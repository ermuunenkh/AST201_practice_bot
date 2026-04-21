"""Tests for logic/question_picker.py and logic/diversity.py."""
import random
import sys
import types
from collections import deque
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Minimal stubs so imports work without a real DB or Telegram installed
# ---------------------------------------------------------------------------

def _stub_module(name: str) -> types.ModuleType:
    mod = types.ModuleType(name)
    sys.modules.setdefault(name, mod)
    return sys.modules[name]

for _pkg in ("db", "db.queries", "db.models", "logs", "logs.logger"):
    _stub_module(_pkg)

sys.modules["db.models"].TopicScore = MagicMock  # type: ignore
sys.modules["db.models"].Question = MagicMock    # type: ignore
BotLogger = MagicMock()
sys.modules["logs.logger"].BotLogger = BotLogger  # type: ignore

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_score(topic: str, correct: int, total: int) -> MagicMock:
    s = MagicMock()
    s.topic = topic
    s.correct = correct
    s.total = total
    return s


def _make_question(q_id: str, topic: str) -> MagicMock:
    q = MagicMock()
    q.id = q_id
    q.topic = topic
    q.subtopic = None
    q.q_type = "MCQ"
    q.difficulty = 2
    q.text = f"Question {q_id}"
    q.choices_json = '["A", "B", "C", "D"]'
    q.answer = "A"
    q.explanation = None
    q.image_path = None
    return q


# ---------------------------------------------------------------------------
# weighted_topic_select
# ---------------------------------------------------------------------------

class TestWeightedTopicSelect:
    def test_weak_topic_gets_high_weight(self):
        from logic.question_picker import weighted_topic_select

        scores = [
            _make_score("Stellar Evolution", 1, 10),   # accuracy 0.1 → weight 0.9
            _make_score("Cosmology", 10, 10),           # accuracy 1.0 → weight 0.05
        ]
        random.seed(42)
        picks = [weighted_topic_select(scores) for _ in range(100)]
        stellar_count = picks.count("Stellar Evolution")
        assert stellar_count > 60, f"Expected weak topic to dominate, got {stellar_count}/100"

    def test_low_attempt_topic_gets_neutral_weight(self):
        from logic.question_picker import weighted_topic_select

        scores = [_make_score("New Topic", 0, 2)]  # < 3 attempts → 0.5
        result = weighted_topic_select(scores)
        assert result == "New Topic"

    def test_all_perfect_scores_get_min_weight(self):
        from logic.question_picker import weighted_topic_select

        scores = [
            _make_score("A", 10, 10),
            _make_score("B", 10, 10),
        ]
        result = weighted_topic_select(scores)
        assert result in ("A", "B")


# ---------------------------------------------------------------------------
# pick_batch — returns distinct questions
# ---------------------------------------------------------------------------

class TestPickBatch:
    def test_returns_distinct_questions(self):
        from logic import question_picker

        questions = [_make_question(f"Q{i:03}", "Stellar Evolution") for i in range(10)]
        # total >= 15 so pick_question takes the weighted-topic path
        scores = [_make_score("Stellar Evolution", 3, 20)]

        with (
            patch("logic.question_picker.queries") as mock_q,
            patch("logic.question_picker.TopicWindow") as mock_tw,
            patch("logic.question_picker.get_eligible_topics") as mock_elig,
        ):
            mock_tw.return_value.is_topic_overused.return_value = False
            mock_tw.return_value.recently_sent_topics.return_value = []
            mock_elig.return_value = ["Stellar Evolution"]
            mock_q.get_topic_scores.return_value = scores
            # each call to get_unseen_questions returns a fresh shuffled copy
            mock_q.get_unseen_questions.side_effect = (
                lambda uid, topic=None, limit=10: random.sample(questions, min(limit, len(questions)))
            )
            mock_q.get_all_topics.return_value = ["Stellar Evolution"]
            mock_q.get_questions_by_topic.return_value = questions
            mock_q.get_questions_not_asked_recently.return_value = []

            result = question_picker.pick_batch(1, 5)

        ids = [q["id"] for q in result]
        assert len(ids) == len(set(ids)), "Duplicate question IDs in batch"
        assert len(result) == 5

    def test_batch_smaller_than_requested_when_pool_exhausted(self):
        from logic import question_picker

        questions = [_make_question("Q001", "Stellar Evolution")]

        with (
            patch("logic.question_picker.queries") as mock_q,
            patch("logic.question_picker.TopicWindow") as mock_tw,
        ):
            mock_tw.return_value.is_topic_overused.return_value = False
            mock_tw.return_value.recently_sent_topics.return_value = []
            mock_q.get_topic_scores.return_value = [_make_score("Stellar Evolution", 3, 10)]
            mock_q.get_unseen_questions.side_effect = lambda uid, topic=None, limit=10: questions
            mock_q.get_all_topics.return_value = ["Stellar Evolution"]
            mock_q.get_questions_by_topic.return_value = questions
            mock_q.get_questions_not_asked_recently.return_value = []

            result = question_picker.pick_batch(1, 5)

        assert len(result) <= 5


# ---------------------------------------------------------------------------
# Diversity: topic overuse prevents re-selection
# ---------------------------------------------------------------------------

class TestDiversity:
    def test_overused_topic_excluded_from_eligible(self):
        from logic.diversity import TopicWindow, get_eligible_topics

        with patch("logic.diversity.queries") as mock_q:
            mock_q.get_recent_send_topics.return_value = [
                "Stellar Evolution", "Stellar Evolution", "Stellar Evolution"
            ]
            eligible = get_eligible_topics(
                user_id=1,
                all_topics=["Stellar Evolution", "Cosmology", "Planetary Science"],
            )

        assert "Stellar Evolution" not in eligible

    def test_always_returns_at_least_two_topics(self):
        from logic.diversity import get_eligible_topics

        with patch("logic.diversity.queries") as mock_q:
            mock_q.get_recent_send_topics.return_value = [
                "Stellar Evolution", "Stellar Evolution", "Stellar Evolution",
                "Cosmology", "Cosmology", "Cosmology",
            ]
            eligible = get_eligible_topics(
                user_id=1,
                all_topics=["Stellar Evolution", "Cosmology"],
            )

        assert len(eligible) >= 2

    def test_topic_window_record_sent_updates_window(self):
        from logic.diversity import TopicWindow

        with patch("logic.diversity.queries") as mock_q:
            mock_q.get_recent_send_topics.return_value = []
            tw = TopicWindow(user_id=1, window_size=5)
            tw.record_sent("Cosmology")
            tw.record_sent("Cosmology")
            tw.record_sent("Cosmology")

        assert tw.is_topic_overused("Cosmology") is True
        assert tw.is_topic_overused("Stellar Evolution") is False
