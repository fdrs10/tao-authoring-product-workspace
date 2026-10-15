# PHASE 3 — API + Audit + Concurrency — Checkpoint Report

**Date:** 2026-10-15 · **Gate:** Product approved Phase 2; D1–D5 decisions applied. Frontend reimplementation explicitly NOT started (contract: shared-state contract first).

## 1. Endpoints implemented (FastAPI, psycopg, all recorded-commit verified)

| Area | Endpoints |
|---|---|
| Health (P2) | `GET /health` `GET /health/db` |
| Capabilities | `GET /api/capabilities` (filters: category, market, moscow, admission incl literal `UNSET`, visibility, source, ideation_sheet, decision, origin) · `GET /api/capabilities/{cap_id}` (markets+colors, sources, source-capability lineage, jira+status+target_release, timing, derived `total_budget_hours`) · `PATCH /api/capabilities/{cap_id}` (working_name, description, category, moscow, visibility, scope, origin, owner, decision, v2_mapping, ideation_sheet, **roadmap_admission**, budgets, notes, review_status, markets replace-set) |
| Jira links | `POST /api/capabilities/{cap_id}/jira` (0..N, create/update split audit with true before-image; unknown ticket → 404) · `DELETE …/jira/{jira_key}` |
| Sources | `GET /api/sources` (+extracted counts) · `GET /api/sources/{id}` · `GET /api/sources/{id}/capabilities` (Source Truth verbatim + canonical reconciliation) |
| Jira | `GET /api/jira` (+linked counts, status/treatment filters) · `GET /api/jira/{key}` (0..N linked CAPs) |
| Roadmap | `GET /api/roadmap` (default admission=COMMITTED §34; UNSET/all filters; Product timing only — Jira target_release surfaced separately, never overwriting §35) · `PATCH /api/roadmap/{cap_id}` (upsert; optimistic version) |
| Milestones | `GET /api/milestones` · `POST /api/milestones` · `PATCH /api/milestones/{id}` — table still **0 rows** (D2 honored) |
| Customers | `GET` list/detail(+required caps) · `POST` (409 dup, §40 TS-code rejection → 422) · `PATCH` · `POST/DELETE /{id}/capabilities` — table still **0 rows** (D3 honored) |
| Identity | `X-User-Ref` header → `Actor(user_ref)` via `get_actor` (`app/identity.py`), default `dev-user`; single replacement point for corporate IdP; nothing Product-facing hardwired (D5) |
| Audit | `app/audit.py` append-only writer; `users` upsert of actor `user_ref` for the future identity linkage |

## 2. Schema/migrations added
None required in Phase 3 — the Phase 2 baseline `0001_initial_schema` anticipated all needs (nullable admission §9, nullable budgets §12, reconciliation §19, users §51). A deliberately empty second migration was NOT introduced (checkpoint-registered decision: next migration lands with Phase 4 UI-state needs or D-data deliveries).

## 3. Tests and results
`tests/api/` (= pytest, suite `test_phase3_api.py` + `conftest.py`): **17/17 PASS** (2.48s) on a dedicated throwaway DB `tao_authoring_test` created by fixture → alembic-migrated → truncated+seeded per test. Coverage of the mandated matrix: success (list/detail/filters/CRUD happy paths), validation (bad admission 422, unknown market 422, negative budget 422, empty patch 400, unknown extra field 422, timing duration<1 422, TS-interval 422), not-found (cap/jira/source/milestone/customer/link 404s + dup 409s), **stale-version conflict → 409 with `current_version`** (capability, timing, milestone, customer), **audit generation** (2 successive PATCHes → 2 audit_events rows with expected actor from default + `X-User-Ref` header, `_changed` lists, before/after fields). Semantic invariants asserted: admission NULL untouched by unrelated PATCH (UNSET ≠ BACKLOG), budgets NULL untouched (NULL ≠ 0), Jira ticket survives link deletion (evidence ≠ capability), Source row read-only via API, derived total only when either budget is set.

## 4. Concurrency strategy
Single-writer optimistic concurrency: every mutable entity carries `version`; every PATCH requires it; mismatch → `409 {"error":"version_conflict","current_version":N,"requested_version":M}` intended for the UI reconciliation message; updates execute `UPDATE … AND version=:requested` in one transaction with the audit row — stale writes physically cannot land silently. CAP-ID immutable (409-less 422 since `cap_id` not an accepted patch field; retired CAP-0135 untouchable by absence).

## 5. Audit strategy
Append-only `audit_events` rows in the mutation's own transaction: actor (user_ref), timestamp (DB), entity_type/entity_id, action (create/update/delete), before/after JSON snapshots of the changed fields, `_changed` field-name list; relationship entities (`capability_jira`, `customer_capabilities`, `roadmap_timing`, `milestone`, `customer`) audited the same way.

## 6. Identity abstraction
`app/identity.py::get_actor` (DEV: header/default) → `Actor(user_ref)` frozen dataclass; routers never parse headers themselves; actor persisted as opaque string in audit and upserted into `users`. Corporate IdP = swap this one function (D5 open until Product selects IdP — non-blocking).

## 7. Exact data counts (dev `tao_authoring` after Phase 3; unchanged data, schema-only phase)
capabilities **135** · sources **8** · source_capabilities **224** · capability_sources **211** · capability_markets **696** · markets **6** · jira_tickets **28** · capability_jira **32** · roadmap_timing **135** · customers **0** · milestones **0** · users **0**

## 8. Product semantic issues found
- **None blocking.** The `total_budget_hours` derivation rule implemented is: `NULL when both parts are NULL, else A+E (NULL coalesced to 0)`. If Product wants stricter "NULL unless both estimated", it's a one-line API change — flagged for the Phase 4 UI display decision.
- Known hygiene note: `fastapi.testclient`/httpx 0.28 deprecation warning (recorded in matrix addendum).

## 9. Commit hashes (this phase, small meaningful commits, §57)
See `git log --oneline` — sequence: `api:` routers (capabilities+jira links; sources+jira; roadmap+milestones; customers) → identity → audit → fix jsonb encoding → tests → docs/checkpoint. Exact SHAs: `git log --oneline 1067931..HEAD`.

## 10. Recommendation for Phase 4
Proceed to **Frontend foundation** once this checkpoint is accepted. It must consume this API (never recreating canonical state in JS/localStorage, contract §51). First frontend wave per implementation order (§36): Ideation shell + Sources + universal CAP modal (already specified in REFERENCE_IMPLEMENTATION_MATRIX rows 1–3) with the smoke-test guard (§55) wired from day one.
