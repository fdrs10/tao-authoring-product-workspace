# SOURCE_ANALYSIS_INGESTION_INVENTORY

**Date:** 2026-10-16 · **Operation:** CONTROLLED OPERATION — INGEST FINAL SOURCE ANALYSIS INTO PRODUCT WORKSPACE

## 1. Exact package used

| Field | Value |
|---|---|
| Package | `TAO_Authoring_Capability_Evidence_Focus_Guide_v1_4_VERIFIED.zip` |
| Location | `~/Desktop/TAO_Authoring_Capability_Evidence_Focus_Guide_v1_4_VERIFIED.zip` |
| Size | 10,948,159 bytes |
| MD5 | `e4d70bb92e7bb14119bf08b8465f111f` |
| Inner analysis HTML | `TAO_AUTHORING_ANALYSIS_v1_4_VERIFIED.html` (957,056 bytes; MD5 `803bd206fafe1a51a35728f4d0fc3ecd`) |
| Package self-declaration | README: "FINAL ANALYSIS v1.3: 426 source signals -> 34 reconciled capability candidates -> 15 cross-market focus capabilities. Read-only. No MoSCoW applied." |
| Selection rule | Latest/final governed package: v1.4 VERIFIED supersedes `TAO_Authoring_Source_Package_Initial.zip` and the bare `TAO_AUTHORING_ANALYSIS_v1_4_VERIFIED.html` (same HTML is bundled inside the ZIP). |

**Extracted (read-only) to:** `~/.kimchi/docs/v1_4_extract/` — the ZIP itself is preserved unchanged on the Desktop and will be copied into the repository under `data/source-analysis/` during ingestion.

## 2. Files found (key contents)

| File | Size | Role |
|---|---|---|
| `data/source_capabilities.json` | 646,189 B | **426** extracted Authoring evidence signals (the evidence universe) |
| `data/reconciliation_register.json` | 721,259 B | per-signal analysis register (426 rows; treatments: 402 UNRECONCILED, 24 DELIVERY_EVIDENCE) |
| `data/capability_candidates.json` | 17,623 B | **34** reconciled Capability Candidates (families F01–F34) |
| `data/focus_sets.json` | 5,960 B | Focus sets per market (7 each) + **Cross-market Focus Set: 15** |
| `data/current_canonical_135.json` | 145,648 B | previous 135-capability baseline (historical reference) |
| `data/SOURCE_SET_METADATA_v1_2.json` | 4,474 B | **9** governed Source definitions (owner, type, evidence class, authority, extraction rule, artifact) |
| `sources/SRC-*__*` | 9 artifacts | original artifacts materialised per Source (md/docx/pdf/csv + READ_ONLY_VIEW.md) |
| `analysis/TAO_Authoring_Source_Capability_Analysis_v2_0.xlsx` + `…_REPORT_v2_0.md` | — | Source-screen & capability-analysis report |
| `analysis/TAO_Authoring_Reconciliation_and_Focus_Analysis_v1_0.xlsx` + `…_Report_v1_0.md` | — | reconciliation & focus analysis |
| `TAO_AUTHORING_ANALYSIS_v1_4_VERIFIED.html` / `index.html` | 957,056 B | final analysis HTML (publication) |

## 3. Funnel verification (against expected)

| Expected | Found in package | Match |
|---|---|---|
| 9 Governed Sources | 9 (`SRC-3X-001, SRC-V1-001, SRC-GAP-001, SRC-NEW-001, SRC-COMP-001, SRC-JIRA-001, SRC-OECD-001, SRC-NYSED-001, SRC-STRATEGY-001`) | ✔ |
| ~426 Evidence Signals / Source Capabilities | **426** exact (`data/source_capabilities.json`) | ✔ |
| 34 Capability Candidates | **34** exact (families F01–F34; `Signals` sum = 426 — full accounting, no signal loss) | ✔ |
| 15 Cross-market Focus Capabilities | **15** (`Cross-market Focus Set`) + per-market focus sets (7 each) | ✔ |
| Historical 135 baseline | `current_canonical_135.json` (135) | ✔ |

## 4. New sources vs current registry

Package introduces **2 new Sources** not in the current registry: `SRC-NYSED-001` (3.x features & enhancements, NYSED — docx) and `SRC-STRATEGY-001` (OAT 18+18 Months Strategy — Product and Markets, docx + read-only view). `SRC-HTML-001` (old registry) is **not part of the governed 9** and becomes out-of-funnel (historical).

## 5. Missing or ambiguous artifacts

| Item | Status |
|---|---|
| Source artifacts | **Present for all 9** (materialised in `sources/`; OECD = original PDF; NYSED/STRATEGY = original docx) — none missing |
| Candidate descriptions | Candidates consolidate evidence families; **no narrative description field** in the package → will render "Awaiting Product data" (not invented) |
| Evidence ↔ Candidate per-row linkage | Not present as explicit per-row family IDs; linkage is the analysis consolidation itself (candidate `Signals` counts sum to 426). No per-row family link will be manufactured |
| MEXCBT / Uchida | Present as a first-class dimension (per-signal flag + candidate `MEXCBT Direct Signals` + dedicated focus set) |
| Conflicts | None blocking: package is internally consistent (426 = Σ candidate signals) |

**Verdict: the package fully supports the expected funnel. Proceeding with governed ingestion.**
