#!/usr/bin/env bash
# Deployment-readiness pipeline (Phase 6, contract §2/§4):
#   empty database → Alembic migrations → canonical import → validation
#   → application boot + smoke.
#
# Used by CI (see .github/workflows/ci.yml) and by DATA_OPERATIONS_RUNBOOK.md
# to prove any Cloud SQL instance can be brought up from zero.
#
# Env (all optional; defaults target the local docker-compose database):
#   PIPELINE_ADMIN_URL   admin connection that may CREATE/DROP the scratch DB
#   PIPELINE_DB_NAME     scratch database name (dropped at the end unless SKIP_DROP=1)
#   PIPELINE_DB_URL      full scratch database URL (overrides PIPELINE_DB_NAME)
#   SKIP_DROP=1          keep the scratch database after the run (debugging)
set -euo pipefail
cd "$(dirname "$0")/../.."

PYTHON="${PYTHON:-.venv/bin/python}"
[ -x "$PYTHON" ] || PYTHON=python3

ADMIN_URL="${PIPELINE_ADMIN_URL:-postgresql://tao:tao_dev_password@localhost:54323/postgres}"
SCRATCH_DB="${PIPELINE_DB_NAME:-tao_authoring_pipeline}"
DB_URL="${PIPELINE_DB_URL:-postgresql://tao:tao_dev_password@localhost:54323/${SCRATCH_DB}}"
PSYCOPG_URL="$($PYTHON -c "import sys; u=sys.argv[1]; print(u.replace('postgresql://', 'postgresql+psycopg://', 1) if u.startswith('postgresql://') else u)" "$DB_URL")"
APP_PID=""

cleanup() {
  if [ -n "$APP_PID" ]; then kill "$APP_PID" 2>/dev/null || true; fi
  if [ "${SKIP_DROP:-0}" != "1" ]; then
    "$PYTHON" - "$ADMIN_URL" "$SCRATCH_DB" <<'PYEOF' 2>/dev/null || true
import sys, psycopg
with psycopg.connect(sys.argv[1], autocommit=True) as c:
    c.execute('DROP DATABASE IF EXISTS "' + sys.argv[2] + '"')
print("dropped", sys.argv[2])
PYEOF
  fi
}
trap cleanup EXIT

echo "== 1/6 scratch database from empty =="
"$PYTHON" - "$ADMIN_URL" "$SCRATCH_DB" <<'PYEOF'
import sys, psycopg
admin, db = sys.argv[1], sys.argv[2]
with psycopg.connect(admin, autocommit=True) as c:
    c.execute(f'DROP DATABASE IF EXISTS "{db}"')
    c.execute(f'CREATE DATABASE "{db}"')
print("created", db)
PYEOF

echo "== 2/6 Alembic migrations on empty database =="
DATABASE_URL="$PSYCOPG_URL" "$PYTHON" -m alembic upgrade head

echo "== 3/6 canonical import + governed bootstrap =="
DATABASE_URL="$PSYCOPG_URL" "$PYTHON" scripts/import/import_canonical.py \
  > /tmp/pipeline_import.json
DATABASE_URL="$PSYCOPG_URL" "$PYTHON" scripts/import/import_milestones.py > /dev/null
DATABASE_URL="$PSYCOPG_URL" "$PYTHON" scripts/import/materialize_source_documents.py > /dev/null
DATABASE_URL="$PSYCOPG_URL" "$PYTHON" scripts/import/ingest_source_analysis.py \
  data/source-analysis/v1_4 > /dev/null
echo "governed bootstrap: 9 sources, 426 evidence, 34 candidates, 15 focus"
"$PYTHON" - <<'PYEOF'
import json
s = json.load(open("/tmp/pipeline_import.json"))
print("import ok:", s.get("skipped_conflicts", {}).get("capabilities", "?"), "capability conflicts skipped")
PYEOF

echo "== 4/6 import validation =="
DATABASE_URL="$PSYCOPG_URL" "$PYTHON" scripts/import/validate_import.py \
  > /tmp/pipeline_validate.json
"$PYTHON" - <<'PYEOF'
import json
rep = json.load(open("/tmp/pipeline_validate.json"))
assert rep["summary"]["fail"] == 0, f"validation FAILED: {rep['summary']}"
print(f"validation: {rep['summary']['pass']} PASS / 0 FAIL")
PYEOF

echo "== 5/6 application boot on the migrated database =="
PORT="${PIPELINE_APP_PORT:-8097}"
DATABASE_URL="$PSYCOPG_URL" APP_ENV=pipeline LOG_FORMAT=text \
  "$PYTHON" -m uvicorn app.main:app --host 127.0.0.1 --port "$PORT" \
  > /tmp/pipeline_uvicorn.log 2>&1 &
APP_PID=$!
for i in $(seq 1 40); do
  if curl -sf "http://127.0.0.1:${PORT}/health" > /dev/null; then break; fi
  if [ "$i" = 40 ]; then echo "app did not become healthy"; tail -20 /tmp/pipeline_uvicorn.log; exit 1; fi
  sleep 0.5
done

echo "== 6/6 smoke =="
curl -sf "http://127.0.0.1:${PORT}/health" | grep -q '"status":"ok"'
curl -sf "http://127.0.0.1:${PORT}/health/db" | grep -q '"database":true'
CAPS=$(curl -sf "http://127.0.0.1:${PORT}/api/capabilities" | "$PYTHON" -c "import sys,json; print(json.load(sys.stdin)['count'])")
FUNNEL=$(curl -sf "http://127.0.0.1:${PORT}/api/funnel" | "$PYTHON" -c "import sys,json; f=json.load(sys.stdin)['funnel']; print(f['sources'],f['evidence_signals'],f['capability_candidates'],f['focus_capabilities'])")
EXPORT=$(curl -sf "http://127.0.0.1:${PORT}/api/export" | "$PYTHON" -c "import sys,json; print(json.load(sys.stdin)['counts']['capabilities'])")
echo "smoke: capabilities=$CAPS funnel=$FUNNEL export_capabilities=$EXPORT"
read GOV_SOURCES GOV_EVIDENCE GOV_CANDIDATES GOV_FOCUS <<< "$FUNNEL"
[ "$CAPS" = "34" ] && [ "$GOV_SOURCES" = "9" ] && [ "$GOV_EVIDENCE" = "426" ] && [ "$GOV_CANDIDATES" = "34" ] && [ "$GOV_FOCUS" = "15" ] && [ "$EXPORT" = "34" ]
echo "== PIPELINE OK: empty → migrated → imported → validated → serving =="
