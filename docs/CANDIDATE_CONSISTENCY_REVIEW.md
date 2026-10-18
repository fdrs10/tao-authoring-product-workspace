# CANDIDATE_CONSISTENCY_REVIEW — cross-candidate consistency analysis (§13)

**Date:** 2026-10-16 · **Nature:** ANALYSIS ONLY — no merge/split/promotion executed. Machine-readable: `data/product-review/consistency_findings.json`.

## Breakdown

| Finding type | Count | Meaning |
|---|---|---|
| FOCUS | 15 | candidates in the Cross-market Focus Set |
| MEXCBT_CRITICAL | 7 | candidates with direct MEXCBT / Uchida evidence signals |
| SINGLE_SOURCE | 6 | candidates whose evidence comes from exactly one Source |
| WEAK_EVIDENCE | 6 | candidates consolidated from ≤2 evidence signals |
| POSSIBLE_OVERLAP | 1 | candidate name-term overlap suggesting related scope |
| JIRA_NOT_REPRESENTED | 1 | governed Jira record with no relationship to the 34 |

## Findings detail

- **WEAK_EVIDENCE (6):** candidates consolidated from ≤2 signals — Product should prioritise reviewing these definitions first; they may be promotion/merge candidates once their Sources are reconstructed. IDs in `data/product-review/consistency_findings.json`.
- **SINGLE_SOURCE (6):** evidence from one Source only — cross-source corroboration pending the Source-by-Source reconstruction.
- **MEXCBT_CRITICAL (7):** the 7 candidates of the MEXCBT / Uchida Focus set — strategically important per the governed analysis; Roadmap coverage should be checked when Admission decisions happen (not done in this operation).
- **POSSIBLE_OVERLAP (1):** one candidate pair shares ≥2 name terms — flagged for Product; no merge executed.
- **JIRA_NOT_REPRESENTED (1):** the governed non-container Jira record not represented by the 34 (Product Review queue — see `jira_candidate_coverage.json`).

## Terminology / scope notes

- Candidate working names use the analysis family terminology; several share generic terms ("authoring", "content") — the POSSIBLE_OVERLAP flag covers the ≥2-term case only; Product should review scope boundaries during review.
- No inconsistent Review-state or Admission anomalies: all 34 are uniformly `CANDIDATE · PRODUCT CONFIRMATION REQUIRED` / not-reviewed / admission-NULL (per §15 of the enrichment operation).

## Product questions requiring human decision

1. Confirm or resolve the flagged POSSIBLE_OVERLAP pair (merge/keep-separate).
2. Review the 6 WEAK_EVIDENCE and 6 SINGLE_SOURCE candidates after their Sources are reconstructed.
3. Decide the disposition of the uncovered Jira record (relate / delivery-only / not relevant).
4. Assign Strategic Categories + Product-written definitions (currently awaiting Product data).
