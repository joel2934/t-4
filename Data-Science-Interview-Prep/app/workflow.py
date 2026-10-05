from collections import defaultdict
import json
from typing import Any

from fastapi import HTTPException
from langgraph.graph import END, START, StateGraph
from langsmith import traceable
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from sqlalchemy import select
from sqlalchemy.orm import Session

from .constants import FRAMEWORK_HINTS, STAGE_ORDER, STAGE_REQUIRED
from .evaluator import history_tool, memory_of, vector_rag
from .models import Interview, Learner, Question, Response
from .schemas import StageState, TransitionState


def _stage_pass_node(state: StageState) -> dict[str, Any]:
    return {}


def _advance_stage_node(state: StageState) -> dict[str, Any]:
    idx = STAGE_ORDER.index(state["stage"])
    next_stage = STAGE_ORDER[idx + 1] if idx + 1 < len(STAGE_ORDER) else "complete"
    return {"stage": next_stage}


def _route_to_current_stage(state: StageState) -> str:
    return state["stage"]


def _stage_is_complete(state: StageState) -> str:
    stage = state["stage"]
    if state["stage_counts"].get(stage, 0) >= STAGE_REQUIRED[stage]:
        return "advance"
    return "stay"


_stage_builder = StateGraph(StageState)
for _name in STAGE_ORDER:
    _stage_builder.add_node(_name, _stage_pass_node)
_stage_builder.add_node("advance", _advance_stage_node)
_stage_builder.add_conditional_edges(START, _route_to_current_stage, {name: name for name in STAGE_ORDER})
for _name in STAGE_ORDER:
    _stage_builder.add_conditional_edges(_name, _stage_is_complete, {"advance": "advance", "stay": END})
_stage_builder.add_edge("advance", END)
stage_graph = _stage_builder.compile()


def state_of(interview: Interview) -> dict[str, Any]:
    return json.loads(interview.state_json or "{}")


def update_memory_node(state: TransitionState) -> dict[str, Any]:
    memory = dict(state["memory"])
    signal = (state["score"] - 65) / 35
    memory[state["topic"]] = round(memory.get(state["topic"], 0.0) * .65 + signal * .35, 3)
    return {"memory": memory}


def adapt_difficulty_node(state: TransitionState) -> dict[str, Any]:
    difficulty = state["difficulty"]
    if state["score"] >= 78: difficulty = min(3, difficulty + 1)
    elif state["score"] < 55: difficulty = max(1, difficulty - 1)
    return {"difficulty": difficulty}


def advance_stage_node(state: TransitionState) -> dict[str, Any]:
    counts = dict(state["stage_counts"])
    stage = state["stage"]
    counts[stage] = counts.get(stage, 0) + 1
    routed = stage_graph.invoke({"stage": stage, "stage_counts": counts})
    return {"stage_counts": counts, "stage": routed["stage"]}


def route_after_score(state: TransitionState) -> str:
    if state["score"] < 55:
        return "reinforce_weakness"
    if state["score"] >= 85:
        return "stretch_candidate"
    return "advance_stage"


def reinforce_weakness_node(state: TransitionState) -> dict[str, Any]:
    memory = dict(state["memory"])
    memory[state["topic"]] = round(memory.get(state["topic"], 0.0) - 0.12, 3)
    return {"memory": memory, "route": "reinforcement"}


def stretch_candidate_node(state: TransitionState) -> dict[str, Any]:
    return {"route": "stretch"}


transition_builder = StateGraph(TransitionState)
transition_builder.add_node("update_memory", update_memory_node)
transition_builder.add_node("adapt_difficulty", adapt_difficulty_node)
transition_builder.add_node("advance_stage", advance_stage_node)
transition_builder.add_node("reinforce_weakness", reinforce_weakness_node)
transition_builder.add_node("stretch_candidate", stretch_candidate_node)
transition_builder.add_edge(START, "update_memory")
transition_builder.add_edge("update_memory", "adapt_difficulty")
transition_builder.add_conditional_edges("adapt_difficulty", route_after_score, {
    "reinforce_weakness": "reinforce_weakness", "stretch_candidate": "stretch_candidate", "advance_stage": "advance_stage"
})
transition_builder.add_edge("reinforce_weakness", "advance_stage")
transition_builder.add_edge("stretch_candidate", "advance_stage")
transition_builder.add_edge("advance_stage", END)
transition_graph = transition_builder.compile()


def report(db: Session, interview: Interview) -> dict[str, Any]:
    responses = list(db.scalars(select(Response).where(Response.interview_id == interview.id, Response.stage != "warmup")).all())
    if not responses: raise HTTPException(409, "Interview has no scored answers yet")
    by_topic: dict[str, list[int]] = defaultdict(list)
    by_stage: dict[str, list[int]] = defaultdict(list)
    for r in responses: by_topic[r.topic].append(r.score); by_stage[r.stage].append(r.score)
    topic_scores = {t: round(sum(v) / len(v)) for t,v in by_topic.items()}
    strengths = [t for t,_ in sorted(topic_scores.items(), key=lambda x:x[1], reverse=True)[:3]]
    weak_areas = [t for t,_ in sorted(topic_scores.items(), key=lambda x:x[1])[:3]]
    overall = round(sum(r.score for r in responses) / len(responses))
    
    response_details = []
    for r in responses:
        q = db.get(Question, r.question_id) if r.question_id else None
        response_details.append({
            "stage": r.stage,
            "topic": r.topic,
            "score": r.score,
            "feedback": r.feedback,
            "question": q.prompt if q else "",
            "reference": q.reference if q else ""
        })
    return {
        "interview_id": interview.id,
        "completed": interview.stage == "complete",
        "overall_score": overall,
        "stage_scores": {s: round(sum(v)/len(v)) for s,v in by_stage.items()},
        "strengths": strengths,
        "weak_areas": weak_areas,
        "recommendations": [f"Practice {topic} using a structured answer: define the concept, state the trade-off, then give a real-world example." for topic in weak_areas],
        "responses": response_details
    }


class InterviewGraph:
    """Explicit staged agent workflow: retrieve → present → capture → score → adapt."""
    @traceable(name="interview_question_retrieval", run_type="chain", tags=["question_selection"])
    def retrieve(self, db: Session, interview: Interview, learner: Learner) -> Question:
        state = state_of(interview)
        history = history_tool.lookup(db, learner)
        memory = history["memory"]
        used = set(state.get("used_question_ids", []))
        candidates = list(db.scalars(select(Question).where(Question.stage == interview.stage)).all())
        candidates = [q for q in candidates if q.id not in used and (q.track == interview.track or q.track == "all")]
        historical_ids = set(db.scalars(
            select(Response.question_id)
            .join(Interview, Response.interview_id == Interview.id)
            .where(Interview.learner_id == interview.learner_id, Response.question_id.is_not(None))
        ).all())
        unseen_candidates = [q for q in candidates if q.id not in historical_ids]
        if unseen_candidates:
            candidates = unseen_candidates
        if not candidates:  
            candidates = list(db.scalars(select(Question).where(Question.stage == interview.stage)).all())
            candidates = [q for q in candidates if q.track == interview.track or q.track == "all"]
        query = (
            f"Role/track: {interview.track}. Level: {interview.level}. Stage: {interview.stage}. "
            f"Warmup goal: {state.get('warmup_context', '')}. "
            f"Needs practice: {', '.join(history['weak_topics'])}. "
            f"Already mastered: {', '.join(history['mastered_topics'])}."
        )
        try:
            vector_order = vector_rag.retrieve_ids(db, query)
            vector_rank = {question_id: index for index, question_id in enumerate(vector_order)}
            relevance = [1 - vector_rank.get(q.id, len(vector_order)) / max(1, len(vector_order)) for q in candidates]
        except Exception:
            corpus = [f"{q.track} {q.stage} {q.topic} {q.prompt} {q.reference}" for q in candidates]
            relevance = [0.0] * len(candidates)
            if len(candidates) > 1:
                matrix = TfidfVectorizer(stop_words="english").fit_transform([query] + corpus)
                relevance = cosine_similarity(matrix[0], matrix[1:]).flatten().tolist()
        desired = interview.current_difficulty
        def rank(i: int) -> float:
            q = candidates[i]
            weak_boost = max(0.0, -memory.get(q.topic, 0.0)) * 0.8
            mastered_penalty = max(0.0, memory.get(q.topic, 0.0)) * 0.55
            level_fit = 0.55 if q.difficulty == desired else 0.0
            return relevance[i] + weak_boost + level_fit - mastered_penalty - .65 * abs(q.difficulty - desired)
        return candidates[max(range(len(candidates)), key=rank)]

    @traceable(name="interview_next_question", run_type="chain", tags=["interview_flow"])
    def next_question(self, db: Session, interview: Interview, learner: Learner) -> dict[str, Any]:

        if interview.stage == "complete":
            return {"complete": True, "report": report(db, interview)}
        if interview.stage == "warmup":
            return {
                "complete": False,
                "stage": "warmup",
                "message": f"Welcome to your Data Science Mock Assessment. I am your AI Interview Assessor. Today, we will evaluate your technical depth, business problem-solving, and behavioral competencies tailored for a {interview.level.title()}-Level {interview.track.upper()} role.\n\nTo begin, please introduce yourself and summarize your data science background and primary project focus.",
                "question_id": None,
                "difficulty": 0,
                "framework_hint": FRAMEWORK_HINTS["warmup"]
            }
        q = self.retrieve(db, interview, learner)
        state = state_of(interview)
        state["current_question_id"] = q.id
        interview.state_json = json.dumps(state)
        db.commit()
        return {
            "complete": False,
            "stage": interview.stage,
            "message": f"{interview.stage.replace('_',' ').title()} Round · Target Difficulty Level {q.difficulty}/3",
            "question_id": q.id,
            "topic": q.topic,
            "difficulty": q.difficulty,
            "question": q.prompt,
            "framework_hint": FRAMEWORK_HINTS.get(interview.stage, FRAMEWORK_HINTS["technical"])
        }

graph = InterviewGraph()
