from contextlib import asynccontextmanager
from datetime import datetime, timezone
import json
import os
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from langsmith import Client, traceable

from .constants import EXPERT_BENCHMARK
from .evaluator import grade_with_llm, history_tool, memory_of, target_difficulty
from .langsmith_eval import (
    run_grader_evaluation,
    run_langsmith_evaluation,
    run_model_comparison,
    run_rag_evaluation,
)
from .models import ROOT, Interview, Learner, Question, Response, SessionLocal, initialize_database
from .schemas import AnswerRequest, FeedbackRequest, StartRequest
from .workflow import graph, report, state_of, transition_graph

load_dotenv(ROOT / "app" / ".env")
load_dotenv(ROOT / ".env")


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    yield


app = FastAPI(title="Data Science Interview Prep Bot", lifespan=lifespan)


@app.get("/")
def home() -> FileResponse:
    return FileResponse(ROOT / "static" / "index.html")


@app.post("/api/interviews")
def start_interview(payload: StartRequest) -> dict[str, Any]:
    track = payload.track.lower().strip()
    if track not in {"ml", "analytics"}:
        raise HTTPException(400, "track must be 'ml' or 'analytics'")
    with SessionLocal() as db:
        learner = db.get(Learner, payload.learner_id) or Learner(id=payload.learner_id)
        db.add(learner)
        interview = Interview(learner_id=payload.learner_id, track=track, level=payload.level.lower(), current_difficulty=target_difficulty(payload.level), state_json=json.dumps({"stage_counts": {}, "used_question_ids": []}))
        db.add(interview); db.commit(); db.refresh(interview)
        return {"interview_id": interview.id, **graph.next_question(db, interview, learner), "history_context": history_tool.lookup(db, learner)}


@traceable(name="submit_candidate_answer", run_type="chain", tags=["candidate_assessment"])
def _execute_answer_evaluation(
    db: Any,
    interview: Interview,
    learner: Learner,
    cleaned_answer: str,
) -> dict[str, Any]:
    state = state_of(interview)
    if interview.stage == "warmup":
        db.add(Response(interview_id=interview.id, question_id=None, stage="warmup", topic="goals", answer=cleaned_answer, score=100, feedback="Warmup completed. Context recorded for interview personalization."))
        self_intro = cleaned_answer[:180]
        state["warmup_context"] = self_intro; interview.stage = "technical"; interview.state_json = json.dumps(state); db.commit()
        return {"evaluation": {"score": 100, "is_warmup": True, "feedback": "Thank you for the introduction. Let's move into your first technical evaluation round.", "missing": [], "covered": ["introduction"]}, **graph.next_question(db, interview, learner)}

    question_id = state.get("current_question_id")
    question = db.get(Question, question_id)
    if not question:
        raise HTTPException(409, "No current question is available")
    grade = grade_with_llm(question, cleaned_answer)
    score, feedback, missing, covered = grade["score"], grade["feedback"], grade["missing"], grade["covered"]
    db.add(Response(interview_id=interview.id, question_id=question.id, stage=interview.stage, topic=question.topic, answer=cleaned_answer, score=score, feedback=feedback))
    memory = memory_of(learner)
    transition = transition_graph.invoke({
        "score": score, "topic": question.topic, "memory": memory,
        "difficulty": interview.current_difficulty, "used_question_ids": state.get("used_question_ids", []),
        "stage": interview.stage, "stage_counts": state.get("stage_counts", {}), "route": "",
    })
    learner.memory_json = json.dumps(transition["memory"]); learner.updated_at = datetime.now(timezone.utc)
    interview.current_difficulty = transition["difficulty"]
    interview.stage = transition["stage"]
    state["stage_counts"] = transition["stage_counts"]
    state.setdefault("used_question_ids", []).append(question.id); state.setdefault("evaluations", []).append({"topic": question.topic, "score": score, "missing": missing, "covered": covered, "engine": grade["engine"], "route": transition["route"]})
    interview.state_json = json.dumps(state)
    if interview.stage == "complete": interview.completed_at = datetime.now(timezone.utc)
    db.commit()
    return {"evaluation": {"score": score, "feedback": feedback, "topic": question.topic, "missing": missing, "covered": covered, "difficulty_next": interview.current_difficulty, "engine": grade["engine"]}, **graph.next_question(db, interview, learner)}


@app.post("/api/interviews/{interview_id}/answer")
def submit_answer(interview_id: int, payload: AnswerRequest) -> dict[str, Any]:
    cleaned_answer = payload.answer.strip()
    if len(cleaned_answer) < 10:
        raise HTTPException(status_code=400, detail="Answer cannot be empty or whitespace. Please provide a detailed response (at least 10 characters) explaining your reasoning.")

    with SessionLocal() as db:
        interview = db.get(Interview, interview_id)
        if not interview or interview.stage == "complete":
            raise HTTPException(404, "Active interview not found")
        learner = db.get(Learner, interview.learner_id)
        return _execute_answer_evaluation(db, interview, learner, cleaned_answer)


def validate_grader(db: Any) -> dict[str, Any]:
    """Compare the configured AI grader with a small expert-labelled holdout set."""
    comparisons = []
    for question_id, answer, expert_score in EXPERT_BENCHMARK:
        question = db.get(Question, question_id)
        if not question:
            continue
        grade = grade_with_llm(question, answer)
        delta = abs(grade["score"] - expert_score)
        comparisons.append({"question_id": question_id, "topic": question.topic, "expert_score": expert_score, "ai_score": grade["score"], "absolute_error": delta, "engine": grade["engine"]})
    mae = round(sum(item["absolute_error"] for item in comparisons) / len(comparisons), 1) if comparisons else None
    agreement = round(100 * sum(item["absolute_error"] <= 15 for item in comparisons) / len(comparisons)) if comparisons else None
    return {"benchmark_size": len(comparisons), "mean_absolute_error": mae, "within_15_points_agreement_percent": agreement, "comparisons": comparisons, "note": "Run this endpoint after configuring OPENROUTER_API_KEY to validate the LLM grader against the included expert-labelled holdout set."}


@app.get("/api/interviews/{interview_id}/report")
def get_report(interview_id: int) -> dict[str, Any]:
    with SessionLocal() as db:
        interview = db.get(Interview, interview_id)
        if not interview: raise HTTPException(404, "Interview not found")
        return report(db, interview)


@app.get("/api/evaluation/validate")
def evaluation_validation() -> dict[str, Any]:
    with SessionLocal() as db:
        return validate_grader(db)


@app.get("/api/learners/{learner_id}/history")
def learner_history(learner_id: str) -> dict[str, Any]:
    with SessionLocal() as db:
        learner = db.get(Learner, learner_id)
        if not learner: raise HTTPException(404, "Learner not found")
        from sqlalchemy import select
        sessions = list(db.scalars(select(Interview).where(Interview.learner_id == learner_id).order_by(Interview.created_at.desc())).all())
        return {"learner_id": learner_id, "performance_context": history_tool.lookup(db, learner), "sessions": [{"id":s.id,"track":s.track,"stage":s.stage,"created_at":s.created_at} for s in sessions]}


@app.post("/api/feedback")
def submit_feedback(payload: FeedbackRequest) -> dict[str, Any]:
    """Capture candidate/user feedback on AI evaluations and log directly to LangSmith."""
    api_key = os.getenv("LANGCHAIN_API_KEY")
    if not api_key:
        return {"status": "saved_local", "message": "Feedback received. LangSmith API key not configured for remote logging."}
    try:
        client = Client()
        runs = list(client.list_runs(project_name=os.getenv("LANGCHAIN_PROJECT", "ds-interview-prep"), limit=5))
        target_run_id = runs[0].id if runs else None
        if target_run_id:
            client.create_feedback(
                run_id=target_run_id,
                key=payload.tag or "user_satisfaction",
                score=payload.score,
                comment=payload.comment,
            )
            return {"status": "success", "run_id": str(target_run_id), "message": "Feedback successfully logged to LangSmith."}
        return {"status": "success", "message": "Feedback recorded."}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@app.post("/api/evaluation/langsmith")
@app.get("/api/evaluation/langsmith")
def trigger_langsmith_evaluation(eval_type: str = Query(default="all", alias="type")) -> dict[str, Any]:
    """Run automated evaluations against LangSmith benchmark datasets."""
    if eval_type == "grader":
        return run_grader_evaluation()
    elif eval_type == "rag":
        return run_rag_evaluation()
    elif eval_type == "regression":
        return run_model_comparison()
    return run_langsmith_evaluation()

