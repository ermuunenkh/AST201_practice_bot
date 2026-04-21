from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import func, select

from db.database import get_session
from db.models import Answer, Question, SendEvent, TopicScore, User, UserActivity


# ---------------------------------------------------------------------------
# User queries
# ---------------------------------------------------------------------------

def register_user(chat_id: int, name: str) -> User:
    with get_session() as session:
        user = session.execute(
            select(User).where(User.chat_id == chat_id)
        ).scalar_one_or_none()

        if user is None:
            user = User(chat_id=chat_id, name=name)
            session.add(user)
        else:
            user.name = name

    return user


def get_user(chat_id: int) -> Optional[User]:
    with get_session() as session:
        return session.execute(
            select(User).where(User.chat_id == chat_id)
        ).scalar_one_or_none()


def get_all_active_users() -> list[User]:
    with get_session() as session:
        return list(
            session.execute(select(User).where(User.is_active == True)).scalars().all()
        )


# ---------------------------------------------------------------------------
# Question queries
# ---------------------------------------------------------------------------

def get_question(q_id: str) -> Optional[Question]:
    with get_session() as session:
        return session.get(Question, q_id)


def get_questions_by_topic(topic: str, limit: int = 20) -> list[Question]:
    with get_session() as session:
        return list(
            session.execute(
                select(Question).where(Question.topic == topic).limit(limit)
            ).scalars().all()
        )


def get_unseen_questions(
    user_id: int, topic: Optional[str] = None, limit: int = 10
) -> list[Question]:
    with get_session() as session:
        asked_ids = select(Answer.question_id).where(Answer.user_id == user_id)

        stmt = select(Question).where(Question.id.not_in(asked_ids))
        if topic:
            stmt = stmt.where(Question.topic == topic)
        stmt = stmt.limit(limit)

        return list(session.execute(stmt).scalars().all())


def get_questions_not_asked_recently(user_id: int, days: int = 3) -> list[Question]:
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    with get_session() as session:
        recent_ids = (
            select(Answer.question_id)
            .where(Answer.user_id == user_id)
            .where(Answer.asked_at >= cutoff)
        )
        stmt = select(Question).where(Question.id.not_in(recent_ids))
        return list(session.execute(stmt).scalars().all())


def get_all_topics() -> list[str]:
    with get_session() as session:
        return list(
            session.execute(select(Question.topic).distinct()).scalars().all()
        )


# ---------------------------------------------------------------------------
# Answer queries
# ---------------------------------------------------------------------------

def record_answer(
    user_id: int,
    question_id: str,
    chosen: str,
    response_time_sec: Optional[float],
    asked_at: datetime,
    answered_at: datetime,
) -> Answer:
    question = get_question(question_id)
    is_correct = question is not None and chosen == question.answer

    with get_session() as session:
        answer = Answer(
            user_id=user_id,
            question_id=question_id,
            chosen=chosen,
            is_correct=is_correct,
            response_time_sec=response_time_sec,
            asked_at=asked_at,
            answered_at=answered_at,
        )
        session.add(answer)

    if question:
        update_topic_score(user_id, question.topic, is_correct)

    return answer


def update_topic_score(user_id: int, topic: str, is_correct: bool) -> None:
    with get_session() as session:
        score = session.execute(
            select(TopicScore).where(
                TopicScore.user_id == user_id, TopicScore.topic == topic
            )
        ).scalar_one_or_none()

        now = datetime.now(timezone.utc)
        if score is None:
            score = TopicScore(
                user_id=user_id,
                topic=topic,
                correct=1 if is_correct else 0,
                total=1,
                last_asked_at=now,
            )
            session.add(score)
        else:
            if is_correct:
                score.correct += 1
            score.total += 1
            score.last_asked_at = now


# ---------------------------------------------------------------------------
# Send event queries
# ---------------------------------------------------------------------------

def record_send_event(user_id: int, question_id: str) -> SendEvent:
    with get_session() as session:
        event = SendEvent(user_id=user_id, question_id=question_id)
        session.add(event)
    return event


def mark_answered(send_event_id: int) -> None:
    with get_session() as session:
        event = session.get(SendEvent, send_event_id)
        if event:
            event.was_answered = True


def get_send_event(user_id: int, question_id: str) -> Optional[SendEvent]:
    with get_session() as session:
        return session.execute(
            select(SendEvent)
            .where(SendEvent.user_id == user_id, SendEvent.question_id == question_id)
            .order_by(SendEvent.sent_at.desc())
        ).scalar_one_or_none()


# ---------------------------------------------------------------------------
# Topic score queries
# ---------------------------------------------------------------------------

def get_topic_scores(user_id: int) -> list[TopicScore]:
    with get_session() as session:
        return list(
            session.execute(
                select(TopicScore).where(TopicScore.user_id == user_id)
            ).scalars().all()
        )


def get_weakest_topic(user_id: int, min_attempts: int = 3) -> Optional[str]:
    with get_session() as session:
        scores = session.execute(
            select(TopicScore).where(
                TopicScore.user_id == user_id,
                TopicScore.total >= min_attempts,
            )
        ).scalars().all()

    if not scores:
        return None

    weakest = min(scores, key=lambda s: s.correct / s.total if s.total else 1.0)
    return weakest.topic


# ---------------------------------------------------------------------------
# Activity queries
# ---------------------------------------------------------------------------

def update_user_activity(
    user_id: int,
    hour: int,
    dow: int,
    response_time_sec: Optional[float],
    did_respond: bool,
) -> None:
    with get_session() as session:
        row = session.execute(
            select(UserActivity).where(
                UserActivity.user_id == user_id,
                UserActivity.hour_of_day == hour,
                UserActivity.day_of_week == dow,
            )
        ).scalar_one_or_none()

        if row is None:
            row = UserActivity(
                user_id=user_id,
                hour_of_day=hour,
                day_of_week=dow,
                avg_response_sec=response_time_sec if did_respond else None,
                response_rate=1.0 if did_respond else 0.0,
                sample_count=1,
            )
            session.add(row)
        else:
            n = row.sample_count
            if did_respond and response_time_sec is not None:
                prev = row.avg_response_sec or 0.0
                row.avg_response_sec = (prev * n + response_time_sec) / (n + 1)
            prev_rate = row.response_rate or 0.0
            row.response_rate = (prev_rate * n + (1.0 if did_respond else 0.0)) / (n + 1)
            row.sample_count += 1


def get_recent_send_topics(user_id: int, limit: int = 5) -> list[str]:
    with get_session() as session:
        rows = session.execute(
            select(SendEvent.question_id)
            .where(SendEvent.user_id == user_id)
            .order_by(SendEvent.sent_at.desc())
            .limit(limit)
        ).scalars().all()
        if not rows:
            return []
        q_ids = list(rows)
        questions = session.execute(
            select(Question).where(Question.id.in_(q_ids))
        ).scalars().all()
        topic_by_id = {q.id: q.topic for q in questions}
        return [topic_by_id[qid] for qid in q_ids if qid in topic_by_id]


def get_best_send_hours(user_id: int, top_n: int = 3) -> list[int]:
    with get_session() as session:
        rows = session.execute(
            select(UserActivity)
            .where(UserActivity.user_id == user_id)
            .order_by(UserActivity.response_rate.desc())
            .limit(top_n)
        ).scalars().all()

    return [row.hour_of_day for row in rows]


# ---------------------------------------------------------------------------
# Stats query
# ---------------------------------------------------------------------------

def get_user_stats(user_id: int) -> dict:
    scores = get_topic_scores(user_id)
    return {
        s.topic: {
            "correct": s.correct,
            "total": s.total,
            "accuracy": round(s.correct / s.total, 3) if s.total else 0.0,
        }
        for s in scores
    }
