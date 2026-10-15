# Deployment Runbook — Cloud Run + Cloud SQL (shared Product DEV)

**Scope:** Phase 6 · **Environment:** shared DEV only (production is explicitly out of scope for this phase, contract §8)
**Companion docs:** `DATA_OPERATIONS_RUNBOOK.md` (backup/restore/import), `PRODUCT_UAT_GUIDE.md` (Product team usage), `docs/checkpoints/PHASE_6_REPORT.md` (external inputs still required).

---

## 1. Architecture

```
GitHub main ──CI (5 jobs)──▶ deploy.yml (workflow_run, environment gcp-dev)
                                │
                     Artifact Registry (image: app + web/ SPA)
                                │
                     Cloud Run service (stateless, $PORT, min=0/max small)
                                │  unix socket /cloudsql/…
                     Cloud SQL PostgreSQL 16 (private IP, DEV tier)
                                │
                     Cloud Storage bucket (source documents — artifacts only)
```

- The application container is **stateless**: all configuration from env, no local persistent state (verified by container smoke: DB down → `/health` 200, `/health/db` 503, SPA 200).
- Health/readiness: `/health` = liveness (Cloud Run startup+liveness probe), `/health/db` = readiness (DB ping; 503 when down).
- Logging: application log records are JSON (`LOG_FORMAT=json` default) on stdout; uvicorn lifecycle lines are plain text (Cloud Run severity parsing tolerates this).

## 2. Configuration (env)

| Variable | Value in DEV |
|---|---|
| `DATABASE_URL` | `postgresql+psycopg://tao_app:<SECRET>@/tao_authoring?host=/cloudsql/PROJECT:REGION:INSTANCE` |
| `APP_ENV` | `dev` |
| `LOG_FORMAT` | `json` |
| `PORT` | injected by Cloud Run (container honours it; verified with `PORT=8091`) |
| `SOURCE_DOC_BUCKET` | `gs://<project>-source-documents` (activates the GCS artifact driver) |
| `SOURCE_DOC_PREFIX` | `source-documents` |

`.env.example` documents all of these. Secrets never enter the repo (§12).

## 3. Cloud SQL — bring-up from empty (proven pipeline)

The exact sequence proven locally and in CI (`scripts/ops/pipeline_from_empty.sh`,
green in `scripts/ops` run + CI job `migration-import-pipeline`):

1. create empty database;
2. `DATABASE_URL=… alembic upgrade head` (head: `0002_roadmap_outcomes`);
3. `python scripts/import/import_canonical.py` (idempotent, ON CONFLICT DO NOTHING — never clobbers Product edits);
4. `python scripts/import/validate_import.py` — must end **26 PASS / 0 FAIL**;
5. boot app + smoke: `/health`, `/health/db`, `/api/capabilities` (135), `/api/export`.

For Cloud SQL the same steps run from a Cloud Run **job** (or any VM with the
Cloud SQL Auth Proxy) using the unix-socket URL above — see §5.

## 4. First deployment (once GCP inputs exist)

```bash
# 0. prerequisites (PHASE_6_REPORT §external-inputs):
#    GCP_PROJECT_ID, GCP_REGION, Cloud SQL instance, service accounts, secrets
gcloud config set project "$GCP_PROJECT_ID"

# 1. Cloud SQL (DEV tier, private IP)
gcloud sql instances create tao-authoring-dev \
  --database-version=POSTGRES_16 --tier=db-f1-micro --region="$GCP_REGION" \
  --network="projects/$GCP_PROJECT_ID/global/networks/default" --no-assign-ip
gcloud sql users create tao_app --instance=tao-authoring-dev --password="$DB_PASSWORD"
gcloud sql databases create tao_authoring --instance=tao-authoring-dev

# 2. image
gcloud auth configure-docker "$GCP_REGION"-docker.pkg.dev
docker build -t "$IMG" .
docker push "$IMG"     # IMG=$GCP_REGION-docker.pkg.dev/$GCP_PROJECT_ID/app/tao-authoring:sha

# 3. source-document bucket (artifacts only — Product Truth stays in SQL)
gcloud storage buckets create "gs://$GCP_PROJECT_ID-source-documents" \
  --location="$GCP_REGION" --uniform-bucket-level-access
gcloud storage buckets add-iam-policy-binding "gs://$GCP_PROJECT_ID-source-documents" \
  --member="serviceAccount:$RUN_SA" --role="roles/storage.objectAdmin"

# 4. Cloud Run service
gcloud run deploy tao-authoring-dev \
  --image "$IMG" --region "$GCP_REGION" \
  --service-account "$RUN_SA" \
  --add-cloudsql-instances "$GCP_PROJECT_ID:$GCP_REGION:tao-authoring-dev" \
  --set-env-vars "APP_ENV=dev,LOG_FORMAT=json,SOURCE_DOC_BUCKET=gs://$GCP_PROJECT_ID-source-documents" \
  --set-secrets "DB_PASSWORD=DB_PASSWORD_SECRET:latest" \
  --min-instances 0 --max-instances 2 --allow-unauthenticated   # DEV: IdP later, see §6
```

## 5. Schema + canonical data on Cloud SQL

Run as a one-off Cloud Run **job** using the same image (it ships `migrations/` +
`alembic.ini`; the importer scripts are in the repo — run them from a checkout
with the proxy, or bake `scripts/` into an ops image):

```bash
DATABASE_URL="postgresql+psycopg://tao_app:$DB_PASSWORD@/tao_authoring?host=/cloudsql/PROJECT:REGION:INSTANCE" \
  alembic upgrade head
DATABASE_URL=… python scripts/import/import_canonical.py
DATABASE_URL=… python scripts/import/validate_import.py   # must be 26 PASS / 0 FAIL
```

Then verify: `curl https://<dev-url>/health/db` → `{"database":true}`, `/api/capabilities` → count 135.

## 6. Identity on DEV (§5 of the contract)

- The app keeps the **replaceable identity abstraction**: every request carries `X-User-Ref` (default `dev-user`); the UI chip allows switching it. Product entities are never coupled to it.
- **Production IdP integration point** (documented contract): `app/identity.py::get_actor` is the single seam. It reads `X-User-Ref` today; the production implementation adds an IAP/JWT verification step and derives `user_ref` from a verified identity claim, keeping the same `Actor` model, audit and `updated_by` semantics. No Product schema change is required — swap the implementation, keep the interface.
- Until IdP integration: shared DEV accepts controlled `user_ref` values so audit trails distinguish Product users (agree a convention, e.g. `firstname.lastname`).

## 7. Rollback

- **Application rollback:** redeploy the previous image tag (`gcloud run deploy … --image $IMG_PREV`); Cloud Run keeps revision history — `gcloud run revisions list` / `gcloud run services update-traffic --to-revisions REV=100`.
- **Migration rollback:** only where safe — `alembic downgrade <target>`; `0002_roadmap_outcomes` downgrades cleanly (single table, no data loss). Never downgrade across a migration that would destroy Product Truth without a prior export (see DATA_OPERATIONS_RUNBOOK §export).
- **Bad data import:** the importer never overwrites (`ON CONFLICT DO NOTHING`); to fully re-seed a DEV database, take an export first, drop + recreate the DB and re-run the pipeline (DATA_OPERATIONS_RUNBOOK §re-seed).

## 8. Deployment blockage (honest status)

The deployment automation above is **prepared but not executed**: actual Cloud
Run/Cloud SQL provisioning requires the external inputs listed in
`docs/checkpoints/PHASE_6_REPORT.md` (project id, region, instance, IAM/SA
decisions, secret handling per IT policy). Everything up to that boundary is
proven locally: image build, `$PORT`, graceful DB failure, SPA serving, live-DB
serving, and the empty→serving pipeline.
