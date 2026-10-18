# CLOUD_HANDOFF_CURRENT_HEAD — deployment handoff at the current HEAD

**Date:** 2026-10-16 · **HEAD:** see `git log --oneline -1` (pushed after all corrections) · **Tag:** `dev-candidate-v1.0` = `04f5208` (frozen)

## Verdict: PASS (all gates verified on the current HEAD)

| Gate | Result |
|---|---|
| Docker build | ✔ `docker build -t tao-authoring .` (verified: includes app/ + web/ + migrations/) |
| Empty PostgreSQL → Alembic head | ✔ `alembic upgrade head` from empty (0001→0007, 7 migrations) |
| Governed bootstrap | ✔ import_canonical + milestones + materialize + source-analysis ingestion (9 sources, 426 evidence, 34 candidates, 15 focus, 135 historical) |
| Application container | ✔ `/health` 200, `/health/db` 200, SPA 200, assets 200 |
| Governed funnel via API | ✔ Sources 9+ (incl. historical), Evidence 426, Candidates 34, Focus 15 |
| Ideation / Reports / Roadmap / Migration | ✔ all render without JS errors (§55 guard) |
| Population isolation | ✔ active (34) ≠ historical (135); no union in default views |
| Full regression | ✔ 122 passed |

## Deployment commands

### 1. Build
```bash
docker build -t tao-authoring:latest .
```

### 2. Environment variables (Cloud Run)
| Variable | Value |
|---|---|
| `DATABASE_URL` | `postgresql+psycopg://tao_app:<SECRET>@/tao_authoring?host=/cloudsql/PROJECT:REGION:INSTANCE` |
| `APP_ENV` | `dev` |
| `LOG_FORMAT` | `json` |
| `SOURCE_DOC_BUCKET` | `gs://PROJECT-source-documents` |

### 3. Required secrets
- `DB_PASSWORD` — Cloud SQL user password (Secret Manager)

### 4. Cloud SQL bootstrap (from empty)
```bash
gcloud sql databases create tao_authoring --instance=INSTANCE
# Migrations + governed bootstrap (Cloud Run job or local with proxy):
DATABASE_URL="postgresql+psycopg://tao_app:$DB_PASSWORD@/tao_authoring?host=/cloudsql/…" alembic upgrade head
DATABASE_URL="…" python scripts/import/import_canonical.py
DATABASE_URL="…" python scripts/import/import_milestones.py
DATABASE_URL="…" python scripts/import/materialize_source_documents.py
DATABASE_URL="…" python scripts/import/ingest_source_analysis.py data/source-analysis/v1_4
DATABASE_URL="…" python scripts/import/validate_import.py  # 26 PASS / 0 FAIL
```

### 5. Cloud Run deploy
```bash
gcloud run deploy tao-authoring-dev \
  --image "$IMG" --region "$REGION" --service-account "$RUN_SA" \
  --add-cloudsql-instances "$PROJECT:$REGION:INSTANCE" \
  --set-env-vars "APP_ENV=dev,LOG_FORMAT=json,SOURCE_DOC_BUCKET=gs://…" \
  --set-secrets "DB_PASSWORD=DB_PASSWORD_SECRET:latest" \
  --min-instances 0 --max-instances 2
```

### 6. Post-deployment smoke
```bash
curl "$URL/health"            # 200
curl "$URL/health/db"         # 200 {"database":true}
curl "$URL/api/funnel"        # {"funnel":{"sources":≥9,"evidence_signals":426,"capability_candidates":34,"focus_capabilities":15,…}}
curl "$URL/api/capabilities"  # count = 34 (active population)
curl "$URL/api/reports"       # 5 contracts listed
```

### 7. Rollback
- Application: `gcloud run revisions list` → `gcloud run services update-traffic --to-revisions PREV=100`
- Migration: `alembic downgrade 0006_source_analysis` (safe — drops only enrichment/coverage columns)
- Data: restore from Cloud SQL backup + governed re-import (DATA_OPERATIONS_RUNBOOK)

## External inputs still required (unchanged from PHASE_6_REPORT §9)

1. GCP project ID · 2. Region · 3. Cloud SQL instance decision · 4. IAM/SA + secret policy · 5. DB password secret · 6. DEV ingress policy · 7. (optional) GCS bucket + google-cloud-storage approval
