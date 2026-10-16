# CUSTOMER_MIGRATION_PLAN_MODEL — model, derivation rules, boundaries

**Date:** 2026-10-16 · **Implements:** FINAL UAT EVOLUTION §8–§14

## 1. Concept

ONE Product Roadmap → ONE common Migration Path (M1–M6) → **MULTIPLE Customer Migration Plans**. A Customer Migration Plan applies the shared transition framework to **one customer's real situation** so they can start preparing their own TAO Studio implementation plan.

## 2. Data model (Alembic `0004_customer_migration_plans`)

The plan lives on the existing Customer entity — no new entity, no duplicate truth.

### Customer context (new columns)
| Column | Carries |
|---|---|
| `current_environment` | current TAO version / environment where known |
| `relevant_markets` | relevant markets / use case where known |
| `proposed_migration_window` | proposed migration window (free text; Product/Customer agreed — never auto-generated) |
| `customer_dependencies` | customer-specific dependencies |
| `assumptions` | assumptions |
| `exceptions` | exceptions |
| `customer_feedback` | customer feedback / evidence |

### Pre-existing (already governed)
`name`, `current_use`, `min_functionality_today`, `min_functionality_studio`, `desired_outcome`, `value_opportunity`, `blockers` (covers workflow/governance/data/metadata/integrations/training/contracts/procedures/adoption/organisational readiness), `earliest_milestone_interval` (e.g. `M3 -> M4`; TS codes refused by API), `validation_status`, `notes`, `version` — plus `customer_capabilities` (required Canonical Capabilities, M:N).

### No speculative scoring
Readiness is **derived at read time** (below); no numeric score is stored anywhere.

## 3. Derived dependency & readiness rules (§14)

All inputs are canonical: `roadmap_timing` (the ONLY Product timing truth), `milestones` (M1–M6), `customer_capabilities`, `validation_status`.

```
proposed interval start = position_month of the first milestone in earliest_milestone_interval
per required capability:
  roadmap_end = start_month + duration_months          (NULL when untimed)
  available_by_interval_start = (roadmap_end is not NULL) AND (roadmap_end ≤ interval start)
readiness:
  no interval proposed                        → PRODUCT DECISION REQUIRED
  any capability not available_by_interval_start → BLOCKED BY ROADMAP CAPABILITY
  all available AND validation ∉ {Customer validated, Migration committed} → CUSTOMER VALIDATION REQUIRED
  all available AND validated/committed        → READY FOR PROPOSED INTERVAL
  validation_status starts with "migration exception" → MIGRATION EXCEPTION
```

Every state is explainable from the data: the plan view lists **which capabilities create the blocker** (identifiable per CAP, with the dependency reason: *untimed — dependent on Roadmap planning* or *Roadmap timing completes month N, after the proposed interval start*), plus Feature composition where defined (derived from `feature_capabilities`).

**§10 boundary:** when Roadmap timing changes, the derived availability and readiness change on the next read — the plan stores **no timing of its own** (tested).

## 4. API surface

- `GET /api/customers` — list incl. per-customer `migration_plan` (readiness, interval, counts, milestones).
- `GET /api/customers/{id}` — full plan payload (context/need fields, required capabilities with availability + features, shared milestones, readiness + reason).
- `POST/PATCH /api/customers[/{id}]` — create/edit plan fields; **optimistic concurrency** (409 with `current_version`), actor + audit (`record_audit`), TS codes refused (422).
- `POST/DELETE /api/customers/{id}/capabilities[/{cap_id}]` — required-capability links (audited).
- No customer or date is ever invented: the UI creates customers only with Product-supplied IDs/names; windows are free-text Product/Customer agreements.

## 5. UI

- Migration screen gains a **Migration Path | Customer Plans** switch (§12) — the common path stays intact.
- **Customer Plans tab**: customer list (name, readiness badge, interval, required-caps count, blockers) with an honest empty state (D3) and "+ Register customer".
- **Open Migration Plan**: full plan — readiness + reason; Customer context & need; Product dependencies table (CAP → universal CAP modal, admission, timing, availability badge, dependency reason, Features); shared M1–M6 strip; Migration (interval, window, dependencies, blockers, assumptions, exceptions); Validation (status, notes, feedback). **Edit plan** persists via the API.

## 6. Boundaries

No duplicate Roadmap timing · no independent Feature timing consumed · no invented customers/dates/requirements · TS1/TS2/TS3 never canonical · Milestone edits propagate to the common path and every customer plan (same records).
