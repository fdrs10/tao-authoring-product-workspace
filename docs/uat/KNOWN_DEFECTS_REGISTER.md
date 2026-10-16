# KNOWN_DEFECTS_REGISTER — DEV candidate v1.0 (overnight QA 2026-10-16)

Categories: **Technical defect** (does not work) · **Product decision** (works, needs Product validation) · **Missing data** (not supplied) · **Enhancement** (future, not a blocker).

| ID | Category | Area | Description | Status | Evidence |
|---|---|---|---|---|---|
| QA-1 | Technical defect — **FIXED** | Sources / global | Drill-down overlay covered the sticky nav (`inset:0; z-index 500` over header `z-index 200`): navigation impossible while a pane was open | **Fixed** `db60b85` — overlay starts below the 41px header + clears on navigation; regression test `test_source_pane_does_not_block_navigation` | `docs/evidence/overnight/02-source-drilldown.png` (post-fix) |
| QA-2 | Technical defect — **FIXED** | Roadmap | "Admission · All" omitted the param → API applied its COMMITTED default → roadmap appeared empty on governed data | **Fixed** `db60b85` — All sends explicit empty admission; regression test `test_roadmap_admission_all_shows_all_states` | — |
| QA-3 | Enhancement | Roadmap | Dense shared/market lanes overlap bars when many caps share months (D-R1 duplicates bars per market band by design); individual access via band expand (v10 behaviour) | Open — possible Phase 7 improvement (e.g. lane bar stacking) | `docs/evidence/overnight/08-roadmap-full-expanded.png` |
| QA-4 | Enhancement | API | Audit events are recorded (actor/before/after/changed) but there is **no read endpoint** — Product cannot review history without DB access | Open — add `GET /api/audit` in a future phase | `scripts/ops/scenario_e_two_user.py` |
| QA-5 | Enhancement | Roadmap | With 199 bar placements, expanded bands push quarter headers out of the sticky row on long pages (scroll-to-find) | Open — cosmetic | `docs/evidence/overnight/08-roadmap-full-expanded.png` |
| QA-6 | Technical defect — **out of scope, historic** | (reference HTML) | v38.6 kept Roadmap/Outcome narratives and milestones in localStorage — superseded by server persistence; do NOT reintroduce | Closed by design (Phases 5–6) | RECOVERY_SPEC §5 |

## Verified-OK items that looked like defects
- 4 Jira tickets without CAP links (`PCR-139/117/201/215`) — all Epics/placeholder items; Jira ≠ Capability, correct.
- SRC-HTML-001 has 0 extracted source_capabilities — its capabilities were imported directly as canonical (verified against import files); use **View Extracted** on SRC-V1/3X/NEW/OECD/COMP.
- Roadmap shows 199 bars for 135 caps — D-R1 market-band placement by design (🟡 pending Product confirmation).
- "Open Source" pane shows metadata only — extracted list is under **View Extracted** (by design).
