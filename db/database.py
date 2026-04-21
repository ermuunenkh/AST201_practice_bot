import json
import logging
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from config import DB_PATH
from db.models import Base, Question

DATABASE_URL = f"sqlite:///{DB_PATH}"
QUESTIONS_JSON = "data/questions/astronomy_questions.json"

logger = logging.getLogger(__name__)

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)

_SessionFactory = sessionmaker(bind=engine, expire_on_commit=False)


@contextmanager
def get_session() -> Generator[Session, None, None]:
    session = _SessionFactory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def load_questions_from_json(path: str = QUESTIONS_JSON) -> int:
    with open(path, "r", encoding="utf-8") as f:
        questions = json.load(f)

    loaded = 0
    with get_session() as session:
        for q in questions:
            exists = session.get(Question, q["id"])
            if exists:
                continue
            choices = q.get("choices")
            session.add(
                Question(
                    id=q["id"],
                    topic=q["topic"],
                    subtopic=q.get("subtopic"),
                    q_type=q["type"],
                    difficulty=q.get("difficulty", 2),
                    text=q["text"],
                    choices_json=json.dumps(choices) if choices else None,
                    answer=q["answer"],
                    explanation=q.get("explanation"),
                    image_path=q.get("image"),
                )
            )
            loaded += 1

    logger.info("Loaded %d new questions from %s", loaded, path)
    return loaded


def init_db() -> None:
    Base.metadata.create_all(engine)
    logger.info("Database tables created (or already exist).")

    with get_session() as session:
        count = session.execute(select(Question)).scalars().first()

    if count is None:
        loaded = load_questions_from_json()
        logger.info("Seeded question pool with %d questions.", loaded)
    else:
        logger.info("Question pool already seeded; skipping JSON load.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    init_db()

    with get_session() as session:
        from sqlalchemy import func, select as sa_select
        from db.models import Question as Q

        total = session.execute(sa_select(func.count()).select_from(Q)).scalar()
        topics = session.execute(sa_select(Q.topic).distinct()).scalars().all()

    print(f"Questions loaded: {total}")
    print(f"Topics found: {sorted(topics)}")
