# Cloud Run-compatible application image (§15/§27).
# Stateless container; all config from env; listens on $PORT.
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY migrations/ ./migrations/
COPY alembic.ini ./alembic.ini

# Non-root runtime user.
RUN useradd -r -u 1000 appuser && chown -R appuser /app
USER appuser

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s \
  CMD wget -qO- "http://127.0.0.1:${PORT:-8080}/health" || exit 1

# Cloud Run injects $PORT; default 8080 for local/container use.
CMD exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8080}"
