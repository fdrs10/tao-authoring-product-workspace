# TO_BE_PRODUCT_MANAGER_OPERATING_MODEL

**Date:** 2026-10-16 · **Based on:** AS-IS analysis (`AS_IS_*` docs) + FINAL UAT EVOLUTION contract

---

## Design principle

A PM should NOT need to understand the internal architecture. The application makes it obvious:

**WHAT DO I WANT TO DO? → WHERE DO I GO? → WHAT DO I DECIDE? → WHAT HAPPENS NEXT?**

## Simple conceptual model

```
EVIDENCE → CAPABILITY → FEATURE → BACKLOG / ROADMAP
CUSTOMER → NEEDS → KEY FEATURES / REQUIRED CAPABILITIES
                          ↓
PRODUCT ROADMAP + COMMON M1–M6 + CUSTOMER NEEDS
                          ↓
              CUSTOMER MIGRATION PLAN
                          ↓
            D1 / D2 / D3 / D4 / D5 / D5a
```

## Navigation (simplified from 14+ routes to 7 primary areas)

| Nav | Route | Purpose |
|---|---|---|
| **HOME** | `#/home` | What needs attention + Continue working + Quick actions + Recent changes |
| **PRODUCT** → Evidence | `#/evidence` | Explore all 426 signals; promote to Candidate |
| **PRODUCT** → Capabilities | `#/capabilities` | The 34 active Candidates — Product Review workspace |
| **PRODUCT** → Features | `#/features` | Feature compositions (create/edit/link capabilities) |
| **PRODUCT** → Roadmap | `#/roadmap` | Timing + milestones + horizons + outcome |
| **CUSTOMERS** → Customers | `#/customers` | Customer list + plans + readiness |
| **CUSTOMERS** → Migration | `#/migration` | Common Migration Path (M1–M6) |
| **OUTPUT** → Deliverables | `#/reports` | D1–D5/D5a report contracts + generation |

The Ideation lenses (V1 / 3.x / New Needs / Discontinued / Cross-analysis) become **tabs within Capabilities** — they are views over the same Candidate population, not separate universes.

## One object — one editor (§5)

Every object type has exactly one editor, reachable from any screen:

| Object | Editor | Reached from |
|---|---|---|
| Evidence | Evidence detail modal | Evidence Explorer, Analysis lenses |
| Capability | Universal CAP modal (existing, enhanced) | Ideation, Backlog, Roadmap, Features, Evidence, Reports, Home |
| Feature | Feature editor modal (existing, enhanced) | Roadmap Features tab, Capabilities |
| Customer | Customer editor modal (existing, enhanced) | Migration Customer Plans, Home |
| Customer Plan | Plan editor (existing) | Migration Customer Plans |

## Collaboration model (§6–§10)

Three distinct concepts, never conflated:

| Concept | Storage | Purpose |
|---|---|---|
| **Decision Rationale** | Entity field (`rationale`, `product_rationale`) | Why Product made a decision — part of Truth |
| **Discussion** | New `comments` table | Human conversation (author, timestamp, comment, resolved) |
| **Audit History** | `audit_events` (existing) | Immutable system record of what changed |

### Comments table (new)
```
comments(id, entity_type, entity_id, parent_id, author, comment, resolved, created_at)
```

Applied to: Capability, Feature, Customer, Customer Migration Plan.

## Home page (§4)

Three sections:

1. **NEEDS YOUR ATTENTION** — derived from real data: candidates with NULL Product Review, open comments, weak evidence, blocked migration, incomplete deliverables
2. **CONTINUE WORKING** — action cards linking to the working areas
3. **QUICK ACTIONS** — Explore Evidence · New Capability · New Feature · New Customer · Generate Deliverable
4. **RECENT CHANGES** — from audit_events

## Evidence Explorer (§11–§12)

Replaces the flat table in Sources → Evidence tab. A dedicated workspace:

- Header: governed funnel counts (9 / 426 / 34 / 15)
- Search + filters (Source, Market, MEXCBT, scope, treatment, candidate relationship)
- Each row: evidence ID, signal name, source, treatment, candidate family (clickable → Candidate)
- Click row → **Evidence detail** (with Promote button for non-selected evidence)
- **Promote to Product Consideration** — requires rationale; creates a new Candidate; preserves lineage

## Capabilities workspace (§15)

Replaces Ideation 00. The central Product Definition workspace.

- Header: Active / Focus / Review Required / Confirmed / Open discussions
- Views: All | Focus | Needs Review | Confirmed | Not Selected
- Table: Capability | Product Status | Markets | Focus | Features | Customers | Attention
- Click → Universal CAP modal (with enrichment + collaboration)

## Ideation lenses (§17–§19)

Remain as **tabs within Capabilities** — views over the same population:

| Tab | Purpose | Product decision available |
|---|---|---|
| V2 Position | Target scope definition | Admission decision per candidate |
| V1 Carry-forward | How V1 evidence feeds candidates | Treat as evidence lens (read-only) |
| 3.x Migration | How 3.x evidence feeds candidates | Treat as evidence lens (read-only) |
| New Needs & Gaps | New-needs evidence against candidates | Promote unrepresented evidence |
| Discontinued | Historical decision input | Validate discontinuation |
| Cross-analysis / Target Scope | What each Candidate becomes in V2 | Admission + treatment + rationale |

Every lens shows the SAME Candidate objects — just from a different analytical angle. A Product decision on one lens is visible everywhere.

## Features workspace (§21–§22)

- + New Feature (FEAT-ID, name, description, owner, status)
- Table: Feature | Description | Status | Owner | Capabilities | Markets | Customers | Attention
- Click → Feature editor (Definition, Capabilities, Product Context, Customers, Planning, Delivery, Discussion)
- Feature↔Capability: M:N, add/remove from editor
- Feature timing: derived from constituent capabilities (no independent timing)

## Customer workspace (§23–§24)

- + New Customer (governed ID, name)
- Table: Customer | Environment | Market | Key Features | Required Caps | Migration status | Readiness | Attention
- Click → Customer plan (context, needs, required product, dependencies, validation, migration, discussion)

## Customer↔Feature (§25)

New M:N relationship: `customer_features(customer_id, feat_id, importance, required_for_migration, rationale, validation_status, version)`

Importance: KEY / REQUIRED / RELEVANT. Product hypothesis ≠ Customer-validated (§26).

## Customer×Feature matrix (§28)

Cross-customer view: Feature rows × Customer columns. Cells show importance + validation. Clicking opens the relationship.

## Migration evolution (§31–§32)

Customer plans evolve from `earliest_milestone_interval` to milestone-by-milestone:
- For each interval (M1→M2, M2→M3, …): required capabilities, features, availability, blockers
- Conflict detection: "Customer needs Feature X by M2 but Roadmap delivers at M4" → ROADMAP BLOCKER

## View Journey (§34)

For any object, a Journey view shows:
- Lineage: where it came from → what it belongs to → who needs it → where it is on the Roadmap
- Decisions: who proposed, why, discussion, review, changes
- Derived from governed relationships — no duplicated data

## Deliverable readiness (§39)

For every report: X/Y sections ready + missing Product data + open decisions. Clicking a missing item navigates to the relevant workspace.
