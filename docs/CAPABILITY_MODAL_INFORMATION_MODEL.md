# CAPABILITY_MODAL_INFORMATION_MODEL — information hierarchy for the enriched Candidates

**Applies to:** the universal Capability modal when the opened record is an active Candidate (`CAND-*`, population `SOURCE_ANALYSIS_CANDIDATE`). Non-candidate records render exactly as before.

---

## Section order as rendered (top → bottom)

1. **Standard header** — CAP-ID · Working Name, review badge, Edit/Close.
2. **Canonical fields** (existing render: description, category, markets+legend, MoSCoW, Admission, visibility, owner, provenance, decision, V2 mapping, timing notice, sources & evidence, source-capability lineage, Jira, budgets).
3. **PRODUCT DEFINITION (PRODUCT INTERPRETATION — consolidated from source evidence)**
   - Functional definition · What it enables · User/product problem addressed · Functional scope · Out of scope.
   - Every field cites its consolidating evidence; anything not established renders **"Evidence insufficient to determine"**.
4. **PRODUCT CONTEXT**
   - MEXCBT / Uchida (direct signals) · Strategic alignment · Cross-market leverage · Evidence strength · Focus (YES + focus markets / NO).
5. **EVIDENCE & RATIONALE**
   - Why this candidate exists (survival rationale from the 426 → 34 analysis) · Consolidation rationale · Source evidence (signal IDs + sources) · Key references · Provenance.
6. **DELIVERY EVIDENCE (Jira — work evidence, not Product truth)**
   - Linked tickets (key/summary/status/target release + deep links) or explicit "No Jira relationships recorded".
7. **PRODUCT DECISIONS REQUIRED**
   - Open questions (definition required, category required…) as a warning block.
8. **Uncertainty** — explicit statement of what the evidence could not establish.

## Storage

- `capability_candidates.enrichment jsonb` — structured per `docs/CANDIDATE_PRODUCT_ENRICHMENT_REPORT.md`.
- Served via `GET /api/candidates/{candidate_id}` (row + enrichment + Jira delivery evidence).
- The functional definition is mirrored to `capabilities.description` so Backlog/Roadmap/Reports consume it.

## Boundaries

- Product Review, Ideation disposition, MoSCoW, Roadmap Admission render from canonical fields — enrichment never changes them.
- Governance metadata (audit, version, population) stays secondary; it does not displace the Product explanation.
