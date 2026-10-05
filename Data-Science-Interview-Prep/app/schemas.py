from typing import Any, TypedDict
from pydantic import BaseModel, Field

class StartRequest(BaseModel):
    learner_id: str = Field(min_length=2, max_length=100)
    track: str
    level: str = "mid"


class AnswerRequest(BaseModel):
    answer: str = Field(min_length=3, max_length=8000)


class FeedbackRequest(BaseModel):
    interview_id: int
    score: float = Field(ge=0.0, le=1.0, description="1.0 for positive, 0.0 for negative or rating scaled to 0-1")
    comment: str | None = Field(default=None, max_length=1000)
    tag: str | None = Field(default="user_grade_feedback", max_length=100)



class StageState(TypedDict):
    """State for the explicit staged-agent graph: warmup -> technical -> case -> behavioral -> complete."""
    stage: str
    stage_counts: dict[str, int]


class RubricGrade(TypedDict):
    score: int
    feedback: str
    missing: list[str]
    covered: list[str]
    engine: str


class TransitionState(TypedDict):
    score: int
    topic: str
    memory: dict[str, float]
    difficulty: int
    used_question_ids: list[int]
    stage: str
    stage_counts: dict[str, int]
    route: str
