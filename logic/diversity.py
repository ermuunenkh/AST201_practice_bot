from collections import deque

import db.queries as queries


class TopicWindow:
    def __init__(self, user_id: int, window_size: int = 5):
        self.user_id = user_id
        self.window_size = window_size
        self._window: deque[str] = deque(maxlen=window_size)
        self._load_from_db()

    def _load_from_db(self) -> None:
        recent = queries.get_recent_send_topics(self.user_id, limit=self.window_size)
        for topic in recent:
            self._window.append(topic)

    def recently_sent_topics(self) -> list[str]:
        return list(self._window)

    def is_topic_overused(self, topic: str) -> bool:
        return self._window.count(topic) > 2

    def record_sent(self, topic: str) -> None:
        self._window.append(topic)


def get_eligible_topics(user_id: int, all_topics: list[str]) -> list[str]:
    window = TopicWindow(user_id)
    eligible = [t for t in all_topics if not window.is_topic_overused(t)]
    if len(eligible) < 2:
        return all_topics
    return eligible


def should_repeat_question(question_id: str, user_id: int, min_days: int = 3) -> bool:
    eligible = queries.get_questions_not_asked_recently(user_id, days=min_days)
    eligible_ids = {q.id for q in eligible}
    return question_id in eligible_ids
