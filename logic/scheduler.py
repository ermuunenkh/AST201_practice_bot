from datetime import datetime, timedelta, timezone
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler

import config
import db.queries as queries
from logic.question_picker import pick_question
from logs.logger import BotLogger  # STUB if not yet built


def build_scheduler(application) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        daily_question_job,
        trigger="interval",
        hours=config.SCHEDULER_INTERVAL_HOURS,
        args=[application],
        id="daily_question_job",
        replace_existing=True,
    )
    return scheduler


async def daily_question_job(application) -> None:
    from bot.sender import send_question  # STUB: imported here to avoid circular import

    users = queries.get_all_active_users()
    current_hour = datetime.now(timezone.utc).hour

    for user in users:
        try:
            best_hours = queries.get_best_send_hours(user.chat_id)

            if best_hours:
                activity = _get_hour_response_rate(user.chat_id, current_hour)
                if activity is not None and activity < config.MIN_RESPONSE_RATE_THRESHOLD:
                    BotLogger.info(
                        f"Skipping {user.name} at hour {current_hour} "
                        f"(response_rate={activity:.2f})"
                    )
                    continue

                if current_hour not in best_hours:
                    continue

            question = pick_question(user.chat_id)
            if question is None:
                BotLogger.info(f"No question available for {user.name}")
                continue

            await send_question(application.bot, user.chat_id, question)
            BotLogger.info(f"Sent question {question['id']} to {user.name}")

        except Exception as exc:
            BotLogger.error(f"daily_question_job failed for user {user.chat_id}: {exc}")


def _get_hour_response_rate(user_id: int, hour: int) -> Optional[float]:
    from sqlalchemy import select
    from db.database import get_session
    from db.models import UserActivity

    with get_session() as session:
        row = session.execute(
            select(UserActivity).where(
                UserActivity.user_id == user_id,
                UserActivity.hour_of_day == hour,
            )
        ).scalar_one_or_none()
    return row.response_rate if row else None


def get_next_send_time(user_id: int) -> Optional[datetime]:
    best_hours = queries.get_best_send_hours(user_id, top_n=3)
    if not best_hours:
        return None

    now = datetime.now(timezone.utc)
    for delta_days in range(2):
        candidate_day = now + timedelta(days=delta_days)
        for hour in sorted(best_hours):
            candidate = candidate_day.replace(hour=hour, minute=0, second=0, microsecond=0)
            if candidate > now:
                return candidate
    return None


def update_activity_after_answer(
    user_id: int,
    asked_at: datetime,
    answered_at: datetime,
) -> None:
    hour = asked_at.hour
    dow = asked_at.weekday()
    response_time_sec = (answered_at - asked_at).total_seconds()
    queries.update_user_activity(
        user_id=user_id,
        hour=hour,
        dow=dow,
        response_time_sec=response_time_sec,
        did_respond=True,
    )
