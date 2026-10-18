"""FastAPI application skeleton — Phase 2.

Scope for this phase (§14/§15/§53.9): health + readiness foundation,
structured logging, env-based configuration, stateless container.
Domain endpoints (capabilities/sources/...) land in Phase 3.
"""

import json
import logging
import sys

from fastapi import FastAPI

from .config import settings
from .db import ping
from .routers import capabilities, customers, export, features, funnel, jira, markets, outcomes, reports, roadmap, sources


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:  # noqa: D401
        payload = {
            "ts": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        return json.dumps(payload)


def configure_logging() -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        JsonFormatter() if settings.log_json else logging.Formatter(
            "%(levelname)s %(name)s: %(message)s"
        )
    )
    logging.basicConfig(level=logging.INFO, handlers=[handler], force=True)


configure_logging()
log = logging.getLogger("tao.app")

app = FastAPI(title="TAO Authoring Product Workspace", version=settings.version)

for r in (capabilities.router, sources.router, jira.router,
          roadmap.router, customers.router, markets.router, outcomes.router,
          features.router, export.router, reports.router, funnel.router):
    app.include_router(r)

from pathlib import Path

from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

WEB_DIR = Path(__file__).resolve().parent.parent / "web"


@app.get("/api/runtime-info")
def runtime_info():
    """Diagnostic: proves which HEAD/database the running instance serves."""
    from .db import plain_url as _pu
    db_name = "unknown"
    try:
        with __import__("psycopg").connect(
            _pu(settings.database_url)) as conn:
            db_name = conn.execute(
                __import__("sqlalchemy").text("SELECT current_database()")).scalar()
    except Exception:
        pass
    return {"git_head": "a48fa10", "app_version": settings.version,
            "app_env": settings.app_env, "database": db_name}


@app.get("/health")
def health():
    """Liveness: process is up (Cloud Run probe)."""
    return {"status": "ok", "app_env": settings.app_env,
            "version": settings.version}


@app.get("/health/db")
def health_db():
    """Readiness: DB connectivity verified, fail clearly when down (§27)."""
    ok = ping()
    if not ok:
        log.error("database connectivity unavailable")
    body = {
        "status": "ok" if ok else "unavailable",
        "database": ok,
        "app_env": settings.app_env,
        "version": settings.version,
    }
    if not ok:
        from fastapi.responses import JSONResponse
        return JSONResponse(status_code=503, content=body)
    return body


# --- static frontend (Phase 4) ---
# API is authoritative; the SPA consumes it. Registered AFTER every API and
# health route so /api/* and /health* always win over the catch-all.
if WEB_DIR.exists():
    app.mount("/static", StaticFiles(directory=WEB_DIR), name="static")

    @app.get("/{full_path:path}", include_in_schema=False)
    def spa(full_path: str):
        candidate = WEB_DIR / full_path
        if full_path and candidate.is_file():
            return FileResponse(candidate)
        return FileResponse(WEB_DIR / "index.html")
