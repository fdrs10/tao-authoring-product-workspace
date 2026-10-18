# SOURCE_RECONSTRUCTION_CONTRACT — governed ingestion for the next stage

**Stage:** source-by-source reconstruction of Authoring Product Truth, performed progressively **by Product**. This document defines what the application is now ready to receive and the exact workflow. The application does **not** perform the reconstruction itself.

---

## 1. Core model chain (keep the concepts separate)

```
Source Document → Source Capability → Cross-source Reconciliation
→ Canonical Capability → Feature Composition → Product Backlog → Roadmap → Migration Path
```

## 2. Source package contract (§25)

Each Source package Product supplies contains:

| Element | Requirement |
|---|---|
| Original Source artifact | the actual document (PDF/CSV/TXT/MD/HTML). Materialised to `data/source-documents/<SRC-ID>/<name>`; `sources.document_uri = local://<SRC-ID>/<name>`; never a fabricated URL |
| Source metadata | human name, type, owner, date/version, status (matches `sources` columns) |
| Source Capability dataset | the extracted capabilities (CSV/JSON) — see §3 below |
| Extraction/review metadata | extraction type, confidence, authoring-scope assessment, strategic-category interpretation, review notes |
| Lineage references | upstream references, evidence pointers inside the Source |

**Import is explicit and controlled** — no automatic ingestion of files dropped into the repository. Each package goes through `scripts/import/` as a deterministic, idempotent operation (pattern: `import_canonical.py` / `import_milestones.py` / `materialize_source_documents.py`), reporting inserted vs skipped rows; conflicts never overwrite in-database Product edits.

## 3. Source Capability dataset rules (§5/§6)

Minimum fields per Source Capability: ID, Source ID, original name, full original description, source category (where available), evidence/reference/location inside the Source, extraction type, confidence (where applicable), **authoring scope assessment**, **strategic category interpretation**, reconciliation status/relationship, eventual Canonical CAP-ID, notes.

- **ID convention:** existing IDs stay verbatim (Source Truth: `3X-001`, `V1-001`, …). **New** extractions use source-scoped IDs `SRC-<SOURCE_ID>-CAP-<NNN>` (e.g. `SRC-OECD-001-CAP-014`) so identity never collides across Sources.
- **Terminology:** when the Source defines capabilities explicitly — preserve the Source's name and description verbatim. Never rename to fit the canonical model.
- **Narrative Sources:** a Source Capability may be abstracted from text, but must record extraction type (`AI_ABSTRACTED` / `MANUAL_EXTRACTION`) and carry evidence.
- **Authoring scope only:** do not extract Portal, Delivery, Administration or other non-Authoring TAO capabilities merely because they appear in the Source. Record them (if at all) with `authoring_scope_assessment = OUT_OF_SCOPE`.
- New schema columns ready: `source_capabilities.authoring_scope_assessment`, `source_capabilities.strategic_category_interpretation` (Alembic 0003).

## 4. Capability traceability rule (§9)

- No canonical Capability may exist without ≥1 traceable Source Capability — **except** Product-created capabilities: `extraction_origin = PRODUCT_CREATED` **and** a recorded `product_rationale`.
- Every CAP must answer "where did this come from?" — e.g. `CAP-0087 → SRC-OECD-001-CAP-014 → OECD Source → evidence`, or `CAP-0087 → PRODUCT_CREATED → rationale`.
- Current caps not yet satisfying the rule are reported `TRACEABILITY_REVIEW_REQUIRED` (API `traceability_status`; visible in the CAP drawer) — currently CAP-0134/CAP-0136. They are **not** deleted.

## 5. Provenance vs Product Review (§10) — implemented, independent

| Field | Meaning | Mutability |
|---|---|---|
| `extraction_origin` | how the information entered the system: `SOURCE_DEFINED / AI_EXTRACTED / AI_ABSTRACTED / PRODUCT_CREATED / MANUAL_EXTRACTION` | historical provenance — set at import/creation; **never overwritten** by later review; not PATCHable |
| `product_review_status` | Product's decision: `REVIEW_REQUIRED / CONFIRMED / CONFIRMED_WITH_CHANGES / REJECTED` (NULL = not yet reviewed) | editable via `PATCH /api/capabilities/{id}` — API persistence, actor, timestamp, audit, optimistic concurrency (409 on stale) |
| `review_status` (legacy) | Phase-1 flags incl. the 5 `PRODUCT_SCOPE_REVIEW_REQUIRED` caps | preserved; scope-review requirements remain enforced |
- A capability may correctly show `Origin: AI_EXTRACTED` + `Product Review: CONFIRMED`.
- 128 of the current 135 caps carry `extraction_origin = AI_EXTRACTED` (deterministic derivation from their recorded AI-PROPOSED review status); the remaining 7 stay NULL until their Source is reconstructed.

## 6. Source-by-source workflow (§26) — explicit, never collapsed

1. Register Source → 2. Preserve original artifact → 3. Extract Authoring Source Capabilities → 4. Review Source extraction → 5. Mark Source extraction complete → *(next Source)* → 6. Cross-source reconciliation → 7. Compare against current canonical baseline → 8. Product review → 9. Publish new canonical baseline.

Reconciliation output classes (§11): unchanged · description change · merge candidate · split candidate · new capability · unsupported capability · Product-created capability · conflict · unresolved. **Only after Product review does the canonical baseline change.** The current 135-CAP baseline remains untouched meanwhile.

## 7. Ready-to-receive checklist (status)

- [x] Schema: provenance + Product-review + scope/interpretation columns; Features; (milestones already modelled)
- [x] API: traceability status; Product-review PATCH (audited/versioned); Features CRUD/M:N; source artifact + availability endpoints
- [x] UI: Open Source (artifact/unavailable), View Extracted → Source Capability → Canonical CAP navigation; CAP drawer shows Origin/Product Review/traceability; source-package-ready fields exposed
- [x] Governed import patterns + coverage reporting (`materialize_source_documents.py`, `SOURCE_DOCUMENT_COVERAGE_REPORT.md`)
- [ ] Per-package importer invocation (written when the first package arrives)


## 8. Ingestion executed (2026-10-16) — CONTROLLED OPERATION

The FINAL governed Source-analysis package (`TAO_Authoring_Capability_Evidence_Focus_Guide_v1_4_VERIFIED`, md5 `e4d70bb9…`) has been ingested: 9 Sources, 426 evidence signals (`source_evidence`), 34 Capability Candidates (population `SOURCE_ANALYSIS_CANDIDATE` — the active Ideation population), 15 Cross-market Focus Capabilities; the previous 135 caps marked `HISTORICAL_BASELINE_V1`. See docs/SOURCE_ANALYSIS_INGESTION_REPORT.md + docs/SOURCE_ANALYSIS_FUNNEL_MODEL.md + docs/CAPABILITY_CANDIDATE_GOVERNANCE.md. The Source-by-Source RECONSTRUCTION itself (per-Source review passes 1–5) remains the next Product operation.
