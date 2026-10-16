#!/usr/bin/env bash
# start-local.sh — one command to open the TAO Authoring Product Workspace
# locally (overnight QA, Phase 6 acceptance).
#
#   ./start-local.sh              → starts DB (if needed) + app, prints URL
#   ./start-local.sh --no-browser don't try to open a browser
#
# Behaviour:
#   1. checks Docker availability;
#   2. starts the PostgreSQL container if it is not running;
#   3. checks schema migrations — upgrades ONLY if behind (never re-imports
#      or overwrites existing data);
#   4. starts the application on http://127.0.0.1:8080;
#   5. reports startup failures with the last log lines.
set -euo pipefail
cd "$(dirname "$0")"

APP_PORT="${APP_PORT:-8080}"
DB_PORT="${DB_PORT:-54323}"
DB_NAME="${DB_NAME:-tao_authoring}"
VENV=".venv"
PYTHON="$VENV/bin/python"
[ -x "$PYTHON" ] || PYTHON=python3
URL="http://127.0.0.1:${APP_PORT}"

fail() { echo "STARTUP FAILED: $1" >&2; exit 1; }

echo "== 1/5 Docker =="
if ! command -v docker > /dev/null 2>&1; then
  fail "Docker is not installed. Install Docker (or colima: 'brew install colima docker && colima start'), then re-run."
fi
if ! docker info > /dev/null 2>&1; then
  echo "Docker daemon not reachable — attempting 'colima start' (macOS)…"
  if command -v colima > /dev/null 2>&1; then colima start || fail "could not start colima"; fi
  docker info > /dev/null 2>&1 || fail "Docker daemon is not running. Start Docker Desktop / colima, then re-run."
fi
echo "Docker OK."

echo "== 2/5 PostgreSQL container =="
# compose is idempotent: creates on first run, starts if stopped, no-op if up
if docker compose up -d db 2>/dev/null; then
  echo "compose db service up."
else
  fail "could not start the DB via docker compose (see docker compose logs db)"
fi
DB_CID=$(docker compose ps -q db)
[ -n "$DB_CID" ] || fail "DB container not found after compose up"
for i in $(seq 1 30); do
  if docker exec "$DB_CID" pg_isready -U tao > /dev/null 2>&1; then break; fi
  [ "$i" = 30 ] && fail "PostgreSQL did not become ready in 15s (docker compose logs db)"
  sleep 0.5
done
echo "PostgreSQL ready on port ${DB_PORT}."

echo "== 3/5 Python environment + migrations =="
[ -x "$VENV/bin/python" ] || { echo "creating venv + installing requirements (first run)…"; python3 -m venv "$VENV"; "$VENV/bin/pip" install -q -r requirements.txt alembic==1.20.0 psycopg==3.3.6; }
export DATABASE_URL="postgresql+psycopg://tao:tao_dev_password@localhost:${DB_PORT}/${DB_NAME}"
"$PYTHON" - <<'PYEOF'
import os, sys
import psycopg
url = os.environ["DATABASE_URL"].replace("postgresql+psycopg://", "postgresql://")
with psycopg.connect(url, autocommit=True) as c, c.cursor() as cur:
    cur.execute("SELECT 1 FROM information_schema.tables WHERE table_name='alembic_version'")
    has = cur.fetchone() is not None
    if not has:
        print("schema: EMPTY database — migrations will be applied (no canonical data yet; run scripts/import/import_canonical.py to load it)")
    else:
        print("schema: present — migration check continues outside")
PYEOF
"$PYTHON" -m alembic upgrade head || fail "alembic upgrade head failed (see message above)"

echo "== 4/5 application =="
if lsof -ti ":${APP_PORT}" > /dev/null 2>&1; then
  echo "Port ${APP_PORT} is busy — assuming the app is already running."
  echo "URL: ${URL}"
  exit 0
fi
LOG="/tmp/tao-authoring-local.log"
DATABASE_URL="$DATABASE_URL" APP_ENV=local LOG_FORMAT=text \
  nohup "$PYTHON" -m uvicorn app.main:app --host 127.0.0.1 --port "$APP_PORT" \
  > "$LOG" 2>&1 &
APP_PID=$!
for i in $(seq 1 40); do
  if curl -sf "${URL}/health" > /dev/null 2>&1; then break; fi
  if ! kill -0 "$APP_PID" 2>/dev/null; then
    echo "--- last log lines:"; tail -15 "$LOG"
    fail "application process exited during startup"
  fi
  [ "$i" = 40 ] && { echo "--- last log lines:"; tail -15 "$LOG"; fail "application did not become healthy in 20s"; }
  sleep 0.5
done

echo "== 5/5 ready =="
DB=$(curl -sf "${URL}/health/db" || echo '{"database":false}')
echo "URL:        ${URL}"
echo "DB check:   $DB"
echo "App PID:    $APP_PID (log: $LOG; stop with: kill $APP_PID)"
[ "${1:-}" = "--no-browser" ] || (open "$URL" 2>/dev/null || xdg-open "$URL" 2>/dev/null || true) && true
echo "Open ${URL} in a browser if it did not open automatically."
