# REPORT_TEMPLATE_CONTRACTS — fixed section structures (§2)

These are the **predefined report templates**. A generated report must follow its contract's section structure exactly; sections may be incomplete (explicitly stated) but never reordered, removed, or filled with generated assumptions.

---

## D1 — Authoring Product Definition — Ideation & Target Scope
**Target delivery: 30 October 2026**

| # | Section | Source mapping |
|---|---|---|
| 1 | Executive Summary | counts: capabilities, categories, sources, extracted SCs |
| 2 | Product Vision and Authoring Objective | approved V2 Position reference (fixed objective statement) |
| 3 | Sources and Evidence | `sources` + artifact availability + extracted counts |
| 4 | TAO Studio V1 Carry-forward | capabilities `ideation_sheet='V1 Carry-forward'` |
| 5 | TAO 3.x Direct Migration | `ideation_sheet='3.x Direct Migration to V2'` |
| 6 | New Needs & Gaps | `ideation_sheet='New Needs & Gaps / Developments'` |
| 7 | Discontinued | `ideation_sheet='Discontinued'` |
| 8 | Cross-analysis | traceability coverage (source-traceable vs pending) |
| 9 | Target Authoring V2 Scope | capabilities with Roadmap Admission (PRODUCT DECISION REQUIRED when none) |
| 10 | Market and MEXCBT / Uchida Relevance | market census |
| 11 | Open Product Decisions | pending review / traceability / admission counts |

## D2 — TAO Studio Creator V2 — Product Backlog
**Target delivery: 30 October 2026**

| # | Section | Source mapping |
|---|---|---|
| 1 | Executive Summary | counts |
| 2 | Product Backlog Overview | fixed scope statement |
| 3 | Canonical Capabilities | full capability table (classification fields) |
| 4 | Strategic Categories | per-category counts |
| 5 | Market Coverage | per-market counts |
| 6 | Feature Composition | `features` (+ per-feature capability counts) |
| 7 | Product Review Status | reviewed vs not-reviewed counts |
| 8 | Source / Evidence Traceability | TRACEABILITY_REVIEW_REQUIRED list |
| 9 | MoSCoW and Roadmap Admission | distribution table |
| 10 | Open Decisions and Gaps | admission/review/traceability pending counts |

## D3 — TAO Studio Creator V2 — Product Roadmap
**Target delivery: 13 November 2026**

| # | Section | Source mapping |
|---|---|---|
| 1 | Executive Summary | timed capability counts |
| 2 | Roadmap Principles | confirmed hierarchy statement (Strategic Category → Capability; market = filter) |
| 3 | Roadmap Timeline | `roadmap_timing` per capability + version |
| 4 | Full / 0–6m / 7–24m / Tail Horizons | horizon buckets |
| 5 | Capabilities by Strategic Category | per-category timed counts |
| 6 | Priorities and Sequencing | MoSCoW distribution + timing order |
| 7 | Feature Composition View | features + derived coverage windows |
| 8 | Market Views | per-market applicable timed capabilities |
| 9 | Dependencies | untimed capabilities list |
| 10 | M1–M6 Alignment | **canonical milestone dataset** (never duplicated) |
| 11 | Risks and Open Product Decisions | admission/timing pending counts |

## D4 — TAO 3.x → TAO Studio Authoring — Common Migration Path
**Target delivery: 13 November 2026**

| # | Section | Source mapping |
|---|---|---|
| 1 | Executive Summary | milestone + COMMITTED counts |
| 2 | Migration Objective | fixed objective statement |
| 3 | Current → Target Authoring Model | fixed model statement (TS not canonical) |
| 4 | Common Migration Principles | fixed principles (Roadmap → capabilities → milestones → customers) |
| 5–10 | M1 … M6 (one section per milestone) | **governed milestone dataset** rows (ID/name/date/position/description) |
| 11 | Capabilities and Value Available by Milestone | availability derivation over COMMITTED capabilities |
| 12 | Roadmap Dependencies | COMMITTED capabilities without timing |
| 13 | Migration Conditions | fixed non-capability conditions statement |
| 14 | Common Blockers and Exceptions | governed customers' blockers/exceptions |
| 15 | Customer Transition Approach | customer count + D5 reference |

## D5 — Customer Migration Plan (one report per governed customer)
**Model ready: 20 November 2026**

| # | Section | Source mapping |
|---|---|---|
| 1 | Executive Summary | customer + readiness |
| 2 | Customer Context | ID, name, relevant markets |
| 3 | Current Authoring Situation | current_use, min functionality today |
| 4 | Current TAO Environment | current_environment |
| 5 | Required Functionality | min functionality in Studio, desired outcome, value opportunity |
| 6 | Required Canonical Capabilities | customer_capabilities + timing + availability + dependency |
| 7 | Relevant Features | features composed around required capabilities |
| 8 | Product Roadmap Availability | availability summary (Roadmap truth consumed) |
| 9 | Proposed Migration Milestone / Interval | earliest_milestone_interval |
| 10 | Proposed Migration Window | proposed_migration_window |
| 11 | Customer-specific Dependencies | customer_dependencies |
| 12 | Blockers | blockers |
| 13 | Assumptions | assumptions |
| 14 | Exceptions | exceptions |
| 15 | Customer Feedback / Evidence | customer_feedback |
| 16 | Migration Readiness | derived readiness + reason |
| 17 | Product Decisions Required | derived from gaps (interval/timing) |
| 18 | Validation Status | validation_status + product notes |
| 19 | Next Actions | derived from readiness |

---

## Pilot Set (§3) — not a contract

`PILOT` packages selected D5 reports into one deliverable. Initial intended pilot customers: DEPP, INVALSI, NSA, NCCER — **only when governed records exist**; the generator refuses unknown customers (422 `unknown_customers`).
