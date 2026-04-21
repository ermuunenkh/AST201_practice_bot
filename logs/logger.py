import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

_LOG_DIR = Path("logs")
_LOG_DIR.mkdir(exist_ok=True)

_handler = RotatingFileHandler(
    _LOG_DIR / "astrobot.log",
    maxBytes=5 * 1024 * 1024,
    backupCount=3,
)
_handler.setFormatter(
    logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
)

_console = logging.StreamHandler()
_console.setFormatter(logging.Formatter("%(levelname)s | %(name)s | %(message)s"))


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        logger.addHandler(_handler)
        logger.addHandler(_console)
        logger.propagate = False
    return logger


BotLogger = get_logger("astrobot")
