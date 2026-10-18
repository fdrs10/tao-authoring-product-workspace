# TAO Authoring - Source & Capability Analysis v2.0

## Status

This is the source-first reconstruction baseline. It does **not** replace the current 135 canonical CAP baseline.

The analysis now covers nine governed sources and 426 in-scope Authoring source-capability/signals. The next controlled step is cross-source reconciliation (SAME / OVERLAP / SUPPORTS / EVOLVES / DISTINCT) and comparison with the current 135-CAP baseline.

## Governed Source Set

| Source | Owner / proposer | Evidence role | Extracted rows |
|---|---|---|---:|
| SRC-3X-001 - TAO Authoring feature list | Dragos Ivan | Existing product baseline | 83 |
| SRC-V1-001 - TAO Studio feature list | Dragos Ivan | Existing product baseline | 91 |
| SRC-GAP-001 - 3.x vs Studio gap analysis | Dragos Ivan | Comparative / gap evidence | 129 |
| SRC-NEW-001 - Strategic Initiative / New Developments | Internal / Product | Product need / customer evidence | 21 |
| SRC-COMP-001 - Competitor Intelligence | Internal strategic use | Market / competitor evidence | 14 |
| SRC-JIRA-001 - Current Authoring Jira backlog | Product / Engineering | Delivery evidence | 28 evidence rows; only specific tickets are capability signals |
| SRC-OECD-001 - OECD Digital Education Outlook 2026 | Mack | External research evidence | 10 Authoring-only signals after re-scope |
| SRC-NYSED-001 - 3.x Features and Enhancements | Dan | Customer / VoC | 18 Authoring needs/gaps |
| SRC-STRATEGY-001 - OAT Market Portfolio and Product Strategy 2027-2029 | Miguel | **High-authority strategy** | 36 Authoring-relevant strategic capabilities/features |

## Important re-scope decisions

### OECD

The previous OECD extraction mixed Authoring with scoring, learner-process assessment and other downstream assessment capabilities. The v2 extraction is narrower and is based mainly on the high-stakes assessment material in Chapter 12.

Retained Authoring signals include AI item generation, human review, task-specific generation setup, staged generation, generated-item QA, authentic interactive item designs, comparability constraints, curriculum alignment and responsible human oversight.

### NYSED

NYSED is treated as **customer need/gap evidence**, not as proof that 3.x already supports the capability. Generic platform items such as branding/logout-domain behaviour were excluded by the Authoring scope gate. Authoring-relevant requirements such as repository bulk actions, usage traceability, metadata authoring, preview, search, access control, workflow and item provenance were retained.

### Strategy

Miguel's strategy is treated as **STRATEGY - HIGH AUTHORITY**. Authoring-relevant rows from the integrated feature roadmap and market-specific roadmaps are preserved as strategic evidence. Non-Authoring delivery, reporting, commerce, credential, infrastructure and generic integration capabilities are excluded from the capability extraction.

Strategy influences prioritisation and alignment, but does not automatically create canonical identity before reconciliation.

### Jira

Jira remains delivery evidence. Broad epics/placeholders are not promoted into capabilities merely because a ticket exists. Specific tickets retain their current CAP relationships; one ticket may relate to several capabilities.

## Capability metadata model used in the workbook

Each Source Capability now supports:

- Source Capability ID
- current canonical CAP-ID, where an existing baseline mapping exists
- Source ID and document
- source category
- capability/signal name
- full description
- one of the five Strategic Categories
- five independent Market dimensions
- **MEXCBT / Uchida as a separate Strategic Initiative dimension**
- market/initiative mapping basis
- Owner / Proposer
- Evidence Type
- Origin / Extraction Provenance
- Source Confidence
- Extraction Type
- Evidence / Reference
- Product Review Status
- Authoring Scope
- current reconciliation/treatment
- Feature ID(s) placeholder
- Feature Composition Status
- Notes

Origin/provenance and Product Review are intentionally separate. `AI_ABSTRACTED` can later coexist with `CONFIRMED`.

## Source Screen - required Product Truth behaviour

The Sources screen should become the audit surface for this model.

### Source list

Every source row should show:

- Source ID
- human-readable document name
- Owner / Proposer
- Source Type / Evidence Class
- Authority (especially Strategy)
- Artifact availability
- extracted Source Capability count
- extraction/review status

Primary actions:

- **Open Source** - open the actual governed artifact
- **View Extracted** - show the Source Capabilities extracted from that artifact

If the artifact is missing, show `Source document unavailable`; do not provide a fake Open Source action.

### Source detail

The detail view should show source metadata, lineage, artifact location and extraction status, followed by the extracted capability register.

### View Extracted

The extracted register should support filters for:

- Search
- Strategic Category
- Market
- MEXCBT / Uchida
- Product Review Status
- Authoring Scope
- Current reconciliation/treatment

Each Source Capability ID should open a detail view containing the complete source description and evidence pointer, plus the current canonical CAP mapping where one exists.

### Review controls

Product should be able to change Product Review Status without changing extraction provenance. Suggested controlled values:

- REVIEW_REQUIRED
- CONFIRMED
- CONFIRMED_WITH_CHANGES
- REJECTED

Changes must be audited and version-guarded.

## Markets and MEXCBT / Uchida

Markets and MEXCBT must remain visible throughout Ideation, Cross-analysis, Backlog and Roadmap.

They are not the same concept:

- Markets = five market dimensions.
- MEXCBT / Uchida = Strategic Initiative.

A source only marks MEXCBT as direct when evidence supports it. Otherwise the field remains blank or `TO_REVIEW`; strategy does not mention MEXCBT explicitly.

## Feature model

No Features have been invented in this extraction.

The model remains:

**Canonical Capability = Product Truth**

**Feature = Product-managed composition of 1..N Canonical Capabilities**

Feature composition will occur after cross-source reconciliation, not during source extraction.

## Next controlled operation

1. Product reviews the nine source sheets.
2. Confirm/reject/adjust source extraction and metadata.
3. Run cross-source reconciliation.
4. Produce canonical proposal and diff against current 135 CAP baseline.
5. Run the requested model-consistency analysis: granularity, naming, unsupported CAPs, duplicates, gaps, market coverage, MEXCBT coverage, strategic alignment and Feature composition candidates.
6. Only after Product review update the application canonical baseline.
