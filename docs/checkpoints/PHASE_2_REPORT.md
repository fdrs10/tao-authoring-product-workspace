# PHASE 2 — Database (PostgreSQL + Alembic + FastAPI) — Checkpoint Report

**Date:** 2026-10-15 · **Contract:** KINCHI POST PHASE 1 EXECUTION / IMPLEMENTATION CONTRACT (§14–16, §26–53)

## 1. Work completed
- **§2 Push baseline**: `main` + tag `functional-baseline-v38.6` pushed to `fdrs10/tao-authoring-product-workspace` (before Phase 2 code).
- **Governance decisions applied in schema/importer** (no source data rewritten):
  - §3 five caps → `review_status='PRODUCT_SCOPE_REVIEW_REQUIRED'` (CAP-0071/0126/0128/0131/0133).
  - §5 SRC-JIRA-001 registered in `sources` (`Operational / Delivery Evidence`; document_uri=`data/raw/JIRA_current_backlog.csv`; API-future note preserved).
  - §8 CAP-0134/0136 → `ideation_sheet='UNSET'`, `review_status='REVIEW_REQUIRED'`.
  - §9 `roadmap_admission` **nullable** (NULL=UNSET; 133 NULL + 2 Candidate verified).
  - §12 budgets **nullable**, never populated on import (135/135 NULL).
  - §13 decision labels verbatim in DB (`Develop`/`DEVELOP / VALIDATE`) — normalization pending Product review.
  - §19 `source_capabilities.reconciliation_relationship` present (values from governed lineage).
  - §26 six markets seeded as reference data with the approved colour identity recovered from v38.6 (`#4388bd #8061b5 #2f99aa #669b3c #d77619 #c95c5c`).
  - §36/§39/§58 milestones & customers tables present, **0 rows** (no governed data; none invented).
- **Alembic baseline migration** `0001_initial_schema` (15 tables) — schema now migration-managed; `db/schema.sql` remains the frozen handoff seed.
- **Idempotent importer** `scripts/import/import_canonical.py` (ON CONFLICT DO NOTHING everywhere; deterministically ordered; conflict policy = insert-once/skip + report; never clobbers in-DB Product edits).
- **Validator** `scripts/import/validate_import.py` → `data/reports/phase2_import_validation.json`.
- **App skeleton** FastAPI `/{health,health/db}`, structured JSON logs, env-only config, stateless; **Dockerfile** (python:3.12-slim, non-root, $PORT, HEALTHCHECK) + `docker-compose.yml` (postgres:16-alpine + app/migrate/import services) + `.env.example`; `requirements.txt` frozen from the working venv (fastapi 0.143.1, uvicorn 0.54.0, SQLAlchemy 2.1.4, alembic 1.20.0, psycopg 3.3.6, pydantic 2.14.1).
- **§48 docs/REFERENCE_IMPLEMENTATION_MATRIX.md** — all seven required reference artifacts physically verified; v33 family reported as missing (non-blocking; v10 verified with pointer drag/resize/snap code, v38.6 retains hierarchy/horizon/resize markers).
- **README** local-development run instructions added.

## 2. Files changed
`alembic.ini`, `migrations/{env.py,script.py.mako,versions/0001_initial_schema.py}`, `scripts/import/{import_canonical.py,validate_import.py}`, `app/{__init__,config,db,main}.py`, `Dockerfile`, `docker-compose.yml`, `.env.example`, `requirements.txt`, `README.md`, `data/reports/phase2_import_validation.json` (new), `docs/REFERENCE_IMPLEMENTATION_MATRIX.md` (new), `docs/checkpoints/PHASE_2_REPORT.md` (new).

## 3. Data counts (from live `tao_authoring` dev DB)
| Table | Rows |
|---|---:|
| capabilities | 135 |
| sources | 8 |
| source_capabilities | 224 |
| capability_sources | 211 |
| capability_markets | 696 |
| markets | 6 |
| jira_tickets | 28 |
| capability_jira | 32 (24 linked tickets × 17 caps) |
| roadmap_timing | 135 |
| customers / milestones | 0 / 0 (awaiting governed data) |

## 4. Migrations
- `0001_initial_schema` — applied (`alembic_version` tracked); deterministic DDL; downgrade provided.

## 5. Tests run
1. `alembic upgrade head` → 15 tables created, markets seeded ✓.
2. Import #1: 135/8/224/211/696/28/32/135 inserted, **0 warnings** ✓.
3. Import #2 (idempotency): 0 inserted, all 1,441 rows skipped by conflict ✓.
4. `validate_import.py`: **26/26 checks PASS** (counts, 5 referential-integrity queries, duplicate/retired-ID guards, admission NULL semantics, budgets NULL≠0, §3/§5/§6/§8/§26 contract verifications). Report: `data/reports/phase2_import_validation.json`.
5. Health smoke (uvicorn local vs. dockerised PG): `/health` → 200, `/health/db` → 200 `{"database":true}` ✓.

## 6. Results
DEV dataset in PostgreSQL equals Phase 1 reconciled truth; contract governance decisions encoded in DB; cloud-compatible connection config documented; importer idempotent; validation green.

## 7. Defects found & fixed this phase
- Validator initial expected `count:capability_jira=24` (misread of Phase 1 wording: 24 = linked tickets, 32 = pair rows). Corrected expectation + added `linked_jira_tickets==24`, `caps_with_jira_links==17` — rerun 26/26 PASS. (Correction logged; no data change.)

## 8. Product decisions required before Phase 3
| # | Decision | Context |
|---|---|---|
| D1 | Supply or skip v33 Roadmap family artifacts | Not blocking until Phase 7 (matrix §50); v10 suffices unless branch/quarter-detail gaps emerge. |
| D2 | Governed **milestones** dataset (names, dates) | `milestones` empty; Roadmap/Migration need real rows before Phase 8. Do not invent dates (§36). |
| D3 | Governed **customers** dataset | `customers` empty per §39/§58; implement-as-governed-import-later. |
| D4 | Decision-label normalization (`Develop` vs `DEVELOP / VALIDATE`) | Verbatim in DB per §13; Product semantic review pending (flag in Backlog UI later). |
| D5 | Auth model choice for Phase 3+ (identity provider / anonymous user_ref) | `users` table exists; no auth UX yet; Cloud Architecture expects authenticated users. |

## 9. Commit hashes (this phase)
See git log: `db:` (schema+seed), `data:` (importer+validator+validation report), `api:` (skeleton+infra), `docs:` (matrix, README, this checkpoint). Exact SHAs: `git log --oneline 20ba370..HEAD`.

## 10. Next phase
PHASE 3 — API + audit + concurrency: CRUD capability/source/jira, admission sync across the three views (§11), optimistic concurrency (`version` → 409), audit_events writes, users/auth foundation (D5). Gate before frontend: matrix reviewed; only v33 optionally requested (D1).
