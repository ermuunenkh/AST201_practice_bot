import random
from typing import Optional

import db.queries as queries
from db.models import Question, TopicScore
from logic.diversity import TopicWindow, get_eligible_topics, should_repeat_question
from logs.logger import BotLogger  # STUB if not yet built


def _question_to_dict(q: Question) -> dict:
    import json
    return {
        "id": q.id,
        "topic": q.topic,
        "subtopic": q.subtopic,
        "type": q.q_type,
        "difficulty": q.difficulty,
        "text": q.text,
        "choices": json.loads(q.choices_json) if q.choices_json else [],
        "answer": q.answer,
        "explanation": q.explanation,
        "image": q.image_path,
    }


def weighted_topic_select(topic_scores: list[TopicScore]) -> str:
    topics, weights = [], []
    for s in topic_scores:
        if s.total < 3:
            w = 0.5
        else:
            accuracy = s.correct / s.total
            w = max(1.0 - accuracy, 0.05)
        topics.append(s.topic)
        weights.append(w)
    return random.choices(topics, weights=weights, k=1)[0]


def pick_question(user_id: int, topic_override: Optional[str] = None) -> Optional[dict]:
    if topic_override:
        topic = topic_override
        return _pick_from_topic(user_id, topic)

    scores = queries.get_topic_scores(user_id)
    total_attempts = sum(s.total for s in scores)

    if total_attempts < 15 or not scores:
        unseen = queries.get_unseen_questions(user_id, limit=1)
        if unseen:
            return _question_to_dict(unseen[0])
        return _fallback_random(user_id)

    all_topics = [s.topic for s in scores]
    eligible_topics = get_eligible_topics(user_id, all_topics)
    eligible_scores = [s for s in scores if s.topic in set(eligible_topics)]

    for _ in range(3):
        topic = weighted_topic_select(eligible_scores if eligible_scores else scores)
        window = TopicWindow(user_id)
        if not window.is_topic_overused(topic):
            result = _pick_from_topic(user_id, topic)
            if result:
                return result

    return _fallback_random(user_id)


def _pick_from_topic(user_id: int, topic: str) -> Optional[dict]:
    unseen = queries.get_unseen_questions(user_id, topic=topic, limit=10)
    if unseen:
        return _question_to_dict(random.choice(unseen))

    spaced = queries.get_questions_not_asked_recently(user_id, days=3)
    topic_spaced = [q for q in spaced if q.topic == topic]
    if topic_spaced:
        return _question_to_dict(random.choice(topic_spaced))

    all_topic = queries.get_questions_by_topic(topic, limit=20)
    if all_topic:
        return _question_to_dict(random.choice(all_topic))

    return None


def _fallback_random(user_id: int) -> Optional[dict]:
    all_topics = queries.get_all_topics()
    if not all_topics:
        return None
    topic = random.choice(all_topics)
    all_q = queries.get_questions_by_topic(topic, limit=20)
    return _question_to_dict(random.choice(all_q)) if all_q else None


def pick_batch(user_id: int, n: int) -> list[dict]:
    window = TopicWindow(user_id)
    seen_ids: set[str] = set()
    results: list[dict] = []

    for _ in range(n * 2):
        if len(results) >= n:
            break
        q = pick_question(user_id)
        if q is None:
            break
        if q["id"] in seen_ids:
            continue
        seen_ids.add(q["id"])
        window.record_sent(q["topic"])
        results.append(q)

    return results


if __name__ == "__main__":
    from db.models import TopicScore

    mock_scores = [
        TopicScore(user_id=0, topic="Stellar Evolution", correct=3, total=10),
        TopicScore(user_id=0, topic="Cosmology", correct=8, total=10),
        TopicScore(user_id=0, topic="Planetary Science", correct=2, total=5),
    ]

    print("weighted_topic_select dry-run:")
    for _ in range(5):
        print(" →", weighted_topic_select(mock_scores))
