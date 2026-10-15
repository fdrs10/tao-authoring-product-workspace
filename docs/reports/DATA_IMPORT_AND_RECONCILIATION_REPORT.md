# DATA IMPORT AND RECONCILIATION REPORT

**Date:** 2026-10-15 · **Phase:** 1 · **Basis:** repository baseline `functional-baseline-v38.6` (commit `1b0a31e`)
**Method:** all counts/checks produced by scripted analysis over `data/canonical/*.json` and `data/source_extracts/*.csv`. No data was repaired; anomalies are flagged for review, never silently fixed (execution prompt §3 trust order, §5).

## 1. Records imported by dataset

| Dataset (file) | Role | Data rows | Verified |
|---|---|---:|---|
| `data/canonical/capabilities.json` | Canonical capability register (AUTHORITATIVE) | 135 | ✓ |
| `data/canonical/jira_tickets.json` | Governed Jira subset (AUTHORITATIVE for Jira) | 28 | ✓ |
| `data/canonical/sources.json` | Source register | 7 | ✓ |
| `data/source_extracts/CANONICAL_CAPABILITIES.csv` | Canonical register (CSV mirror) | 133 | ✓ (Δ2 vs JSON, see §6 C1) |
| `data/source_extracts/CROSS_ANALYSIS.csv` | Cross-analysis decisions | 133 | ✓ |
| `data/source_extracts/PASS1_IDENTITY.csv` / `PASS2_TREATMENT.csv` | Identity/treatment passes | 133 / 133 | ✓ |
| `data/source_extracts/PASS3_PRIORITY.csv` | MoSCoW proposal pass | 133 | ✓ |
| `data/source_extracts/MARKET_IMPACT.csv` | Market applicability matrix | 133 | ✓ |
| `data/source_extracts/IDEATION_DISTRIBUTION.csv` | Ideation summary stats | 37 | ✓ |
| `data/source_extracts/SOURCE_TO_CANONICAL.csv` | Source-cap → canonical lineage | 224 | ✓ |
| `data/source_extracts/ALL_CAPABILITIES.csv` | Union source-capability extract | 224 | ✓ |
| `data/source_extracts/3X_CAPS.csv` / `V1_CAPS.csv` | Per-source extracts | 83 / 91 | ✓ |
| `data/source_extracts/NEW_DEVELOPMENT.csv` / `OECD_2026.csv` / `COMPETITORS.csv` | Per-source extracts | 21 / 15 / 14 | ✓ |
| `data/source_extracts/GAP_3X_V1.csv` | 3.x↔V1 gap analysis (adds comparative columns) | 129 | ✓ |
| `data/raw/JIRA_current_backlog.csv` | Jira raw export (== canonical json rows) | 28 | ✓ |
| `data/raw/*` (2 XLSX, GAP txt, OECD PDF ×2) | Audit/reference artifacts | — | ✓ (not rewritten) |

Set identities verified: 83+91+21+15+14 = 224 (per-source == ALL == S2C), with 0 duplicates.

## 2. Canonical CAP IDs
- **135** unique, all matching `CAP-\d{4}`, 0 duplicates, 0 format violations.
- Numbering covers CAP-0001–CAP-0136 with a single gap at **CAP-0135 (retired — never reuse)** ✓.
- Distributions (JSON) match `KINCHI_MASTER_HANDOFF.md` exactly:
  - Strategic Category: Standards & Portability 50, Create & Design 23, Manage & Govern 25, AI-assisted Authoring 19, Collaborate & Assure Quality 18.
  - MoSCoW: Must 33, Should 75, Could 22, Won't 5.
  - Ideation sheet: V1 Carry-forward 90, 3.x Direct Migration 24, New Needs & Gaps 14, Discontinued 5, **unassigned 2**.
  - Decision: Keep as-is 58, Evolve/enhance 32, Migrate/recreate 22, DISCONTINUE/VALIDATE 5, DEVELOP/VALIDATE 14, Develop 2, Replace with new approach 2.
  - Admission: **133 UNSET (null)**, 2 Candidate.
  - All 135 carry roadmap timing (start 0–6, dur 1–6); all have ≥1 market, ≥1 sourceId, non-empty description and V2 mapping.

## 3. Source IDs
Registered (7): SRC-3X-001 (TAO Authoring – feature list), SRC-V1-001 (TAO Studio – feature list), SRC-NEW-001 (TAO Authoring Strategic Initiative), SRC-COMP-001 (TAO AI Competitor Intelligence Report), SRC-OECD-001 (OECD Digital Education Outlook 2026), SRC-HTML-001 (Existing TAO Authoring HTML capability seed), SRC-GAP-001 (TAO Authoring–TAO Studio gap analysis).
- cap.sourceIds usage: SRC-V1-001 → 90 caps, SRC-3X-001 → 75, SRC-NEW-001 → 19, SRC-OECD-001 → 13, SRC-COMP-001 → 12, **SRC-JIRA-001 → 2 (NOT REGISTERED)**.
- SRC-GAP-001 and SRC-HTML-001 appear in lineage tables (SOURCE_TO_CANONICAL) but in no cap.sourceIds — expected (gap/evidence layers), documented here, no repair.

## 4. Source capability IDs
224 unique across SRC-3X (83), SRC-V1 (91), SRC-NEW (21), SRC-OECD (15), SRC-COMP (14); each mapped in SOURCE_TO_CANONICAL; **0 unmapped, 0 mapping to unknown CAP-IDs**.

## 5. Jira tickets
- 28 tickets (27 Epic, 1 Task). Raw CSV == canonical json (28 keys, identical sets).
- 24 tickets carry `capIds` → covering **17 distinct CAPs**; all references valid.
- 4 tickets intentionally carry **no capIds**, governed by treatment decisions: PCR-117 EVIDENCE_ONLY · PCR-139 NEEDS_DECOMPOSITION · PCR-201 NON_CAPABILITY · PCR-215 NEEDS_DECOMPOSITION ✓ (matches KINCHI_MASTER_HANDOFF §6).
- Jira deep links (`url`, e.g. `https://oat-sa.atlassian.net/browse/PCR-117`) preserved.

## 6. Markets
Six preserved (identity/order/color-bearing): Traditional / K-12, Professional / Credentialing, Higher Education, Governed Formative, Assessment-led Learning, MEXCBT / Uchida (never "Mexico").
- Coverage across 135 caps: K-12 131 · Professional 133 · HigherEd 125 · Governed Formative 101 · Assessment-led 101 · MEXCBT/Uchida 105.
- MARKET_IMPACT CSV ●-markers ↔ JSON `markets[]`: **0 mismatches** over 133 rows.

## 7. Mappings
- capability↔source: 224 lineage rows; every canonical CSV cap has ≥1 lineage row; cap.sourceIds consistent with registered set except SRC-JIRA-001 (§3).
- capability↔market: consistent JSON↔CSV (0 mismatch §6); capability↔jira: 24 ticket links, 17 caps.
- Cross-analysis consistency: JSON `category` vs CROSS_ANALYSIS — 0 mismatches; MoSCoW vs PASS3/CROSS_ANALYSIS — 0 mismatches.

## 8. Duplicates
None: canonical CAP-IDs unique; source capability IDs unique; Jira keys unique; markets unique. Artifact-level note: OECD PDF stored twice (`OECD_Digital_Education_Outlook_2026.pdf` and `SRC-OECD-001_OECD_Digital_Education_Outlook_2026.pdf`, byte-identical) — keep both in repo; document storage layer will dedupe by URI (§10 G4).

## 9. Orphan records
- **CAP-0134, CAP-0136**: exist only in capabilities.json — absent from all 14 CSV tables, no source-capability lineage rows, ideationSheet null, reviewStatus null, sourceIds=[SRC-JIRA-001]. Not repaired; flagged for Product review (G1).
- Roadmap timing on the 5 Discontinued caps (start=6, dur=6): placeholder-looking values on out-of-scope items (G3).

## 10. Contradictions / records requiring review (flagged, NOT repaired)
| # | Item | Detail | Required resolution |
|---|---|---|---|
| G1 | JSON 135 vs CSV canonical 133 | CAP-0134 (TTS pronunciation specification authoring), CAP-0136 (Scoring rule debugging and traceability) are JSON-only; both origin=new, Decision="Develop", admission=Candidate | Product to assign ideation sheet + reviewStatus; decide canonical CSV regeneration |
| G2 | SRC-JIRA-001 unregistered | Referenced by G1 caps; absent from sources.json | Register Jira Current Backlog as a source record (ties to Defect 2) |
| G3 | Discontinued ∩ roadmap timing | CAP-0040/41/65/66/73 carry (6,6) despite Discontinued | Product confirm: clear timing or mark "no placement" |
| G4 | OECD PDF duplicated | Two filenames, identical bytes | Storage-layer dedupe; both stay in repo |
| G5 | Decision label drift | "Develop" (2, JSON-only caps) vs "DEVELOP / VALIDATE" (14, New Needs) | Normalize label at import? — recommendation-only, don't patch data |
| G6 | Admission unset vs schema default | JSON null (UNSET) collides with schema.sql `NOT NULL DEFAULT 'Backlog'` | DB import must keep admission NULLABLE; UNSET ≠ Backlog |
| G7 | Budgets have **no source data** | No analysis/execution hours anywhere in handoff | Budgets seed 0/0; `total_hours` derived = A+E; ownership is Product |

## 11. Import verdict
Governed datasets are internally coherent and lineage-complete for the 133-cap corpus. The 135th/136th caps and the Jira source registration are the only structural gaps, all known and consistent with the documented defect list. **Clears the bar to proceed to Phase 2 (schema + migrations)**, with G1–G3/G6 as import-contract inputs and G7 as Product todo.
