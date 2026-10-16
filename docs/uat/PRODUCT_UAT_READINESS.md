# PRODUCT_UAT_READINESS — DEV candidate v1.0

**Baseline:** tag `dev-candidate-v1.0` → commit `04f520845a8c0a12438fb3e5caed43ad116c462d`
**Automated tests:** 80/80 (26 API · 38 UI E2E · 10 ESM gate · 6 phase-6) — see OVERNIGHT_READINESS_REPORT.md
**Verdict:** **READY WITH WARNINGS** — see §verdict below and `docs/checkpoints/OVERNIGHT_READINESS_REPORT.md`.

## What is ready for Product use

| Area | State |
|---|---|
| Sources & Evidence (list, document metadata, extracted→canonical, SRC-JIRA-001 evidence) | ✔ verified on governed data |
| Ideation 01–06 (V2 Position + figure, V1, 3.x, New Needs, Discontinued, Cross-analysis) | ✔ |
| Product Backlog (Must default 33 / All 135, filters) | ✔ |
| Roadmap (Full/0–6m/7–24m/Tail, expand, drag/resize/snap, milestones, Quarter, Outcome) | ✔ (two defects found and fixed overnight) |
| Migration Path (3 bands, derived availability, shared milestones, customer intervals) | ✔ |
| Universal CAP modal (from every view; NULL budgets; Jira link/unlink) | ✔ |
| Export / audit / concurrency | ✔ |
| Local launcher | ✔ `./start-local.sh` (tested cold + warm) |

## Warnings (do not block UAT)

1. **Roadmap default view is empty by design** — governed data has 0 COMMITTED caps (133 UNSET, 2 CANDIDATE). Use *Admission · All*. Product should start committing admissions during UAT (D-R3).
2. **Milestones & customers datasets are pending** (D2/D3) — functionality live, data honestly absent.
3. **Dense roadmap lanes overlap bars** in shared/market bands when many caps share months — expand a band (v10 behaviour) for individual access. Enhancement candidate.
4. **Audit events are write-only** in the API (recorded with actor/before/after; no read endpoint yet) — enhancement candidate.

## Fixed during overnight QA (included in this candidate's working tree, tag untouched)

- Drill-down overlay trapped navigation (could not click nav links while a pane was open).
- Roadmap "Admission · All" showed an empty roadmap (API default swallowed the omitted param).

Both have regression tests (`tests/ui/test_ui.py`).
