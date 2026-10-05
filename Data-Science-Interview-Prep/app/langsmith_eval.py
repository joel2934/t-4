import os
from typing import Any

from langsmith import Client, evaluate
from langsmith.schemas import Example, Run
from sqlalchemy import select

from .constants import EXPERT_BENCHMARK
from .evaluator import grade_with_llm, vector_rag
from .models import Question, SessionLocal, initialize_database

GRADER_DATASET_NAME = "ds-interview-expert-benchmark"
RAG_DATASET_NAME = "ds-interview-rag-benchmark"

RAG_BENCHMARK_QUERIES = [
    {
        "query": "Role/track: ml. Level: mid. Stage: technical. Needs practice: overfitting, regularization.",
        "target_topics": ["overfitting", "regularization", "validation"],
        "track": "ml",
    },
    {
        "query": "Role/track: analytics. Level: senior. Stage: technical. Needs practice: ab_testing, p_values, guardrails.",
        "target_topics": ["ab_testing", "experiment", "statistics"],
        "track": "analytics",
    },
    {
        "query": "Role/track: ml. Level: mid. Stage: technical. Needs practice: data_leakage, temporal_split.",
        "target_topics": ["data_leakage", "features", "time_split"],
        "track": "ml",
    },
    {
        "query": "Role/track: analytics. Level: mid. Stage: case. Needs practice: funnel_dropoff, cohort_segmentation.",
        "target_topics": ["funnel", "segmentation", "case"],
        "track": "analytics",
    },
    {
        "query": "Role/track: ml. Level: senior. Stage: technical. Needs practice: training_serving_skew, drift_monitoring.",
        "target_topics": ["training_serving_skew", "monitoring", "operations"],
        "track": "ml",
    },
]


def sync_grader_dataset(client: Client) -> Any:
    """Ensure the expert benchmark dataset exists and is populated in LangSmith."""
    if not client.has_dataset(dataset_name=GRADER_DATASET_NAME):
        dataset = client.create_dataset(
            dataset_name=GRADER_DATASET_NAME,
            description="Expert-labelled holdout dataset for Data Science candidate answer grading validation.",
        )
        initialize_database()
        with SessionLocal() as db:
            for question_id, answer, expert_score in EXPERT_BENCHMARK:
                question = db.get(Question, question_id)
                if not question:
                    continue
                client.create_example(
                    inputs={
                        "question_id": question_id,
                        "prompt": question.prompt,
                        "reference": question.reference,
                        "rubric_json": question.rubric_json,
                        "answer": answer,
                        "topic": question.topic,
                        "track": question.track,
                    },
                    outputs={"expert_score": expert_score},
                    dataset_id=dataset.id,
                )
        return dataset
    return client.read_dataset(dataset_name=GRADER_DATASET_NAME)


def sync_rag_dataset(client: Client) -> Any:
    """Ensure the RAG retrieval benchmark dataset exists and is populated in LangSmith."""
    if not client.has_dataset(dataset_name=RAG_DATASET_NAME):
        dataset = client.create_dataset(
            dataset_name=RAG_DATASET_NAME,
            description="Benchmark dataset for ChromaDB VectorRAG retrieval quality and grounding in DS interview questions.",
        )
        for item in RAG_BENCHMARK_QUERIES:
            client.create_example(
                inputs={"query": item["query"], "track": item["track"]},
                outputs={"target_topics": item["target_topics"]},
                dataset_id=dataset.id,
            )
        return dataset
    return client.read_dataset(dataset_name=RAG_DATASET_NAME)


def eval_grader_target(inputs: dict[str, Any]) -> dict[str, Any]:
    """Target evaluation function wrapper for LLM grading."""
    question_id = inputs.get("question_id")
    answer = inputs.get("answer", "")
    with SessionLocal() as db:
        question = db.get(Question, question_id)
        if not question:
            return {"score": 0, "feedback": "Question not found", "missing": [], "covered": [], "engine": "error"}
        grade = grade_with_llm(question, answer)
        return {
            "score": grade["score"],
            "feedback": grade["feedback"],
            "missing": grade["missing"],
            "covered": grade["covered"],
            "engine": grade["engine"],
        }


def eval_rag_target(inputs: dict[str, Any]) -> dict[str, Any]:
    """Target evaluation function wrapper for VectorRAG retrieval."""
    query = inputs.get("query", "")
    with SessionLocal() as db:
        try:
            retrieved_ids = vector_rag.retrieve_ids(db, query, limit=5)
            questions = [db.get(Question, qid) for qid in retrieved_ids]
            topics = [q.topic for q in questions if q]
            tracks = [q.track for q in questions if q]
            return {"retrieved_ids": retrieved_ids, "topics": topics, "tracks": tracks, "status": "success"}
        except Exception as e:
            return {"retrieved_ids": [], "topics": [], "tracks": [], "status": "error", "error": str(e)}


# --- Multi-Dimensional Grader Evaluators ---

def metric_absolute_error(root_run: Run, example: Example) -> dict[str, Any]:
    """Absolute score error vs expert benchmark."""
    ai_score = (root_run.outputs or {}).get("score", 0)
    expert_score = (example.outputs or {}).get("expert_score", 0)
    return {"key": "absolute_error", "score": abs(ai_score - expert_score)}


def metric_within_15_agreement(root_run: Run, example: Example) -> dict[str, Any]:
    """Binary agreement indicator (error <= 15 points)."""
    ai_score = (root_run.outputs or {}).get("score", 0)
    expert_score = (example.outputs or {}).get("expert_score", 0)
    return {"key": "within_15_agreement", "score": 1 if abs(ai_score - expert_score) <= 15 else 0}


def metric_feedback_quality(root_run: Run, example: Example) -> dict[str, Any]:
    """Evaluates if feedback is actionable, non-empty, and provides concrete reasoning."""
    feedback = (root_run.outputs or {}).get("feedback", "")
    is_quality = 1 if len(feedback.strip()) >= 25 and not feedback.lower().startswith("error") else 0
    return {"key": "feedback_quality", "score": is_quality}


def metric_rubric_fidelity(root_run: Run, example: Example) -> dict[str, Any]:
    """Checks consistency between score and covered/missing concept breakdowns."""
    outputs = root_run.outputs or {}
    score = outputs.get("score", 0)
    missing = outputs.get("missing", [])
    covered = outputs.get("covered", [])
    
    # High score should have covered concepts; low score should have missing concepts
    consistent = True
    if score >= 80 and not covered:
        consistent = False
    if score <= 40 and not missing:
        consistent = False
        
    return {"key": "rubric_fidelity", "score": 1 if consistent else 0}


# --- RAG Retrieval Evaluators ---

def metric_rag_topic_precision(root_run: Run, example: Example) -> dict[str, Any]:
    """Calculates topic precision for VectorRAG retrieved question bundles."""
    outputs = root_run.outputs or {}
    retrieved_topics = [t.lower() for t in outputs.get("topics", [])]
    target_topics = [t.lower() for t in (example.outputs or {}).get("target_topics", [])]
    
    if not retrieved_topics or not target_topics:
        return {"key": "rag_topic_precision", "score": 0.0}
        
    matches = sum(1 for rt in retrieved_topics if any(target in rt or rt in target for target in target_topics))
    score = round(matches / len(retrieved_topics), 2)
    return {"key": "rag_topic_precision", "score": score}


# --- Evaluation Runner Functions ---

def run_grader_evaluation() -> dict[str, Any]:
    """Run automated evaluations on the LLM grader against the expert benchmark."""
    api_key = os.getenv("LANGCHAIN_API_KEY")
    if not api_key:
        return {
            "status": "disabled",
            "message": "LANGCHAIN_API_KEY environment variable is not set. Please configure it in app/.env.",
        }

    try:
        client = Client()
        dataset = sync_grader_dataset(client)
        experiment_results = evaluate(
            eval_grader_target,
            data=dataset.name,
            evaluators=[
                metric_absolute_error,
                metric_within_15_agreement,
                metric_feedback_quality,
                metric_rubric_fidelity,
            ],
            experiment_prefix="ds-grader-eval",
            metadata={
                "model": os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini"),
                "task": "candidate_answer_grading",
            },
        )
        return {
            "status": "success",
            "type": "grader_evaluation",
            "dataset": dataset.name,
            "experiment_results": str(experiment_results),
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


def run_rag_evaluation() -> dict[str, Any]:
    """Run automated retrieval evaluations on ChromaDB VectorRAG."""
    api_key = os.getenv("LANGCHAIN_API_KEY")
    if not api_key:
        return {
            "status": "disabled",
            "message": "LANGCHAIN_API_KEY environment variable is not set. Please configure it in app/.env.",
        }

    try:
        client = Client()
        dataset = sync_rag_dataset(client)
        experiment_results = evaluate(
            eval_rag_target,
            data=dataset.name,
            evaluators=[metric_rag_topic_precision],
            experiment_prefix="ds-rag-retrieval-eval",
            metadata={"retriever": "chromadb_sentence_transformers", "task": "rag_question_retrieval"},
        )
        return {
            "status": "success",
            "type": "rag_evaluation",
            "dataset": dataset.name,
            "experiment_results": str(experiment_results),
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


def run_model_comparison(models: list[str] | None = None) -> dict[str, Any]:
    """Safely run regression testing comparing different models or prompt versions in LangSmith."""
    api_key = os.getenv("LANGCHAIN_API_KEY")
    if not api_key:
        return {"status": "disabled", "message": "LANGCHAIN_API_KEY not set."}

    target_models = models or [os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")]
    client = Client()
    dataset = sync_grader_dataset(client)
    comparison_runs = {}

    current_model = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")
    try:
        for model in target_models:
            os.environ["OPENROUTER_MODEL"] = model
            results = evaluate(
                eval_grader_target,
                data=dataset.name,
                evaluators=[metric_absolute_error, metric_within_15_agreement, metric_feedback_quality],
                experiment_prefix=f"model-cmp-{model.replace('/', '-').replace(':', '-')}",
                metadata={"model": model, "purpose": "model_regression_comparison"},
            )
            comparison_runs[model] = str(results)
    finally:
        os.environ["OPENROUTER_MODEL"] = current_model

    return {
        "status": "success",
        "dataset": dataset.name,
        "models_evaluated": target_models,
        "experiments": comparison_runs,
        "note": "Regression comparison runs successfully logged in LangSmith dashboard for side-by-side analysis.",
    }


def run_langsmith_evaluation() -> dict[str, Any]:
    """Unified entrypoint: executes both Grader and RAG automated evaluations."""
    grader_res = run_grader_evaluation()
    rag_res = run_rag_evaluation()
    return {
        "status": "success" if grader_res.get("status") == "success" and rag_res.get("status") == "success" else "partial",
        "grader_evaluation": grader_res,
        "rag_evaluation": rag_res,
        "note": "Automated evaluation pipelines completed and recorded in LangSmith.",
    }


if __name__ == "__main__":
    results = run_langsmith_evaluation()
    print(results)
