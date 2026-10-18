# JIRA_CANDIDATE_COVERAGE_REPORT — Jira vs the 34 active Candidates

**Date:** 2026-10-16 · **Method:** deterministic classification from governed data only (§9) · **Machine-readable:** `data/product-review/jira_candidate_coverage.json`

## Coverage breakdown (28 governed Jira records)

| Class | Count | Meaning |
|---|---|---|
| D — NON-CAPABILITY / DELIVERY CONTAINER | 27 | Epics/containers/work-management records — not Product Capabilities |
| C — NOT REPRESENTED BY ACTIVE CANDIDATES | 1 | governed record with no supported relationship to the 34 |
| A — COVERED BY ACTIVE CANDIDATE | 0 | none yet: existing links point to the historical baseline |
| B — SUPPORTING / RELATED | 0 | no supported candidate-level relation recorded |
| E — PRODUCT REVIEW REQUIRED | 0 | — |

**Honest reading:** the governed Jira dataset is dominated by Epic/container records (D). Jira existence is delivery fact only — it implies no Product decision, no Admission, and no automatic promotion.

## Uncovered Jira work (§10 — Product Review queue)

| Jira key | Type | Why uncovered | Suggested review question |
|---|---|---|---|
| (see `jira_candidate_coverage.json`, class C_) | Story/Task | No governed Jira↔Capability relationship exists | Should this work relate to an active Candidate, stay delivery-only, or be treated as no longer relevant? |

Product may later decide: promote to Candidate · relate to an existing Candidate · supporting/delivery-only · no longer relevant. **Kimchi did not make that decision.**

## Rules applied

- A: linked (capability_jira) to a capability with `population='SOURCE_ANALYSIS_CANDIDATE'`.
- D: issue type/summary marks the record as Epic/container/placeholder.
- E: linked only to historical-baseline capabilities (none in the governed dataset — all governed links are container-classified, hence D first).
- C: no relationship at all.
- M:N cardinality preserved; deep links preserved; Jira existence never changes Roadmap Admission (tested).
