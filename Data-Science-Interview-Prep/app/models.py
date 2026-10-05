import json
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

from .questions import QUESTIONS

ROOT = Path(__file__).resolve().parent.parent
engine = create_engine(f"sqlite:///{ROOT / 'interview_prep.db'}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class Question(Base):
    __tablename__ = "questions"
    id: Mapped[int] = mapped_column(primary_key=True)
    stage: Mapped[str] = mapped_column(String(30), index=True)
    track: Mapped[str] = mapped_column(String(30), index=True)
    topic: Mapped[str] = mapped_column(String(80), index=True)
    difficulty: Mapped[int] = mapped_column(Integer)
    prompt: Mapped[str] = mapped_column(Text)
    reference: Mapped[str] = mapped_column(Text)
    rubric_json: Mapped[str] = mapped_column(Text)


class Learner(Base):
    __tablename__ = "learners"
    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    memory_json: Mapped[str] = mapped_column(Text, default="{}")
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


class Interview(Base):
    __tablename__ = "interviews"
    id: Mapped[int] = mapped_column(primary_key=True)
    learner_id: Mapped[str] = mapped_column(ForeignKey("learners.id"), index=True)
    track: Mapped[str] = mapped_column(String(30))
    level: Mapped[str] = mapped_column(String(30))
    stage: Mapped[str] = mapped_column(String(30), default="warmup")
    current_difficulty: Mapped[int] = mapped_column(Integer, default=2)
    state_json: Mapped[str] = mapped_column(Text, default="{}")
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


class Response(Base):
    __tablename__ = "responses"
    id: Mapped[int] = mapped_column(primary_key=True)
    interview_id: Mapped[int] = mapped_column(ForeignKey("interviews.id"), index=True)
    question_id: Mapped[int | None] = mapped_column(ForeignKey("questions.id"), nullable=True)
    stage: Mapped[str] = mapped_column(String(30))
    topic: Mapped[str] = mapped_column(String(80))
    answer: Mapped[str] = mapped_column(Text)
    score: Mapped[int] = mapped_column(Integer)
    feedback: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


def seed(db: Session) -> None:
    if db.scalar(select(Question.id).limit(1)):
        return
    rows = []
    for item in QUESTIONS:
        row = dict(item)
        row["rubric_json"] = json.dumps(row.pop("rubric"))
        rows.append(Question(**row))
    db.add_all(rows)
    db.commit()


def initialize_database() -> None:
    """Initialize eagerly so CLI scripts and ASGI lifespan hosts behave identically."""
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        seed(db)
