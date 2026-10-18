# REPORTS_LAYER_IMPLEMENTATION_REPORT

**Date:** 2026-10-16 · **Implements:** FINAL STRUCTURAL STEP — governed Reports / Deliverables · **Regression:** **111 passed** (30 API · 54 UI E2E · 10 ESM gate · 10 reports · 7 November) — all prior suites preserved.

---

## 1. Implementation

| Layer | What was built |
|---|---|
| Schema | Alembic `0005_report_generations`: `report_generations(generation_id, report_id, report_type, version, actor, generated_at, params jsonb, source_snapshot jsonb, html text)` + index. Applied to dev + CI DBs. |
| Contracts | `app/reports.py`: D1–D5 contracts (fixed target dates, predefined sections), canonical-data section generators with `AVAILABLE / INCOMPLETE / PRODUCT DECISION REQUIRED / NOT APPLICABLE` states, publication HTML renderer (title page, ToC, meta, print CSS, "Print / Save as PDF"). |
| API | `GET /api/reports` (contracts + section completeness + status + last generation) · `GET /api/reports/{rid}/preview[?customer_id=]` (live publication HTML — labelled as preview, not recorded) · `POST /api/reports/{rid}/generate` (records a versioned snapshot; optional `customer_id` / `customer_ids`; PILOT packaging) · `GET /api/reports/{rid}/generations` (history incl. source snapshot). |
| UI | **REPORTS / DELIVERABLES** main-nav section (`#/reports`): one compact row per contract — ID, name, target date, X/Y sections available, status badge, last generated (vN by actor) — with **Preview Report | Generate HTML**; D5 adds **Select customer** (governed records only) and **Generate Customer Migration Pilot Set**. |
| Governance | Generating records a snapshot (version per report, actor, params, source counts + max capability version) and **never mutates Product Truth** (tested: capability count/version/name unchanged across generation). |

## 2. Report contracts & data mappings

`docs/REPORT_TEMPLATE_CONTRACTS.md` — fixed section structures per contract with the exact source mapping for every section. D4's M1–M6 sections come from the governed canonical milestone dataset (tested: names in the preview match `GET /api/milestones`).

## 3. Data rules honoured (§8/§10)

- All generators read canonical PostgreSQL data only; no independent report truth.
- Missing data renders **"Awaiting Product data"**; decision-dependent sections render **"Product decision required"** (e.g. D1 Target Scope with no admissions; D5 without an interval). Verified in preview content.
- Pilot Set refuses ungoverned customers (DEPP/INVALSI/NSA/NCCER → 422 `unknown_customers`); only selected governed records are packaged.

## 4. Tests (§11) — `tests/ui/test_reports.py` (10)

Contracts + target dates + section totals (D1–D5) · D4 M1–M6 canonical + TS model absent · D2/D1 previews consume canonical data (CAP + source IDs) and are print-friendly with version metadata · missing data explicit · generation versioning/history/snapshot + **no Product-Truth mutation** · D5 requires a governed customer (400/404) · D5 uses the customer's required capabilities and **reflects a Roadmap timing change** on regeneration · Pilot Set 422 on intended-but-ungoverned customers and uses selected governed customers only.

## 5. Screenshots (`docs/evidence/reports-deliverables/`)

01 Reports landing · 02 D1 preview · 03 D2 preview · 04 D3 preview · 05 D4 with M1–M6 · 06 D5 empty/no-customer state · 07 D5 populated (test-fixture customer) · 08 Pilot Set selection.

## 6. Remaining Product decisions

- Section content wording for D1 "Product Vision and Authoring Objective" currently carries the fixed approved objective statement — Product may want a longer narrative.
- Pilot Set customer selection UI is single-select; multi-select packaging is supported by the API when Product confirms the pilot list.
- DOCX output deliberately not implemented (contract §7).

## 7. Commits

Reports layer (schema + module + router + UI + tests + docs) lands as small logical commits after the November work; final pushed HEAD reported in the session log.
