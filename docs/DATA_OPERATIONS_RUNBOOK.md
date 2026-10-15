# Data Operations Runbook — backup, restore, re-import, recovery

**Scope:** shared Product DEV (and the same procedures apply to any future production environment with tighter access).
**Principle (contract §3):** PostgreSQL keeps **Product Truth** (metadata + lineage); object storage keeps only **document artifacts**. The two are never conflated.

---

## 1. Product Truth export (§7)

One authoritative JSON export — no UI scraping:

```bash
curl -s "https://<dev-url>/api/export" -o export-$(date +%F).json
```

Contents (deterministic ordering, stable diffs): `capabilities` (incl. MoSCoW,
Roadmap Admission, budgets, decision, visibility, review status),
`capability_markets`, `markets`, `sources`, `source_capabilities` (lineage),
`capability_sources`, `jira_tickets` + `capability_jira`, `roadmap_timing`,
`roadmap_outcomes`, `milestones`, `customers`, `customer_capabilities`.
Verify with `python -c "import json;d=json.load(open('export-…json'));print(d['counts'])"`.

Recommended cadence on DEV: before/after each UAT round; at minimum weekly.

## 2. Database backup (Cloud SQL)

```bash
# on-demand logical backup
gcloud sql export sql tao-authoring-dev "gs://$GCP_PROJECT_ID-backups/db-$(date +%F-%H%M).sql" \
  --database=tao_authoring --offload

# automated: Cloud SQL scheduled backups (retention per IT policy)
gcloud sql instances patch tao-authoring-dev --backup-start-time 03:00 --retention-backup-count 14
```

Local/compose equivalent: `pg_dump -h localhost -p 54323 -U tao tao_authoring > db.sql`.

## 3. Database restore

```bash
# into a fresh database (preferred — never in-place over live DEV)
gcloud sql databases create tao_authoring_restore --instance=tao-authoring-dev
gcloud sql import sql tao-authoring-dev "gs://$GCP_PROJECT_ID-backups/db-….sql" \
  --database=tao_authoring_restore
# verify: row counts + /health/db on a temporary service pointing at _restore
# then swap the service's DATABASE_URL or rename databases
```

Restore verification checklist: capabilities = 135 (or current governed count); export diff against the pre-incident export (`counts` equal); `/api/roadmap?admission=` row count sane; UI loads `#/roadmap`.

## 4. Governed canonical re-import (from empty)

Proven end-to-end by `scripts/ops/pipeline_from_empty.sh` (also a CI job):

1. create empty DB → `alembic upgrade head`;
2. `python scripts/import/import_canonical.py` — **idempotent, `ON CONFLICT DO NOTHING`**: a re-import never clobbers in-DB Product edits; would-be conflicts are reported as SKIPPED for human review;
3. `python scripts/import/validate_import.py` — gate: **26 PASS / 0 FAIL**;
4. boot + smoke (`/health/db`, 135 capabilities, `/api/export`).

**Re-seed a corrupted DEV database:** export first (§1) → drop DB → recreate → pipeline → reconcile the export against the fresh import (Product edits made in DEV are NOT in the canonical source files; the export is the only record of them).

## 5. Source documents (artifacts) — backup and recovery

- Storage layout: `<bucket>/source-documents/<SOURCE-ID>/<filename>` (GCS) or `./data/source-documents/<SOURCE-ID>/…` (local dev driver). References are opaque (`gs://…` / `local://…`); Source metadata + lineage stay in PostgreSQL (never moved to object storage).
- Backup: GCS bucket versioning + a second-region copy for the governed set:
  ```bash
  gcloud storage buckets update "gs://$GCP_PROJECT_ID-source-documents" --versioning
  gcloud storage rsync -r "gs://$GCP_PROJECT_ID-source-documents" "gs://$GCP_PROJECT_ID-source-documents-dr"
  ```
- Recovery: re-rsync from the DR bucket; verify per-source listing via the docstore (`store.list(source_id)`); orphan check = artifacts whose SOURCE-ID has no row in `sources` (deletion follow-up, manual).
- Local dev driver: copy the `data/source-documents/` directory; it is external to the app container (mount a volume in containerised use).

## 6. Migration rollback (where safe)

- `alembic downgrade <target>` — **only** with a prior export and only for migrations whose `downgrade()` is data-safe.
- Current history: `0001_initial_schema` (full schema — downgrade drops everything: treat as rebuild-via-pipeline, not a rollback) and `0002_roadmap_outcomes` (single table, safe to downgrade: `alembic downgrade 0001_initial_schema` drops only outcome narratives).
- Rule: if in doubt, **restore from backup instead of downgrading**.

## 7. Application rollback

See DEPLOYMENT_RUNBOOK §7 (Cloud Run revision traffic split / previous image tag).

## 8. Portability statement

Product Truth is fully contained in (a) PostgreSQL (live) and (b) the governed source files under `data/` + the export JSON (portable). The application is stateless; the SPA is static files served by the same container. Moving between environments = restore SQL + optionally re-run the pipeline + point `SOURCE_DOC_BUCKET` at the restored artifact bucket.
