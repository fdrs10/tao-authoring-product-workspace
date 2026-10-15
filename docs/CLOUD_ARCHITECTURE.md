# Cloud Run + Cloud SQL Target Architecture

## Recommended stack
- Frontend: existing HTML/CSS/JS UX reimplemented as modular web frontend (framework optional; do not redesign merely to adopt one).
- Backend: FastAPI or equivalent stateless HTTP API.
- DB: PostgreSQL on Cloud SQL.
- Runtime: Cloud Run.
- Source documents: Google Cloud Storage or approved document URLs; metadata in PostgreSQL.
- Secrets: Secret Manager.

## Environments
- `dev`: independent Cloud Run service + Cloud SQL database/schema.
- `staging`: regression/UAT.
- `prod`: shared company URL after acceptance.

## Required env vars
`DATABASE_URL` or Cloud SQL connection components, `APP_ENV`, auth configuration, source bucket, Jira base URL if needed. Never commit secrets.

## Concurrency
Every mutable canonical record should carry `version` and `updated_at`. PATCH requests use optimistic concurrency. On conflict return 409 and show user a reconciliation message.

## Audit
Write append-only audit events for capability, source mapping, Jira relationship, Admission, budget, roadmap timing, milestone and customer changes.
