# Phase 5 Checkpoint — Roadmap + Migration Recovery and Implementation

**Date:** 2026-10-15 · **Status:** COMPLETE · **Tests:** 74/74 (26 API + 38 UI E2E + 10 JS-ESM gate), single combined pytest invocation

---

## 1. Recovery analysis (hard gate honoured)

Behaviours were physically extracted from the historical artifacts **before** any implementation:

- **`legacy/TAO_Studio_Authoring_Action_Plan_Roadmap_v10.html`** (JS read in full): 27-month window (Oct 2026 → Dec 2028, 9 quarters); bar geometry `left=start/27 %, width=dur/27 %`; pointer drag with `delta=round((clientX-sx)/(trackWidth/27))` month snapping; left/right handle resize clamps; category→big rock→feature hierarchy; independent `Set`-keyed branch expansion with multiple open; red vertical milestone lines at `((month+.5)/27 %)` labelled once per category, scope-filtered (global/category/big rock), draggable; quarter modal (3 month columns × rows, active features, milestone chips); horizon modal with window-clipped bars; scope modal; design-rules tab.
- **`legacy/TAO_Authoring_v35_6_MIGRATION_DIAGRAM(1).zip`** (md5 `e873d77d…`, preserved unchanged; extracted to working dir only): Slide-3 vertical bands **VALUE / CAPABILITIES UNLOCKED → MIGRATION PATH (3.x → transition states → Target) → CUSTOMERS READY TO MOVE**; 7 milestone intervals holding manually-authored unlocked-capability bullets + customer names; customer transition form (current use, desired outcome, value opportunity, required capabilities, blockers, earliest transition state, validation status); M1–M6 example milestones; fake customers A–F.
- **v38.6** (consulted only for later additions): horizon buttons Full/0–6m/7–24m/Tail; Roadmap | Outcome switch with three narrative blocks; admission filter incl. UNSET.
- **v33 family remains absent** from `/legacy` — v10 carried every required behaviour, so nothing is blocked.

Full deliverable: `docs/ROADMAP_MIGRATION_RECOVERY_SPEC.md` (behaviour found / to recover / **not** to copy / canonical mapping / derived rules D-R1, D-R2, D-R3, D-M1, D-M2 / Product decisions).

## 2. Roadmap behaviours recovered from v10 → implementation

| Behaviour | Where |
|---|---|
| Full Roadmap default view, 3-level hierarchy, desktop-width without horizontal scroll (asserted in test) | `renderFull` — Category → Big Rock/Market band → capability bars + drilldown rows |
| Independent expand/collapse, multiple open, preserved across edits/filters/reloads | module-level `session.expanded` Set (in-memory UI state; canonical state never local) |
| Drag move / left resize / right resize / month snapping | v10 pointer model verbatim; on drop → `PATCH /api/roadmap/{cap}` with optimistic version; **409 reverts the bar to server truth** + explicit warn (never silent overwrite) |
| Milestone red vertical lines, labelled once per category, draggable | milestone PATCH (versioned); label once on first band per category |
| Quarter report view | `openQuarter` modal: month-detail grid, active caps w/ MoSCoW/admission/Jira, milestone chips, click-through to the **universal CAP modal** |
| Design rules | collapsed `Roadmap design rules` panel (8 v10 rules) |
| Market legend + governed colours | Phase 4 `marketLegend` reused (§17) |

Horizons Full/0–6m/7–24m/Tail and the Outcome switch (v38.6 concepts) implemented as **views over the same data**; Outcome narratives are server-persisted (§18 — no LocalStorage for shared state).

## 3. Migration behaviours recovered from v35.6 → implementation

- Vertical 3-band layout: **VALUE / ROADMAP CAPABILITIES UNLOCKED** → **MIGRATION PATH / MILESTONES** → **CUSTOMER TRANSITION PROJECTS — CUSTOMERS READY TO MOVE**.
- **Derivation, not duplication (§13):** interval bands are computed from `roadmap_timing` + milestones — "Unlocked by the start of this interval" (start+dur ≤ interval start) and "In flight during this interval" (overlap). Changing Roadmap timing changes Migration on next load (test-verified).
- **One shared milestone dataset** with the Roadmap: the same `GET/PATCH /api/milestones`; editing a milestone in Migration updates the Roadmap lines (test-verified).
- **Customer transition = milestone interval** (`M1 -> M2`); TS1/TS2/TS3 never canonical — the API 422s TS codes (§14, test-verified).
- **Migration ≠ parity (§15):** blockers beyond capability (workflow, governance, data, metadata, integrations, training, contracts, procedures, adoption, organisational readiness) carried in `customers.blockers` + `validation_status`; the UI states explicitly that availability ≠ readiness.
- **Honest empty states (§10/D3):** no governed milestones/customers exist → the view says so and never invents names, dates or customers. The milestone editor requires Product-supplied IDs/names.

## 4. Differences deliberately not reproduced

localStorage persistence of any shared state (v10/v35.6/v38.6); invented baseline roadmap content; v35.6 M1–M6 milestones and customers A–F (**kept only as clearly-marked test fixtures**); TS transition-state vocabulary as model; commitment-type visual marks (◇■◆↔ — replaced by canonical Admission/MoSCoW/Decision); Jira-level ticket bars with their own timing (Jira = evidence: key/status/target release only, never timing); random `uid()` ids; create-buttons for categories/big rocks (ID governance).

## 5. Schema / API extensions (governed)

1. **Alembic `0002_roadmap_outcomes`** — `roadmap_outcomes(horizon PK '0-6m'|'7-24m'|'tail', narrative, version, updated_at, updated_by)`; applied to dev DB (head = `0002_roadmap_outcomes`); UI test DB upgraded per-session by conftest.
2. **`GET /api/outcomes`** (rows created on demand, narrative NULL — no invented content) and **`PATCH /api/outcomes/{horizon}`** (optimistic version + actor + audit_events).
3. `PATCH /api/roadmap/{cap_id}` now returns the **new version** (the UI needs it after drag-drop).
4. No other schema changes: milestones/customers/customer_capabilities already modelled in Phase 2.

## 6. Tests (§19 matrix)

**New suites:** `tests/api/test_phase5_api.py` (9), `tests/ui/test_phase5_ui.py` (18), `tests/js/test_web_esm_syntax.py` (10).
**Coverage:** default COMMITTED population + empty state (D-R3); hierarchy + desktop-width assertion; independent multi-open expand/collapse; 0–6m/7–24m/Tail windows over same data; Outcome persist + 409 recover; CAP modal reuse from bars and quarter chips; drag move (+ month snap 2.4→2), right resize, left resize (v10 math (3,4)→(2,7)); persisted timing via API; **409 timing conflict never overwrites** (server truth asserted); filters do not reset expansion/timing; Jira evidence display-only; milestone render + drag persist; quarter view + click-through; migration honest empty states; derived availability unlocked/in-flight; **timing change updates derivation**; customer interval + blockers; TS refusal; **milestone edit reflected in both views**; §55 blank-screen guard active on every test.
**New permanent JS gate:** `tests/js/test_web_esm_syntax.py` — feeds every `web/**/*.js` to Node as an explicit module. **Verified defect in the old practice:** plain `node --check` silently *passes* files containing broken syntax + `import` (reproduced minimally), which had masked the Phase 4 `crossAnalysis.js` paren bug and a Phase 5 bug in `roadmap.js` (two one-paren-short nested `el()` chains, both fixed; found via browser-side import bisection + real ESM parse).

**Regression:** all Phase 3 + Phase 4 suites green — **74/74 combined** (`pytest tests`).

## 7. Visual regression evidence

`docs/evidence/phase5/` (1440×900, seeded reference-fixture data):
`roadmap_full.png` (hierarchy + expanded drilldown + milestone lines labelled once + legend), `roadmap_horizon_0_6.png`, `roadmap_outcome.png`, `migration.png` (3 bands + derived intervals + shared milestones + customer interval table).

## 8. Known gaps / missing governed data

- **Milestones:** table empty in dev; functionality + API live; historical M1–M6 recovered as test fixtures only. Product must supply the governed milestone list (D2).
- **Customers:** table empty; model/API/UI ready; governed dataset awaited (D3). No invented customers anywhere.
- **Default Roadmap population is empty** until Product sets Roadmap Admission = COMMITTED on real caps (D-R3): the governed dataset currently has 133 NULL + 2 CANDIDATE. The empty state explains the switch.
- Roadmap bars render for caps **with** timing only (timing NULL = not yet planned — visible in Backlog/Cross-analysis, not as bars).

## 9. Product decisions required for Phase 6 (non-blocking, defaults shipped)

| ID | Decision | Shipped default |
|---|---|---|
| D-R1 | Middle hierarchy level "Big Rock / Market" mapping | shared-common-core band + per-governed-market bands (see spec §7) |
| D-R2 | Tail window | months 24–26 |
| D-R3 | Default population COMMITTED → empty until Product commits | shipped with explanatory empty state |
| D-R4 | Outcome narrative granularity | one versioned text block per horizon |
| D-M1 | "Unlocked" semantics | unlocked-before-interval vs in-flight split |
| D-M2 | Milestone scope semantics | global/category (scope_ref = category name); market scope deferred until governed milestones exist |

## 10. Commits

Phase 5 ships as small logical commits (recovery spec → schema/API → roadmap view → migration view → tests → checkpoint) ending at the push of `main`.

## 11. Recommendation for Phase 6

With Roadmap + Migration live on canonical data, the next natural increment is the governed-data on-ramp: bulk milestone import (Product-supplied CSV), admission commit workflow (CANDIDATE→COMMITTED transition with audit), and Cloud Run/Cloud SQL deployment hardening — all within the existing schema; no redesign required.
