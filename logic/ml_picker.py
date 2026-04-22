import random
import numpy as np
import pandas as pd
from datetime import datetime, timezone


def _compute_features(df: pd.DataFrame) -> pd.DataFrame:
    """Returns one row per subtopic with features: accuracy, days_since_last,
    attempt_count, recent_accuracy (last 5 attempts)."""
    now = datetime.now(tz=timezone.utc)
    df = df.copy()
    df["answered_at"] = pd.to_datetime(df["answered_at"], utc=True)

    rows = []
    for subtopic, group in df.groupby("sub_topic"):
        group = group.sort_values("answered_at")
        attempts = len(group)
        accuracy = group["is_correct"].mean()
        days_since = (now - group["answered_at"].iloc[-1]).total_seconds() / 86400
        recent = group.tail(5)["is_correct"].mean()
        rows.append({
            "sub_topic":      subtopic,
            "accuracy":       accuracy,
            "days_since_last": days_since,
            "attempt_count":  attempts,
            "recent_accuracy": recent,
        })
    return pd.DataFrame(rows)


def _softmax(x: np.ndarray) -> np.ndarray:
    e = np.exp(x - x.max())
    return e / e.sum()


def ml_pick(df: pd.DataFrame, question_pool: list[dict]) -> dict:
    """Pick the question whose subtopic scores highest on weakness."""
    from sklearn.preprocessing import StandardScaler

    features_df = _compute_features(df)
    if features_df.empty:
        return random.choice(question_pool)

    X = features_df[["accuracy", "days_since_last", "attempt_count", "recent_accuracy"]].values
    if len(features_df) > 1:
        X = StandardScaler().fit_transform(X)

    # Higher weight → more "weak" signal
    weights = np.array([-0.4, 0.3, 0.0, -0.3])  # accuracy↓, stale↑, recent_accuracy↓
    scores = X @ weights
    probs = _softmax(scores)

    chosen_subtopic = features_df["sub_topic"].iloc[
        np.random.choice(len(features_df), p=probs)
    ]

    candidates = [q for q in question_pool if q["sub_topic"] == chosen_subtopic]
    return random.choice(candidates) if candidates else random.choice(question_pool)
