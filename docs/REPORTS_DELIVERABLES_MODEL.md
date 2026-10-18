# REPORTS_DELIVERABLES_MODEL — governed reports over Product Truth

**Date:** 2026-10-16 · **Model:** `Application Product Truth → Report Contract → Generated Report`

## 1. Position

Reports are **generated representations** of the canonical Product Truth held in PostgreSQL. The application remains the only Product Truth; a generated report is a **versioned snapshot**. Nothing in the report layer can mutate Product Truth (verified by test).

## 2. The five November deliverable contracts

| ID | Report | Target delivery | Sections | Consumes |
|---|---|---|---|---|
| D1 | Authoring Product Definition — Ideation & Target Scope | 30 Oct 2026 | 11 | Sources + Ideation + Cross-analysis + Target Scope |
| D2 | TAO Studio Creator V2 — Product Backlog | 30 Oct 2026 | 10 | Capabilities + Features + Markets + Product Review + Traceability + Admission |
| D3 | TAO Studio Creator V2 — Product Roadmap | 13 Nov 2026 | 11 | Backlog + Roadmap timing + Features + Markets + M1–M6 |
| D4 | TAO 3.x → TAO Studio — Common Migration Path | 13 Nov 2026 | 15 | Roadmap + M1–M6 + derived migration availability/dependencies |
| D5 | Customer Migration Plan (**one per governed customer**) | 20 Nov 2026 | 19 | Customer + required capabilities + Features + Roadmap + M1–M6 + blockers + readiness |

## 3. Section states (§4)

Each section renders one state, computed from data:

| State | Meaning |
|---|---|
| `AVAILABLE` | underlying canonical data present; section fully rendered |
| `INCOMPLETE` | underlying data missing → the section renders **"Awaiting Product data"** explicitly |
| `PRODUCT DECISION REQUIRED` | the section depends on a decision Product has not made (e.g. Target Scope membership, migration interval) |
| `NOT APPLICABLE` | genuinely not applicable (e.g. Relevant Features when none composed) |

**Never** is missing content filled with generated assumptions (§10).

## 4. Generation & versioning (§9)

- `POST /api/reports/{rid}/generate` (optional `customer_id`, or `customer_ids` for the Pilot Set) records a **generation snapshot**: `report_generations(report_id, report_type, version, actor, generated_at, params, source_snapshot, html)`.
- `version` = per-report increment (v1, v2, …); `source_snapshot` = counts + max capability version at generation time.
- `GET /api/reports/{rid}/generations` = history. Preview (`GET …/preview`) does NOT record a generation — it is a live representation labelled as such.
- HTML output is print-friendly (`@media print`, "Print / Save as PDF" button). DOCX deliberately not implemented yet.

## 5. Pilot Set (§3)

`POST /api/reports/PILOT/generate {"customer_ids": [...]}` packages the selected D5 plans into one deliverable. Rules: only **governed customer records** can be selected — unknown IDs (e.g. the intended-but-ungoverned DEPP / INVALSI / NSA / NCCER) are refused with `unknown_customers` (422); nothing is created automatically.

## 6. Data mappings (§8)

- D1 ← `sources` (+extracted counts, artifact availability), capabilities by `ideation_sheet` (V1 / 3.x / New Needs / Discontinued), cross-analysis traceability, admission decisions, market census.
- D2 ← capabilities (all §8 classification fields), features, market coverage, Product Review + provenance, traceability, admission; open gaps (review/traceability/admission counts).
- D3 ← roadmap timing (timeline + horizons + per-category), MoSCoW sequencing, features (derived coverage), market views, M1–M6 (canonical), dependency/risk counts.
- D4 ← milestone baseline (one section per M1–M6, verbatim from the governed dataset), availability-by-milestone derivation over COMMITTED capabilities, dependencies/conditions, customer blockers/exceptions (from governed customers only), transition approach.
- D5 ← the customer's plan model (`CUSTOMER_MIGRATION_PLAN_MODEL.md`): context, need, required capabilities with availability-by-interval + dependency reasons + features, milestones, migration fields, validation, readiness, next actions.
