# PHASE 1 — Data Reconciliation — Checkpoint Report

**Date:** 2026-10-15 · **Commit:** `e4e337f` — `data: phase 1 import/reconciliation report and authoring scope audit`

## What was inspected
- Full canonical corpus: capabilities.json (135), jira_tickets.json (28), sources.json (7).
- All 15 `data/source_extracts/*.csv` tables and `data/raw/JIRA_current_backlog.csv`; `data/raw` reference artifacts (2 XLSX, GAP txt, 2×OECD PDF).
- Cross-table reconciliation: JSON↔CSVs, lineage (SOURCE_TO_CANONICAL), market matrix, category/MoSCoW parity, ID integrity, retired-ID handling, PCR treatment classification.

## What was implemented
- `docs/reports/DATA_IMPORT_AND_RECONCILIATION_REPORT.md` — records by dataset, CAP/source/source-cap/Jira/market/mapping tables, duplicates, orphans, contradictions, review items.
- `docs/reports/AUTHORING_SCOPE_AUDIT.md` — gate review of all 135 capabilities (130 clean / 5 flagged for Product review / 0 removal candidates).

## Files changed
- `docs/reports/DATA_IMPORT_AND_RECONCILIATION_REPORT.md` (new)
- `docs/reports/AUTHORING_SCOPE_AUDIT.md` (new)
- `docs/checkpoints/PHASE_1_REPORT.md` (new)

## Tests run (scripted consistency checks — no test suite exists yet)
- ID integrity: 0 dup CAP-IDs; 0 format violations; CAP-0135 absent ✓.
- Distribution parity with master handoff (categories, MoSCoW, admission) ✓.
- Lineage completeness: 224/224 source caps mapped; 0 unknown canonical refs ✓.
- MARKET_IMPACT vs JSON markets: 0/133 mismatches ✓.
- CROSS_ANALYSIS vs JSON: 0 category / 0 MoSCoW mismatches ✓.
- Jira: raw CSV == canonical 28/28 keys; 24 linked tickets → 17 valid caps; 4 classified specials with no capIds ✓.

## Results
Register cleared for Phase 2 import: 135 caps = 130 clean + 5 flagged (CAP-0071, 0126, 0128, 0131, 0133) + 0 removals.

## Unresolved issues (Product input eventually required — none blocking Phase 2 implementation work)
- G1: CAP-0134/0136 lack ideationSheet + reviewStatus — assign via Product.
- G2: register SRC-JIRA-001 in sources.json (ties to Defect 2).
- G3: clear/mark "no placement" roadmap timing on 5 Discontinued caps.
- G5: normalize `Develop` vs `DEVELOP / VALIDATE` decision label at import (recommended).
- G6: DB import must keep `roadmap_admission` **nullable** (UNSET ≠ Backlog — schema default needs adjustment in migrations).
- G7: budgets have no source data → seed 0/0; Product owns hours.

## Next phase
PHASE 2 — Database: PostgreSQL schema + migrations (Alembic, mirroring `db/schema.sql` with G6/G5 input applied), seed DEV from governed datasets, validation counts/relationships. Awaiting go-ahead.
