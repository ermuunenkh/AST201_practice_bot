from datetime import datetime, timezone

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    name: Mapped[str | None] = mapped_column(String(100))
    timezone: Mapped[str] = mapped_column(String(50), default="UTC")
    registered_at: Mapped[datetime] = mapped_column(DateTime, default=_now)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[str] = mapped_column(String(20), primary_key=True)
    topic: Mapped[str] = mapped_column(String(100), nullable=False)
    subtopic: Mapped[str | None] = mapped_column(String(100))
    q_type: Mapped[str] = mapped_column(String(20), nullable=False)
    difficulty: Mapped[int] = mapped_column(Integer, default=2)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    choices_json: Mapped[str | None] = mapped_column(Text)
    answer: Mapped[str] = mapped_column(String(10), nullable=False)
    explanation: Mapped[str | None] = mapped_column(Text)
    image_path: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)


class Answer(Base):
    __tablename__ = "answers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.chat_id"), nullable=False)
    question_id: Mapped[str] = mapped_column(String(20), ForeignKey("questions.id"), nullable=False)
    chosen: Mapped[str | None] = mapped_column(String(10))
    is_correct: Mapped[bool | None] = mapped_column(Boolean)
    response_time_sec: Mapped[float | None] = mapped_column(Float)
    asked_at: Mapped[datetime | None] = mapped_column(DateTime)
    answered_at: Mapped[datetime | None] = mapped_column(DateTime)


class TopicScore(Base):
    __tablename__ = "topic_scores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.chat_id"), nullable=False)
    topic: Mapped[str] = mapped_column(String(100), nullable=False)
    correct: Mapped[int] = mapped_column(Integer, default=0)
    total: Mapped[int] = mapped_column(Integer, default=0)
    last_asked_at: Mapped[datetime | None] = mapped_column(DateTime)

    __table_args__ = (UniqueConstraint("user_id", "topic", name="uq_topic_score_user_topic"),)


class SendEvent(Base):
    __tablename__ = "send_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.chat_id"), nullable=False)
    question_id: Mapped[str] = mapped_column(String(20), ForeignKey("questions.id"), nullable=False)
    sent_at: Mapped[datetime] = mapped_column(DateTime, default=_now)
    was_answered: Mapped[bool] = mapped_column(Boolean, default=False)


class UserActivity(Base):
    __tablename__ = "user_activity"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.chat_id"), nullable=False)
    hour_of_day: Mapped[int] = mapped_column(Integer, nullable=False)
    day_of_week: Mapped[int] = mapped_column(Integer, nullable=False)
    avg_response_sec: Mapped[float | None] = mapped_column(Float)
    response_rate: Mapped[float | None] = mapped_column(Float)
    sample_count: Mapped[int] = mapped_column(Integer, default=0)

    __table_args__ = (
        UniqueConstraint("user_id", "hour_of_day", "day_of_week", name="uq_activity_user_hour_dow"),
    )
