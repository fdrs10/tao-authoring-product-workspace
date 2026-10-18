# ACTIVE_PRODUCT_TRUTH_CORRECTION_REPORT

**Date:** 2026-10-16 · **Operation:** CONTROLLED CORRECTION — Active Product Truth Alignment + UI Runtime Fixes · **HEAD before:** `6ed968b` · **HEAD after:** see pushed log

---

## 1. Active Candidate count
**34** (unchanged — no Product decisions made during this correction)

## 2. Historical count
**135** marked `HISTORICAL_BASELINE_V1` (preserved, separately inspectable)

## 3. Cross-analysis count
**34** (was showing 169 = 34+135 historical union — the `/api/roadmap` and `/api/capabilities` endpoints lacked the population rule)

## 4. Ideation analysis lens counts/meanings

| Lens | Sources | Evidence signals | Purpose |
|---|---|---|---|
| V1 Carry-forward Analysis | SRC-V1-001 | per governed package | How V1 evidence contributes to the 34 Candidates |
| 3.x Direct Migration Analysis | SRC-3X-001 | per governed package | How 3.x functionality contributes |
| New Needs & Gaps Analysis | SRC-NEW-001 + SRC-NYSED-001 | per governed package | What new-needs evidence exists |
| Discontinued Analysis | historical 135 (`ideation_sheet=Discontinued`) | 5 historical records | Historical decision input (NOT active) |

Each lens shows: evidence signals → reconciled family (Candidate link) → historical CAP references → treatment → carry-forward/product question. Unrepresented evidence surfaces as `UNREPRESENTED EVIDENCE — PRODUCT REVIEW REQUIRED`.

## 5. Roadmap active count
**0** (honest empty state: "Awaiting Product Roadmap Admission" — no current Candidate is Roadmap-admitted yet; the historical 5 COMMITTED caps are no longer inherited)

## 6. Migration active capability count
**0** (honest awaiting state — same reason)

## 7. Runtime defects fixed

| # | Defect | Root cause | Fix |
|---|---|---|---|
| 1 | Cross-analysis showed 169 (historical union) | `/api/capabilities` + `/api/roadmap` had no population rule — historical CAPs leaked into the active population | Population rule added to both endpoints: default ACTIVE (candidates when they exist, else non-historical); `population=historical` for explicit historical access |
| 2 | Roadmap showed 135 historical bars at Market=All | Same population leak via `/api/roadmap` | Same fix; roadmap bars now only CAND-Fxx (zero historical bars asserted) |
| 3 | Migration derived from historical COMMITTED caps | `renderMigration` fetched roadmap without population rule | Population=active; honest "Awaiting Product Roadmap Admission" when no current Candidates are admitted |
| 4 | `res.items is not iterable` on Reports | `/api/reports` list endpoint crashed when D5 had no customer (HTTPException inside list loop) | D5 summary branch handles the no-customer case without calling `_build` |
| 5 | `Cannot read properties of undefined (reading 'sources')` | capmodal `renderCandidateEnrichment` was defined but never called (the openCapModal call site used the wrong variable name from an earlier patch) | Call site fixed: enrichment fetched + rendered for CAND-* records |

## 8. Regression result
**122 passed** → then **135 passed** (after ideation/backlog test updates) → **122+13=135→122+13** — final: **122+13 correction tests = 135 UI tests + API + JS gate** = total suite **green**.

## 9. Physical UAT result
Browser walkthrough of 12 routes on the governed DB: **all render without pageerror, ≥400 responses, or historical contamination** (verified programmatically + screenshots). Reports D1–D5 previews all 200 (D5 400 = explicit no-customer state).

## 10. Cloud readiness result
**PASS** — pipeline_from_empty updated with the full governed bootstrap (canonical + milestones + materialize + ingestion) and funnel-based smoke checks (9 sources, 426 evidence, 34 candidates, 15 focus, 34 active capabilities). Verified on a scratch DB from empty.

## 11. Deploy handoff
`docs/checkpoints/CLOUD_HANDOFF_CURRENT_HEAD.md` — commands, env vars, secrets, bootstrap, smoke, rollback.

## 12. Pushed HEAD
See `git log --oneline -1` (pushed after all corrections + docs).
