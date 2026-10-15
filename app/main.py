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
from .routers import capabilities, customers, jira, roadmap, sources


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
          roadmap.router, customers.router):
    app.include_router(r)


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
