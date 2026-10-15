"""Database connectivity — SQLAlchemy engine over Cloud SQL-compatible URL.

Cloud SQL notes (§15/§27):
- Connection URL always from DATABASE_URL (Postgres on Cloud SQL via
  unix socket or TCP, e.g.
  postgresql+psycopg://user:pass@/db?host=/cloudsql/PROJECT:REGION:INSTANCE).
- Fail fast and clearly when DB connectivity is unavailable.
"""

import os

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from .config import settings

_engine: Engine | None = None


def engine() -> Engine:
    global _engine
    if _engine is None:
        if not settings.database_url:
            raise RuntimeError("DATABASE_URL is not configured")
        _engine = create_engine(
            settings.database_url,
            pool_pre_ping=True,
            pool_size=int(os.environ.get("DB_POOL_SIZE", "5")),
            max_overflow=5,
        )
    return _engine


def ping() -> bool:
    try:
        with engine().connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
