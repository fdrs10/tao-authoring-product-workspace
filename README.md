# TAO Authoring Product Workspace

Repository seed for the multi-user Authoring Product Definition / Roadmap / Migration workspace.

Start with `docs/KINCHI_MASTER_HANDOFF.md`, then `docs/REPOSITORY_BOOTSTRAP.md`, `docs/KNOWN_DEFECTS.md`, and `tests/ACCEPTANCE_CRITERIA.md`.

The `legacy/` HTML is a functional/visual reference, not the architecture to preserve. Canonical data and lineage are under `data/`.

## Local development (Phase 2: PostgreSQL + Alembic + FastAPI)

```bash
# 1. Copy env template
cp .env.example .env

# 2. Start Postgres 16 (docker compose service)
docker compose up -d db

# 3. Export the app URL, then migrate schema
export DATABASE_URL="postgresql+psycopg://tao:tao_dev_password@localhost:54323/tao_authoring"
alembic upgrade head

# 4. Idempotent canonical import (safe to re-run) + validation
python3 scripts/import/import_canonical.py
python3 scripts/import/validate_import.py   # -> data/reports/phase2_import_validation.json

# 5. Run the API
uvicorn app.main:app --port 8080
curl http://127.0.0.1:8080/health && curl http://127.0.0.1:8080/health/db
```

Schema is **migration-managed** (`migrations/` + `alembic.ini`). `db/schema.sql`
remains the frozen handoff seed for reference; from Phase 2 the authoritative
schema is the Alembic baseline `0001_initial_schema`.

Cloud target (Cloud Run + Cloud SQL + Cloud Storage): `docs/CLOUD_ARCHITECTURE.md`.
