# CAPABILITY_CANDIDATE_GOVERNANCE — working rules for the active Candidate set

**Applies to:** the 34 Capability Candidates (population `SOURCE_ANALYSIS_CANDIDATE`) and any later promotions.

## 1. Identity

- Candidate ID = the governed analysis **Family ID** (F01–F34) — stable, never reused.
- The Candidate's working capability row carries `CAND-<FamilyID>` (e.g. `CAND-F01`) in `capabilities`. CAP-xxxx numbering is reserved for the later canonical baseline (post Source-reconciliation + Product review).

## 2. Ideation disposition (§9)

| Disposition | Meaning |
|---|---|
| `ACTIVE FOR IDEATION` | in the working Ideation population (default for all 34) |
| `NOT SELECTED FOR IDEATION` | Product decided the candidate does not continue — **record kept, never deleted** |

Changing disposition requires: Product actor (X-User-Ref), **rationale** (≥5 chars, 422 otherwise), optimistic version (409 on stale), audit event. The funnel active count follows the disposition (34 ⇄ 33 …).

## 3. Promotion (§8)

Analysed evidence that did not enter the initial 34 can be promoted:

`POST /api/candidates/{any-candidate}/promote { evidence_id, name, rationale, markets? }`

- Requires **Product rationale** (422 otherwise) and a governed `evidence_id` (404 otherwise).
- Creates a new family (F-sequence) + active capability row with **full lineage** (source evidence → source) and an audit event.
- Promotion is never silent: the funnel active count changes and the promotion is inspectable.

## 4. Focus set (§7)

The 15 Cross-market Focus Capabilities are a **Product recommendation** — `is_focus=true` + `focus_markets` (per-market focus sets preserved from the analysis). The Ideation view offers **All Candidates | Focus Capabilities**; Focus is a prioritisation view, never a destructive filter. Per-market focus sets (7 capabilities each) are preserved as analysis data.

## 5. MEXCBT / Uchida (§15)

First-class dimension: per-signal relevance in the evidence layer, `mexcbt_signals` per candidate, a dedicated Focus set, and independent filters (Ideation "MEXCBT / Uchida only", `GET /api/candidates?mexcbt_only=1`, `GET /api/evidence?mexcbt=…`). Relevance is only ever what the governed analysis recorded — never invented.

## 6. Downstream boundaries (§17)

Candidates are **considered** work: Roadmap Admission, Backlog commitment and Migration eligibility remain explicit Product decisions downstream. Nothing in this layer auto-commits a Candidate to the Roadmap or Migration.
