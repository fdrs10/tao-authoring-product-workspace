# TO_BE_DELIVERABLE_DATA_MAPPING

**Date:** 2026-10-16

## Enforced mapping: Product Truth → Deliverable

| Deliverable | Data sources | Missing-data behaviour |
|---|---|---|
| **D1** | `sources` + `source_evidence` + `capability_candidates` + `capabilities` (active) + Ideation lens assignments | Sections render "Awaiting Product data" when evidence/source data is absent; "Product decision required" when no Target Scope admission exists |
| **D2** | `capabilities` (active) + `features` + `capability_markets` + `product_review_status` + `traceability_status` | Feature Composition section renders "Awaiting Product data" when no Features exist |
| **D3** | `capabilities` (active, admitted) + `roadmap_timing` + `features` + `milestones` | Roadmap timeline renders "Awaiting Product Roadmap Admission" when no capabilities are admitted; M1–M6 always render |
| **D4** | `milestones` + `roadmap_timing` (active) + `capabilities` (COMMITTED) + `customers` | Milestone sections render from canonical dataset; availability renders 0 when no COMMITTED capabilities |
| **D5** | `customers` + `customer_capabilities` + `customer_features` (new) + `roadmap_timing` + `milestones` | Readiness derived; missing plan fields render "Awaiting Product data" |
| **D5a** | Selected D5 reports packaged | Requires governed customer records; refuses ungoverned customer IDs |

## Product Narrative Blocks (§38)

The following narrative blocks are stored as Product-owned data (not hardcoded):

| Block | Storage | Consumed by |
|---|---|---|
| Target Product Vision | `roadmap_outcomes` (horizon='v2-vision') or dedicated field | D1 §2 |
| Target Scope rationale | Per-candidate `product_rationale` + Product Review narrative | D1 §9, D2 |
| Roadmap rationale | Per-candidate or global `roadmap_notes` | D3 §2 |
| Migration approach | `milestones.description` + global migration notes | D4 §4 |
| Customer migration recommendation | `customers.notes` + per-interval narrative | D5 |

**Implementation:** the existing `roadmap_outcomes` table pattern is extended. Narrative blocks are Product-owned, versioned and audited — they are NOT hardcoded in report templates and NOT AI-generated.

## Readiness (§39)

For every report, the Reports screen shows:
- X/Y sections ready (AVAILABLE count)
- Missing Product data (which sections are INCOMPLETE and why)
- Open Product decisions (which sections are PRODUCT DECISION REQUIRED)
- Clicking a missing item navigates to the relevant workspace where practical

## PM work progressively completes reports (§41)

The PM's normal work (enriching Candidates, setting Product Review, assigning MoSCoW, setting Roadmap Admission, composing Features, editing Customer Plans) directly feeds D1–D5. No separate report-authoring step is needed.
