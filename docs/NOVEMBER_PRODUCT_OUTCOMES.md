# NOVEMBER_PRODUCT_OUTCOMES — the five outcomes and how the application represents them

**Date:** 2026-10-16 · **Implements:** FINAL UAT EVOLUTION · **In-app orientation:** `NOVEMBER OUTCOMES` in the main navigation (`#/outcomes`) — a lightweight layer over the working areas, **not** a source of Product Truth.

## The Product workflow

```
SOURCES & EVIDENCE → SOURCE CAPABILITIES → PRODUCT ANALYSIS / IDEATION
→ AUTHORING TARGET SCOPE → PRODUCT BACKLOG → PRODUCT ROADMAP
→ COMMON MIGRATION PATH → CUSTOMER MIGRATION PLANS
```

**One Product Roadmap. One common Migration Path. Multiple Customer Migration Plans.**

| # | November Outcome | Answers | In-app area | Key dependency | Product input still required |
|---|---|---|---|---|---|
| 1 | **Authoring Product Definition — Ideation & Target Scope** | What Authoring function do we want TAO to have? | Ideation index 01–06 (V2 Position, V1 carry-forward, 3.x direct migration, new needs & gaps, discontinued → Cross-analysis) | Source documents + Source Capability reconstruction (next controlled operation) | Target-scope admission; source-by-source reviews |
| 2 | **TAO Studio Creator V2 — Product Backlog** | What do we want the Authoring product to contain? (governed, traceable, not "when") | Product Backlog (filterable; full detail in the universal CAP drawer) | Ideation outcomes; Product Review; Feature composition | Product Review statuses; capability edits |
| 3 | **TAO Studio Creator V2 — Product Roadmap** | Which capabilities are we committing to, and when? | Roadmap (Strategic Category → Capability; Capabilities \| Features views; M1–M6 lines) | Product Backlog (same canonical capabilities) | Roadmap Admission; timing; baseline upkeep |
| 4 | **TAO 3.x → TAO Studio Authoring — Common Migration Path** | The shared transition framework all customers move through | Migration Path tab (value unlocked → M1–M6 intervals → customer transition) | Roadmap delivers capabilities → capabilities enable milestones → milestones enable transitions | Milestone baseline upkeep (editable, not immutable) |
| 5 | **Customer Migration Plans** | How does THIS customer move through the common path? | Migration → Customer Plans tab (list + full plan + readiness) | Common Migration Path; Product Roadmap timing (consumed); governed customer data (D3) | Governed customer dataset; per-customer plan fields; validation |

## What makes the relationships explicit

- **Target Scope ≠ Roadmap commitment**: a capability may belong to the desired definition (Backlog) without Roadmap Admission — the Admission field is the explicit gate.
- **Roadmap → Migration**: Migration intervals derive capability availability from Roadmap timing; milestone lines appear in the Roadmap itself (same records).
- **Common Path → Customer Plans**: each plan proposes an interval (`M3 -> M4`) against the shared milestones and consumes Roadmap truth — no second timing (tested).

## Honest states

- Customer data: empty until the governed dataset arrives (D3) — Customer Plans cannot be invented.
- Source reconstruction: NOT executed; packages will be ingested one Source at a time under `docs/SOURCE_RECONSTRUCTION_CONTRACT.md`.
- The 135-capability baseline remains canonical until reconstruction + Product review replace it.
