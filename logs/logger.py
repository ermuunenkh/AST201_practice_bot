import logging
import logging.handlers
from pathlib import Path

_LOG_FILE = Path("logs/astrobot.log")
_LOG_FILE.parent.mkdir(exist_ok=True)

_handler = logging.handlers.RotatingFileHandler(
    _LOG_FILE, maxBytes=200_000, backupCount=3, encoding="utf-8"
)
_handler.setFormatter(logging.Formatter(
    "%(asctime)s | %(levelname)-5s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
))

_logger = logging.getLogger("astrobot")
_logger.setLevel(logging.DEBUG)
_logger.addHandler(_handler)


def log(message: str, level: str = "info") -> None:
    getattr(_logger, level.lower())(message)
