# UAT_STRUCTURAL_CHANGE_REPORT — Sources, Capabilities, Features, Roadmap & Milestones

**Date:** 2026-10-16 · **Mode:** controlled Product-model evolution (no redesign) · **Baseline:** `dev-candidate-v1.0` (04f5208) preserved; this work lands after it.
**Regression:** **90 passed** (26 API · 44 UI E2E · 10 ESM gate · 10 structural) — full suite green before push.

---

## 1. Exact schema changes (Alembic `0003_uat_structural`, applied to dev + CI DBs)

| Table | Change |
|---|---|
| `capabilities` | + `extraction_origin` (CHECK: SOURCE_DEFINED/AI_EXTRACTED/AI_ABSTRACTED/PRODUCT_CREATED/MANUAL_EXTRACTION) · + `product_review_status` (CHECK: REVIEW_REQUIRED/CONFIRMED/CONFIRMED_WITH_CHANGES/REJECTED) · + `product_rationale` |
| `source_capabilities` | + `authoring_scope_assessment` · + `strategic_category_interpretation` |
| `features` | **new table** (feat_id PK, name, description, owner, status, notes, version, timestamps) |
| `feature_capabilities` | **new M:N join** (feat_id, cap_id, added_at; FKs; PK pair) |
| Deterministic data derivation | `extraction_origin='AI_EXTRACTED'` for the 128 caps whose recorded review status documents AI extraction; other 7 NULL until their Source is reconstructed. `product_review_status` NULL everywhere (Product has not reviewed — never silently CONFIRMED). |

## 2. Exact API changes

| Endpoint | Change |
|---|---|
| `GET /api/sources` | + `extracted_capability_count`, `document_available` |
| `GET /api/sources/{id}/document` | **new** — streams the registered artifact (local:// or governed data/ path; path-escape guarded); 404 `source_document_unavailable` when unrecoverable |
| `PATCH /api/capabilities/{id}` | accepts `product_review_status` (4 controlled values; 422 otherwise) + `product_rationale`; `extraction_origin` is NOT patchable (provenance is historical) |
| `GET /api/capabilities[...]` | + `extraction_origin`, `product_review_status`, `product_rationale`, `sources` (ids), `traceable`, `traceability_status` (OK / TRACEABILITY_REVIEW_REQUIRED per §9) |
| `GET/POST/PATCH/DELETE /api/features[...]` | **new** — Feature CRUD with version+audit; link/unlink capabilities (M:N; 409 duplicate link; unlink removes only the relationship); `derived_timing_window` computed, never stored as truth |
| Milestones | endpoints unchanged; governed M1–M6 dataset imported via `scripts/import/import_milestones.py` (idempotent, verified) |

## 3. UI changes

- **Sources**: `Artifact` availability column; **Open Source** renders the actual artifact (inline text preview + "Open raw artifact"; PDF opens for download) or an explicit **"Source document unavailable"** with no fake action; **View Extracted** unchanged (Source Truth verbatim, navigation Source → Source Capability → Canonical CAP → back).
- **CAP drawer**: Origin/extraction provenance + Product Review (+ rationale) shown; TRACEABILITY_REVIEW_REQUIRED warning when applicable; edit form gains Product Review select + rationale field.
- **Ideation sheets 02–06**: compact filter layer (search, category, market, MoSCoW, visibility, product review, review flag, admission, decision, source) + **Clear filters** + **"Showing X of Y capabilities"**; presentation-only.
- **Product Backlog**: columns now CAP-ID | Capability | Category | Markets (dots+legend) | MoSCoW | Admission (editable) | **Visibility** | **Source(s)** (compact "N sources", hover = identities).
- **Roadmap (D-R1 confirmed)**: hierarchy **Strategic Category → Capability** — no market lanes; each canonical CAP renders **exactly once** when Market = All (tested); Market is metadata + filter + legend only; new **Capabilities | Features** switch — Feature view draws each Feature's constituent capabilities with **derived** coverage outline (no second planning truth); Feature editor (FEAT-id governed).

## 4. Milestones (§22/§23/§24)

- Governed baseline materialised at `data/milestones/milestones_baseline.json` (M1–M6 with names, dates, position months 2/8/11/14/23/26, descriptions, `source_lineage: TAO_Authoring_v35_6_MIGRATION_DIAGRAM`, `PRODUCT_BASELINE_CONFIRMED_UAT`).
- Imported idempotently (run 1: 6 inserted; run 2: 0 inserted / 6 identical-skips). Roadmap and Migration consume the same records; edits propagate both ways (tested). TS1/TS2/TS3 remain non-canonical (API 422s TS codes).

## 5. Source-document coverage

See `docs/SOURCE_DOCUMENT_COVERAGE_REPORT.md` — 3 artifacts connected (OECD PDF, GAP analysis text, Jira CSV), 5 explicitly unavailable (Confluence pastes / supplied texts never materialised; v36.9 reference HTML absent). Nothing invented.

## 6. Tests (§27) — new coverage

`tests/api/test_phase6_api.py` additions; `tests/ui/test_uat_structural.py` (10): sources coverage table (8/8 artifact states), artifact open + unavailable-explicit, View Extracted → Canonical navigation, provenance/review independence + 409, traceability flags (CAP-0134/0136), Feature CRUD + M:N + unlink survival + 409 duplicate + derived window, Roadmap Market=All renders each CAP once + market filter narrows without lanes, Feature view on canonical data, ideation combined filters + clear + X-of-Y + no mutation, backlog Visibility/Sources cells, milestones baseline + idempotency + shared-edit + no-TS. Existing suites updated only where the confirmed D-R1 changed bar counts (Jira display-only 2→1) and milestone fixtures (MT-ids to avoid the governed baseline).

## 7. Screenshots (`docs/evidence/uat-structural/`)

`01-sources-open-artifact` · `02-sources-view-extracted` · `03-cap-modal-origin-review` · `04-ideation-filtered` · `05-backlog-structural` · `06-roadmap-market-all` (each CAP once; M1–M6 lines) · `07-roadmap-k12-filter` · `08-roadmap-feature-view` · `09-migration-baseline-milestones`.

## 8. Product decisions still pending (unchanged + new)

Carried: D-R2 tail window, D-R3 admission commits, D5 identity, ADM no-approval-workflow. **Updated:** D-R1 and D-M1 are now **CONFIRMED by Product** (this contract) — the provisional flags in earlier docs are superseded. New pending: Feature timing semantics (currently derived-only), M1–M6 are baseline-not-immutable (Product may edit during UAT).

## 9. Boundary honoured (§28/§30)

No CAP baseline replacement, no automatic source extraction, no Migration redesign, no Jira API, no invented Features/Sources/milestones-beyond-M1–M6/customers, no silent normalisation. **Stopping here** — the next operation is Product's controlled ingestion of Source packages, one at a time.

## 10. Commits

Structural migration + API/UI + tests + docs land as small logical commits after `dev-candidate-v1.0` (tag untouched); full suite green before push.
