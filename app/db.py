"""Database connectivity — Cloud SQL-compatible URL from the environment (§15/§27).

Routers use a psycopg connection per request (dependency ``db_conn``);
health checks use a lightweight SQLAlchemy engine ping. Fail fast and
clearly when DB connectivity is unavailable.
"""

import os
from collections.abc import Iterator

import psycopg
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from .config import settings

_engine: Engine | None = None


def plain_url(url: str) -> str:
    """Accept sqlalchemy-style URLs; psycopg needs the plain form."""
    for prefix in ("postgresql+psycopg://", "postgresql+psycopg2://"):
        if url.startswith(prefix):
            return "postgresql://" + url.split("://", 1)[1]
    return url


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


def db_conn() -> Iterator[psycopg.Connection]:
    """FastAPI dependency: one connection per request, rolled back on error."""
    if not settings.database_url:
        raise RuntimeError("DATABASE_URL is not configured")
    conn = psycopg.connect(plain_url(settings.database_url))
    try:
        yield conn
    finally:
        conn.close()
