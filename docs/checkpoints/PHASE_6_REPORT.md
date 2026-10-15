# Phase 6 Checkpoint — Operational Readiness and DEV Cloud Deployment

**Date:** 2026-10-15 · **Status:** READINESS COMPLETE — actual cloud deployment **blocked only by external GCP inputs** (§9)
**Regression:** 78/78 (26 API + 38 UI + 10 ESM gate + 4 Phase 6) — Phase 1–5 baseline (74) preserved, nothing rewritten.

---

## 1. Cloud Run readiness — validated end-to-end (local proof)

| Constraint | Evidence |
|---|---|
| Stateless container | image contains `app/ + web/ + migrations/ + alembic.ini` only; all config via env (`app/config.py`); no writes to local disk (source-doc artifacts go to the configured external store) |
| `$PORT` | `CMD exec uvicorn … --port "${PORT:-8080}"`; verified with `PORT=8091`/`PORT=8092` |
| Health/readiness | `/health` 200 (liveness, DB-independent); `/health/db` 200/503 with DB ping |
| Graceful DB failures | container smoke with unreachable DB: `/health`=200, `/health/db`=503, SPA=200 |
| Structured logging | `LOG_FORMAT=json` → application log records are JSON on stdout (uvicorn lifecycle lines plain — documented) |
| **No local persistent state** | confirmed; artifacts external via `SOURCE_DOC_*` |

**Defect found & fixed during validation:** the Phase 2 Dockerfile did not copy `web/` — the SPA 404'd inside the container (`/` → 404). Fixed (`COPY web/ ./web/`), rebuilt, re-verified: `/`=200, `/static/js/main.js`=200.

**Live-DB container test:** container run against the dev database via `host.docker.internal` → `/health/db {"database":true}`, `/api/capabilities` count 135, `/api/roadmap?admission=` count 135.

## 2. Cloud SQL readiness — empty→serving pipeline proven

`scripts/ops/pipeline_from_empty.sh` (CI job `migration-import-pipeline` runs it too):
**empty DB → `alembic upgrade head` → canonical import (135, 0 conflicts) → validation (26 PASS / 0 FAIL) → app boot → smoke (135 capabilities via API + `/api/export`)**.
Cloud SQL connection configuration documented (unix-socket URL form) in DEPLOYMENT_RUNBOOK §2/§5. `tests/api/conftest.py` now honours `TEST_ADMIN_URL` for CI portability.

## 3. Source document storage (§3)

`app/docstore.py`: artifact store with two drivers — `LocalDocStore` (dev; tested) and `GcsDocStore` (activates when `SOURCE_DOC_BUCKET` set + optional dependency present; wired at deployment). **Boundary enforced and tested:** PostgreSQL keeps source metadata + lineage; object storage keeps only artifacts (`local://SRC/name` refs today, `gs://…` in cloud). Config keys documented in `.env.example`.

## 4. CI/CD (§4)

`.github/workflows/ci.yml` — five parallel jobs, **any failure blocks deployment**:
1. `api-tests` (Postgres 16 service on 54323; Phase 3/5/6 API suites)
2. `js-esm-gate` (the permanent ESM syntax guard)
3. `migration-import-pipeline` (empty→migrate→import→validate→boot→smoke)
4. `playwright-e2e` (Phase 4+5 UI suites, `--with-deps chromium`)
5. `container-smoke` (build image; assert 200/503/200 under graceful DB failure)

`.github/workflows/deploy.yml` — `workflow_run` after **ci** success on `main`, GitHub Environment `gcp-dev`, hard-fails with a pointer to this report when secrets are absent. **Push-to-deploy is therefore structurally gated on CI.**

## 5. DEV authentication (§5)

Unchanged replaceable abstraction: `X-User-Ref` (default `dev-user`), UI chip for a personal label; Product entities never coupled to it. **Production IdP integration point documented:** `app/identity.py::get_actor` is the single seam — production adds IAP/JWT verification and derives `user_ref` from a verified claim; same `Actor` model, audit, `updated_by` semantics; zero schema impact (DEPLOYMENT_RUNBOOK §6).

## 6. Backup / recovery / portability (§6)

`docs/DATA_OPERATIONS_RUNBOOK.md`: governed export (`/api/export`), Cloud SQL on-demand + scheduled backups, restore into fresh DB + verification checklist, canonical re-import (idempotent, never clobbers), artifact backup/versioning/DR-rsync, safe-vs-rebuild migration rollback rules, portability statement.

## 7. Export (§7) — implemented + tested

`GET /api/export`: all 13 §7 entity groups (MoSCoW/Admission/budgets ride on `capabilities`), deterministic ordering, NULL semantics preserved (`NULL budget ≠ 0`, UNSET distinct). Tests: presence, counts vs the live API surface, NULL round-trip.

## 8. UAT readiness (§9)

`docs/PRODUCT_UAT_GUIDE.md`: getting started (identity chip), workflow walk-through Sources → Ideation → Cross-analysis → Backlog → Admission → Roadmap → Migration, 18-point compact UAT checklist with expectations, honest limitations (D2/D3/identity).

## 9. External inputs required to execute the actual deployment (§8)

Nothing was invented; deployment stops exactly here until Product/IT supply:

| # | Required input | Used for |
|---|---|---|
| 1 | **GCP project ID** (DEV) | `gcloud config set project`, Artifact Registry paths |
| 2 | **Region** (e.g. europe-west1) | Cloud Run, Cloud SQL, bucket, registry |
| 3 | **Cloud SQL instance decision** (name/tier/network — private IP vs proxy) | DEPLOYMENT_RUNBOOK §4 step 1 |
| 4 | **IAM decision**: service account(s) for Cloud Run runtime + deployer, and secret-handling policy (Secret Manager + WIF vs SA key in GitHub) | deploy.yml secrets, bucket IAM |
| 5 | **DB credentials secret** (`tao_app` password) stored in GitHub Environment `gcp-dev` + Secret Manager | `DATABASE_URL`, `DB_PASSWORD_SECRET` |
| 6 | **DEV access policy**: allow `--allow-unauthenticated` (with IdP later) or restrict to corporate IPs/IAP now | Cloud Run ingress setting |
| 7 | (only if GCS artifacts wanted on day 1) bucket name confirmation + `google-cloud-storage` dependency approval | `SOURCE_DOC_BUCKET` wiring |

With 1–6 provided, `deploy.yml` (already wired) performs: build → push → `gcloud run deploy` with Cloud SQL socket + secrets → one-off Alembic/import job → smoke.

## 10. Regression protection (§11)

78/78 combined (`pytest tests`): Phase 1–5 suites untouched and green; Phase 6 added 4 tests (export ×3, docstore ×1) + the pipeline script and container smoke (CI-executed). No approved Product behaviour was modified for deployment — the only product-adjacent change is the Dockerfile `COPY web/` fix (a packaging defect, not behaviour).

## 11. Commits

Phase 6 ships as: ops pipeline script · export endpoint + docstore + tests · CI/CD workflows · Dockerfile fix · runbooks + UAT guide + checkpoint (see pushed log).
