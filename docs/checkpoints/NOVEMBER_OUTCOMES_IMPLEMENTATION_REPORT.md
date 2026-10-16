# NOVEMBER_OUTCOMES_IMPLEMENTATION_REPORT

**Date:** 2026-10-16 · **Implements:** FINAL UAT EVOLUTION (no redesign; existing architecture/shell/APIs/audit/test patterns reused) · **Regression:** **101 passed** (30 API · 54 UI E2E · 10 ESM gate · 7 November) — all prior suites preserved.

---

## 1. Baseline commit

`c35d20f` (UAT structural update) — verified; tag `dev-candidate-v1.0` (04f5208) untouched. This work lands after it.

## 2. Exact schema changes (Alembic `0004_customer_migration_plans`, applied)

`customers` + 7 columns: `current_environment`, `relevant_markets`, `proposed_migration_window`, `customer_dependencies`, `assumptions`, `exceptions`, `customer_feedback`. Everything else reuses existing tables (`customers`, `customer_capabilities`, `roadmap_timing`, `milestones`, `features`/`feature_capabilities`). No new tables; no scoring columns; readiness derived, never stored.

## 3. Exact API changes

- `GET /api/customers` — per-customer embedded `migration_plan` (readiness + reason, interval start milestone, availability counts, shared milestones).
- `GET /api/customers/{id}` — full Customer Migration Plan payload: context/need/migration/validation fields (incl. the 7 new columns), required capabilities **with Roadmap timing, availability-by-interval-start, dependency reason, Feature composition**, shared milestones, readiness.
- `POST/PATCH` customer models accept the 7 new fields (TS-code guard unchanged; optimistic version; actor; audit).
- No other endpoint changed; Jira untouched; no customer/date invented.

## 4. Exact UI changes

- `web/index.html` + `web/js/main.js`: **NOVEMBER OUTCOMES** nav entry + `#/outcomes` route.
- `web/js/views/outcomes.js`: five-outcome orientation page (purpose, status context, working-area links, dependency, Product-input-required) + workflow flow strip.
- `web/js/views/migration.js`: **Migration Path | Customer Plans** subtabs; Customer Plans list (readiness badge, interval, required-caps count, blockers) with honest empty state + "+ Register customer" (Product-supplied data only); **Open Migration Plan** pane (readiness + reason; context & need; Product dependencies table with clickable CAP-IDs → universal modal, availability badges, per-cap dependency reasons, Features; shared M1–M6 strip; Migration + Validation sections); **Edit plan** form persisting all plan fields via API.
- `web/js/components/capmodal.js`: `closeCapModal` now removes only the CAP drawer overlay (closing a CAP drawer opened over a Customer Plan no longer destroys that plan pane — found via the §55 guard).
- `web/js/api.js`: `endpoints.customer(id)`.

## 5. How the five November outcomes are represented

`#/outcomes` renders all five (§15) with purpose/status/link/dependency/Product-input-required; links land in Ideation/Backlog/Roadmap/Migration. No duplicate Product data is introduced (capability count asserted unchanged).

## 6. Common Path vs Customer Plans

The Migration screen separates them explicitly (`Migration Path | Customer Plans`): the common path keeps value-unlocked + M1–M6 intervals; Customer Plans apply the same milestones per customer. Milestone truth is shared (edit propagates to both — tested); TS codes remain non-canonical (UI + API 422 tested).

## 7. Customer Migration Plan model & readiness derivation

Model + derivation rules: `docs/CUSTOMER_MIGRATION_PLAN_MODEL.md`. Short form: the plan consumes `roadmap_timing` (only timing truth) + shared `milestones`; availability per required CAP = `start+duration ≤ proposed interval start`; readiness ∈ {PRODUCT DECISION REQUIRED, BLOCKED BY ROADMAP CAPABILITY, CUSTOMER VALIDATION REQUIRED, READY FOR PROPOSED INTERVAL, MIGRATION EXCEPTION} — each explainable from listed data (blocked CAPs identified by ID and reason).

## 8. Tests added (§22)

`tests/ui/test_november_outcomes.py` (10): outcomes visibility + correct links + no duplicate data; plans honest empty state; CRUD/interval/blockers persistence + CAP modal navigation + audit + 409; no invented dates (only M1–M6 dates shown); readiness follows Roadmap timing (BLOCKED → CUSTOMER VALIDATION after timing + validation change) with blocked CAPs identifiable; PRODUCT DECISION REQUIRED when no interval; Path/Plans separation; TS refusal. Full suite: **101 passed**.

## 9. Screenshots (`docs/evidence/november-outcomes/`)

01 outcomes overview · 02 ideation/target scope · 03 backlog · 04 roadmap · 05 common path with M1–M6 · 06 customer plans list · 07 fixture customer migration plan · 08 required-capability dependencies · 09 readiness/blocker view. The fixture customer exists **only in the throwaway e2e DB** and was removed after capture (governed data untouched; customers remain empty).

## 10. Product decisions still pending

- Governed **customer dataset** (D3) — Customer Plans are ready but honestly empty.
- **Milestone baseline** M1–M6 is editable Product data (D2) — currently the confirmed v35.6 baseline.
- **Feature timing semantics** (Features remain composition-only with derived coverage).
- **IdP identity** integration point (user_ref convention meanwhile).
- Source-by-source reconstruction — **next controlled operation**, not started (§17/§25).

## 11. Commits & pushed HEAD

- `c35d20f` (baseline carried from the structural update, tag `dev-candidate-v1.0` untouched)
- November work: schema/API + UI/outcomes + tests + docs (see pushed log; final HEAD after push reported below).
