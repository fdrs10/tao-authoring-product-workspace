# AUTHORING SCOPE AUDIT

**Date:** 2026-10-15 · **Phase:** 1 · **Scope gate:** execution prompt §4 + KINCHI_MASTER_HANDOFF §2 (Authoring function only)
**Method:** every one of the 135 canonical capabilities was reviewed individually (ID, name, description, category, ideation sheet) against the gate: *belongs to, enables, governs or materially supports Authoring*. No capabilities were deleted. Questionable CAPs are **flagged for Product review only** (§4 requirement).

## 1. Verdict summary

| Classification | Count | Action |
|---|---:|---|
| In scope — no question | 130 | Keep |
| In scope — flagged for Product review | 5 | Keep, review rationale below |
| Out of scope — removal candidate | **0** | — |

No proctoring, candidate/session management, learner administration, generic delivery operations, payments/commerce, tenant provisioning, or Portal capabilities exist in the register. The corpus is Authoring-clean.

## 2. In scope without question (130)
All remaining capabilities fall squarely within the enumerated in-scope families: item/test authoring, assembly, professional authoring workflow, content banking **for Authoring**, authoring metadata/taxonomy, authoring search/discovery, review & QA, authoring permissions (CAP-0058), templates/blueprinting, authoring-related psychometrics (CAP-0049/0059/0067), standards/interoperability (QTI/CASE/API family), AI-assisted authoring (generation, tagging, evaluation families), authoring extensibility (CAP-0068, 0075), and authoring-relevant provenance (CAP-0081). Full register: `data/canonical/capabilities.json`.

Noted sub-domain justifications (kept, not flagged):
- **CAP-0022 / CAP-0023 / CAP-0027 / CAP-0028** (item selection, random selection, test-taker tools, delivery-related settings): these *execute at delivery time but are configured by authors* — authoring of behavior, in scope per §4 ("assembly", "authoring configuration").
- **CAP-0069 / CAP-0070 / CAP-0101–0103** (publishing to TAO 3.x / Advance / Authoring): the author-side act of publishing authored content; a governed authoring workflow endpoint. Delivery-domain operation itself is not a capability here.

## 3. Flagged for Product review (5) — do NOT delete (§4: flag, don't delete)
| CAP | Name | Why kept in scope | Why flagged for review |
|---|---|---|---|
| CAP-0071 | Delivery creation from a test | Author-side creation step from authored test | Verbs a *delivery* object; boundary between authoring and delivery operations needs explicit Product classification (dependency vs capability) |
| CAP-0126 | AI-assisted grading and marking | Author-configured grading support; competitor-backed | "Grading/marking" can read as delivery-time scoring operations; confirm intended frame is authoring-time configuration/assistance |
| CAP-0128 | Speech scoring | Research signal (Cambium); could support authoring of speaking-type items | Automated speech scoring is arguably a delivery/scoring-engine capability, not an authoring capability; confirm Authoring frame or mark as dependency |
| CAP-0131 | Personalised assessment support | AI-assisted authoring intent ("while keeping pedagogy human-led") | Wording implies learner-facing adaptive interactions at delivery; confirm the authored-artifact frame vs runtime personalization |
| CAP-0133 | Process-oriented assessment | OECD-backed design orientation; affects what authors can author | Phrased as an assessment practice ("assess the process used by learners"); confirm it models authoring support for process-oriented items, not delivery analytics |

## 4. Governance gaps tied to this register (carried from reconciliation report)
- **CAP-0134 / CAP-0136**: in scope by content, but lack ideation sheet, review status, and registered source (SRC-JIRA-001). Product to complete governance metadata; see DATA_IMPORT_AND_RECONCILIATION_REPORT.md §10 G1/G2.
- **Discontinued set** (CAP-0040/0041/0065/0066/0073, decision `DISCONTINUE / VALIDATE`): correctly represented as the OUT view; they carry placeholder roadmap timing (G3) — timing should be cleared or explicitly marked "no placement" by Product.

## 5. Outcome
- The register may enter Phase 2 (DB schema + migrations) as-is: **135 capabilities = 130 clean + 5 review-flagged + 0 removal candidates**.
- A future non-Authoring capability must not be admitted without an explicit Product decision (tests/ACCEPTANCE_CRITERIA.md — Scope).
- Recommendation-only (no data change made): record dependency-type relationships for CAP-0071/0126/0128/0131/0133 once a `relationship_type` exists, instead of deleting or distorting the capabilities.
