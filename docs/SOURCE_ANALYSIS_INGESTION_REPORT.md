# SOURCE_ANALYSIS_INGESTION_REPORT — CONTROLLED OPERATION complete

**Date:** 2026-10-16 · **Operation:** INGEST FINAL SOURCE ANALYSIS INTO PRODUCT WORKSPACE · **Status:** COMPLETE — validated, operational

## 1. Exact package used

`TAO_Authoring_Capability_Evidence_Focus_Guide_v1_4_VERIFIED.zip` — MD5 `e4d70bb92e7bb14119bf08b8465f111f` (10,948,159 B). Governed copy stored at `data/source-analysis/` (zip + `TAO_AUTHORING_ANALYSIS_v1_4_VERIFIED.html` + extracted datasets at `data/source-analysis/v1_4/`, minus the duplicate 11 MB OECD PDF which already lives in the artifact store). Inventory: `docs/SOURCE_ANALYSIS_INGESTION_INVENTORY.md`.

## 2–5. Exact counts (governed, verified in DB + manifest)

| Metric | Count |
|---|---|
| Sources (governed registry, incl. 2 new: SRC-NYSED-001, SRC-STRATEGY-001) | **9** |
| Evidence signals (`source_evidence`) | **426** |
| Capability Candidates (`capability_candidates`, population `SOURCE_ANALYSIS_CANDIDATE`) | **34** |
| Cross-market Focus Capabilities (`is_focus`) | **15** |
| Historical baseline marked `HISTORICAL_BASELINE_V1` | **135** |

## 6. Historical baseline archival status

The previous 135 capabilities are **preserved in place**, marked `population='HISTORICAL_BASELINE_V1'` — inspectable via `GET /api/capabilities?population=historical` and the package's `current_canonical_135.json`. They are excluded from the default (active) population on every screen and report; no screen combines them with the active Candidate set (population rule tested).

## 7. Import manifest

`data/import-manifests/TAO_Authoring_Capability_Evidence_Focus_Guide_v1_4_VERIFIED.json` — package id, MD5, sources (9), evidence (426; re-run delta 0), candidates (34; re-run delta 0), active rows (34), historical marked (135), focus (15), warnings [], conflicts []. Re-running the ingestion is idempotent (verified: second run inserts 0).

## 8. Validation results (§21) — all pass (see `tests/ui/test_source_analysis.py`, 11 tests)

Sources: 9 governed registered; artifacts materialised + connected (Open Source works; OECD PDF, NYSED/STRATEGY docx, feature lists, gap analysis). Evidence: 426 with Source lineage on every record; no silent loss (Σ candidate signals = 426). Candidates: 34; active Ideation population = 34; old 135 not mixed in. Focus: 15, subset of Candidates, no duplicates. Promotion: evidence → new Candidate with rationale + audit + count change (F36 test path). Removal: disposition NOT SELECTED FOR IDEATION (rationale + audit + not deleted). Markets: relationships preserved; MEXCBT/Uchida filters independently. Downstream: Ideation consumes the 34; Roadmap does not auto-commit; Reports consume current truth.

## 9. Regression

**122 passed** — the complete pre-existing suite (111) plus 11 new ingestion/funnel tests. One semantic consequence updated: the ideation index now leads with "00 · Capability Candidates" (7 entries — asserted).

## 10. Screenshots

Captured during the operation: funnel banner + registry tabs, evidence universe, capability analysis, 34-candidate Ideation view (All/Focus/MEXCBT toggles) — `docs/evidence/` (source-analysis runs) alongside the UAT-structural set.

## 11. Commit state

Ingestion script (`scripts/import/ingest_source_analysis.py`), migration 0006, funnel API (`app/routers/funnel.py`), population rule, Ideation 00 view, Sources funnel tabs, tests, manifest + docs — committed and pushed after `fdacf39`.

## 12. Genuine ambiguity found in the governed package

- Candidates carry **no narrative description** — the report/UI render the consolidation provenance ("Consolidated from N signals…") and the field awaits Product definition.
- **No explicit per-row evidence→family linkage** exists in the package (the consolidation lives in the analysis narrative; candidate `Signals` counts sum to 426). Per-row linkage will be recorded when Product reviews each family.

**Stopping point honoured:** no Roadmap prioritisation, no automatic Admission changes, no Customer Migration Plans created.
