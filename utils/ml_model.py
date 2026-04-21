import os
import logging
import joblib
import numpy as np
from sklearn.linear_model import LogisticRegression

logger = logging.getLogger(__name__)

MODEL_DIR = "data/models"


class DifficultyModel:
    def __init__(self, model_path: str = f"{MODEL_DIR}/difficulty_model.pkl"):
        self.model_path = model_path
        self.model: LogisticRegression | None = None
        self.is_trained = False
        self._trained_on = 0
        os.makedirs(MODEL_DIR, exist_ok=True)

    def _to_feature_matrix(self, answers: list[dict]) -> np.ndarray:
        rows = []
        for a in answers:
            rows.append([
                a.get("difficulty", 2),
                a.get("user_overall_accuracy", 0.5),
                a.get("user_topic_accuracy", 0.5),
                a.get("hour_of_day", 12),
                a.get("attempt_number", 1),
            ])
        return np.array(rows, dtype=float)

    def train(self, answers: list[dict]) -> None:
        if len(answers) < 30:
            logger.info("Not enough data to train (%d samples, need ≥30).", len(answers))
            return

        X = self._to_feature_matrix(answers)
        y = np.array([int(a["is_correct"]) for a in answers])

        self.model = LogisticRegression(max_iter=200, random_state=42)
        self.model.fit(X, y)
        self.is_trained = True
        self._trained_on = len(answers)

        train_acc = self.model.score(X, y) * 100
        logger.info("Model trained on %d samples, accuracy: %.1f%%", len(answers), train_acc)
        joblib.dump(self.model, self.model_path)

    def predict_difficulty(self, features: dict) -> float:
        if not self.is_trained:
            return 0.5
        X = self._to_feature_matrix([features])
        prob_correct = self.model.predict_proba(X)[0][1]
        return float(prob_correct)

    def load(self) -> None:
        if os.path.exists(self.model_path):
            self.model = joblib.load(self.model_path)
            self.is_trained = True
            logger.info("Loaded difficulty model from %s", self.model_path)

    def should_retrain(self, answers: list) -> bool:
        return len(answers) - self._trained_on > 20
