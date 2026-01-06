from pathlib import Path
import os
from sqlmodel import create_engine, SQLModel, Session

BASE_DIR = Path(__file__).resolve().parents[1]
DB_FILE = BASE_DIR / "database.db"
# Allow overriding the database URL via env var for tests and deployments.
DATABASE_URL = os.environ.get("DATABASE_URL") or f"sqlite:///{DB_FILE}"

# SQLite engine for the application. `check_same_thread` disabled for typical
# FastAPI single-process usage. `echo=False` to avoid noisy production logs.
engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})


def init_db(url: str | None = None) -> None:
    """Create database tables. If `url` is provided, create a temporary engine for that URL."""
    if url:
        tmp_engine = create_engine(url, echo=False, connect_args={"check_same_thread": False})
        SQLModel.metadata.create_all(tmp_engine)
    else:
        SQLModel.metadata.create_all(engine)


def get_session() -> Session:
    return Session(engine)
