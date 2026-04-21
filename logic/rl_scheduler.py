import json
import random
from pathlib import Path


_BANDIT_DIR = Path("data/models")
_ALPHA = 0.1
_EPSILON = 0.15


class HourBandit:
    def __init__(self, user_id: int):
        self.user_id = user_id
        self._path = _BANDIT_DIR / f"{user_id}_bandit.json"
        self._q: dict[int, float] = self.load()

    def select_hour(self) -> int:
        if random.random() < _EPSILON:
            return random.randint(0, 23)
        return max(self._q, key=lambda h: self._q[h])

    def update(self, hour: int, reward: float) -> None:
        current = self._q.get(hour, 0.0)
        self._q[hour] = current + _ALPHA * (reward - current)
        self.save()

    def save(self) -> None:
        _BANDIT_DIR.mkdir(parents=True, exist_ok=True)
        with open(self._path, "w") as f:
            json.dump({str(k): v for k, v in self._q.items()}, f)

    def load(self) -> dict[int, float]:
        if self._path.exists():
            with open(self._path) as f:
                raw = json.load(f)
            return {int(k): v for k, v in raw.items()}
        return {h: 0.0 for h in range(24)}
