import json
import os
import re
from collections import defaultdict
from threading import Lock
from typing import Any

from langsmith import traceable
from langsmith.wrappers import wrap_openai
from openai import OpenAI
import chromadb
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy import select
from sqlalchemy.orm import Session

from .constants import CONCEPT_HINTS
from .models import ROOT, Interview, Learner, Question, Response
from .schemas import RubricGrade

PROMPT_VERSION = "v1.2"


def memory_of(learner: Learner) -> dict[str, float]:
    return json.loads(learner.memory_json or "{}")


def target_difficulty(level: str) -> int:
    return {"junior": 1, "entry": 1, "mid": 2, "senior": 3}.get(level.lower(), 2)


@traceable(name="score_answer_locally", run_type="chain", tags=["local_rubric_grader"])
def score_answer_locally(question: Question, answer: str) -> tuple[int, str, list[str], list[str]]:
    answer_lower = answer.lower()
    rubric = json.loads(question.rubric_json)
    earned, missing, covered = 0.0, [], []
    for concept, weight in rubric.items():
        hints = CONCEPT_HINTS.get(concept, [concept.replace("_", " ")])
        display_concept = concept.replace("_", " ")
        if any(hint in answer_lower for hint in hints):
            earned += weight
            covered.append(display_concept)
        else:
            missing.append(display_concept)
    try:
        matrix = TfidfVectorizer(stop_words="english").fit_transform([question.reference, answer])
        semantic = float(cosine_similarity(matrix[0], matrix[1])[0][0])
    except ValueError:
        semantic = 0.0
    score = round(min(1, earned * 0.85 + semantic * 0.15) * 100)
    if score >= 80:
        feedback = "Strong, well-supported response. You covered the central reasoning expected by the rubric."
    elif score >= 55:
        feedback = "Solid foundation, but the explanation was incomplete. Add the missing concepts to make your reasoning more interview-ready."
    else:
        feedback = "This needs a clearer, more complete answer. Start with the core principle, then explain the practical decision or trade-off."
    if missing:
        feedback += " Missing or unclear: " + ", ".join(missing[:3]) + "."
    return score, feedback, missing, covered


@traceable(
    name="grade_with_llm",
    run_type="chain",
    tags=["rubric_evaluation", "llm_grader"],
    metadata={"prompt_version": PROMPT_VERSION},
)
def grade_with_llm(question: Question, answer: str) -> RubricGrade:
    """Grade open-ended answers against the full expert rubric via OpenRouter."""
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        score, feedback, missing, covered = score_answer_locally(question, answer)
        return {"score": score, "feedback": feedback, "missing": missing, "covered": covered, "engine": "local rubric fallback"}
    rubric = json.loads(question.rubric_json)
    prompt = f"""You are an expert Data Science interview assessor. Grade the learner answer using the reference answer and weighted rubric below. Assess technical correctness, completeness, and reasoning; do not reward unsupported claims. Return ONLY valid JSON with: score (integer 0-100), feedback (brief actionable string), missing (array of missing or weak concepts), covered (array of successfully demonstrated concepts).

Question: {question.prompt}
Reference answer: {question.reference}
Weighted rubric: {json.dumps(rubric)}
Learner answer: {answer}
"""
    try:
        raw_client = OpenAI(
            base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
            api_key=api_key,
            default_headers={"X-OpenRouter-Title": "DS Interview Prep Bot"},
        )
        client = wrap_openai(raw_client)
        completion = client.chat.completions.create(
            model=os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini"),
            messages=[{"role": "system", "content": "You return strict JSON only."}, {"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=300,
        )
        content = (completion.choices[0].message.content or "").strip()
        content = re.sub(r"^```(?:json)?\s*|\s*```$", "", content).strip()
        result = json.loads(content)
        score = max(0, min(100, int(result["score"])))
        feedback = str(result["feedback"]).strip()[:1200]
        missing = [str(item)[:80] for item in result.get("missing", [])[:4]]
        covered = [str(item)[:80] for item in result.get("covered", [])[:4]]
        if not feedback:
            raise ValueError("Empty feedback")
        return {"score": score, "feedback": feedback, "missing": missing, "covered": covered, "engine": "OpenRouter LLM rubric grader"}
    except Exception:
        score, feedback, missing, covered = score_answer_locally(question, answer)
        return {"score": score, "feedback": feedback, "missing": missing, "covered": covered, "engine": "local rubric fallback"}


class VectorRAG:
    """Persistent ChromaDB index of complete interview question bundles."""
    def __init__(self) -> None:
        self._client = None
        self._collection = None
        self._encoder = None
        self._lock = Lock()

    def _ready(self) -> None:
        if self._collection is not None:
            return
        with self._lock:
            if self._collection is not None:
                return
            self._client = chromadb.PersistentClient(path=str(ROOT / "chroma_store"))
            self._collection = self._client.get_or_create_collection(
                name="ds_interview_question_bundles", metadata={"hnsw:space": "cosine"}
            )
            try:
                self._encoder = SentenceTransformer("all-MiniLM-L6-v2")
            except Exception:
                self._encoder = None

    @staticmethod
    def bundle(question: Question) -> str:
        return (
            f"Track: {question.track}\nStage: {question.stage}\nTopic: {question.topic}\n"
            f"Difficulty: {question.difficulty}\nQuestion: {question.prompt}\n"
            f"Reference answer: {question.reference}\nRubric: {question.rubric_json}"
        )

    @traceable(name="vector_rag_retrieval", run_type="retriever", tags=["chromadb", "vector_rag"])
    def retrieve_ids(self, db: Session, query: str, limit: int = 12) -> list[int]:
        self._ready()
        if self._encoder is None:
            raise RuntimeError("SentenceTransformer encoder is unavailable")
        questions = list(db.scalars(select(Question)).all())
        ids = [str(q.id) for q in questions]
        documents = [self.bundle(q) for q in questions]
        self._collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=self._encoder.encode(documents, normalize_embeddings=True).tolist(),
            metadatas=[{"stage": q.stage, "track": q.track, "topic": q.topic, "difficulty": q.difficulty} for q in questions],
        )
        result = self._collection.query(
            query_embeddings=[self._encoder.encode(query, normalize_embeddings=True).tolist()],
            n_results=min(limit, len(ids)),
            include=["distances", "documents", "metadatas"],
        )
        return [int(question_id) for question_id in result["ids"][0]]


vector_rag = VectorRAG()


class PerformanceHistoryTool:
    """Agent tool: exposes concise cross-session evidence for question selection and reports."""
    @traceable(name="history_tool_lookup", run_type="tool", tags=["learner_memory"])
    def lookup(self, db: Session, learner: Learner) -> dict[str, Any]:
        memory = memory_of(learner)
        historical = list(db.scalars(
            select(Response).join(Interview, Response.interview_id == Interview.id)
            .where(Interview.learner_id == learner.id, Response.stage != "warmup")
            .order_by(Response.created_at.desc()).limit(30)
        ).all())
        topic_scores: dict[str, list[int]] = defaultdict(list)
        for response in historical:
            topic_scores[response.topic].append(response.score)
        return {
            "memory": memory,
            "prior_answers": len(historical),
            "weak_topics": [topic for topic, signal in sorted(memory.items(), key=lambda item: item[1]) if signal < -0.15][:4],
            "mastered_topics": [topic for topic, signal in sorted(memory.items(), key=lambda item: item[1], reverse=True) if signal > 0.35][:4],
            "topic_averages": {topic: round(sum(scores) / len(scores)) for topic, scores in topic_scores.items()},
        }


history_tool = PerformanceHistoryTool()

