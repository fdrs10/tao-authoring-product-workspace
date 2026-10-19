# AS_IS_APPLICATION_SCREEN_AND_ACTION_INVENTORY

**Date:** 2026-10-16 · **Mode:** READ-ONLY · **Source:** physical browser walkthrough + API inventory

---

## Navigation structure

| Nav label | Route | Screen |
|---|---|---|
| IDEATION | `#/ideation/00` | Capability Candidates (Product Review workspace) — default landing |
| IDEATION | `#/ideation/01` | V2 Position / Product Definition |
| IDEATION | `#/ideation/02` | V1 Carry-forward Analysis |
| IDEATION | `#/ideation/03` | 3.x Direct Migration Analysis |
| IDEATION | `#/ideation/04` | New Needs & Gaps Analysis |
| IDEATION | `#/ideation/05` | Discontinued Analysis |
| IDEATION | `#/ideation/06` | Cross-analysis / Target Scope |
| (from 06) | `#/backlog` | Product Backlog |
| ROADMAP | `#/roadmap` | Product Roadmap (Capabilities | Features switch) |
| NOVEMBER OUTCOMES | `#/outcomes` | November Outcomes overview |
| REPORTS / DELIVERABLES | `#/reports` | Reports / Deliverables |
| MIGRATION PATH | `#/migration` | Migration Path (Migration Path | Customer Plans subtabs) |
| SOURCES & EVIDENCE | `#/sources` | Sources & Evidence (Sources | Capabilities | Customers subtabs) |

---

## Screen-by-screen inventory

### 00 · Capability Candidates (Ideation 00)
- **Question:** What are we considering?
- **Data:** 34 active Candidates (name, markets, signals, sources, evidence strength, MEXCBT, focus, disposition, enrichment)
- **Editable:** Search, 8 filter dropdowns (market, MEXCBT, focus, review, disposition, source, category, MoSCoW), "Include not-selected" toggle
- **Actions:** Open CAP modal (click CAP-ID), All | Focus toggle, MEXCBT filter, Clear filters, Include not-selected
- **Modal used:** Universal CAP modal
- **After edit:** Audit + version bump; re-render
- **Missing:** No promote-from-evidence button in this view; no Product Review editor on this page (must use modal)

### 01 · V2 Position / Product Definition
- **Question:** What is the target Product definition?
- **Data:** Static V2 Position figure + formula + links to sheets 02–06
- **Editable:** Nothing
- **Actions:** Links to sheets 02–06 and Cross-analysis
- **Missing:** NOT IMPLEMENTED AS A WORKSPACE — this is a static reference page

### 02 · V1 Carry-forward Analysis
- **Question:** How does V1 evidence contribute to the current Candidates?
- **Data:** 91 SRC-V1-001 evidence signals grouped by reconciled family (candidate), with historical CAP references and treatment
- **Editable:** Nothing (read-only analysis lens)
- **Actions:** None (tables only)
- **Missing:** No editable Product decision; no direct "promote" or "confirm" action on this page

### 03 · 3.x Direct Migration Analysis
- **Question:** How does 3.x functionality contribute?
- **Data:** 83 SRC-3X-001 evidence signals grouped by family
- **Editable:** Nothing
- **Missing:** Same as 02

### 04 · New Needs & Gaps Analysis
- **Question:** What new-needs evidence exists?
- **Data:** 21 SRC-NEW-001 + 15 SRC-NYSED-001 + 14 SRC-COMP-001 + 10 SRC-OECD-001 evidence signals
- **Editable:** Nothing
- **Missing:** Same as 02

### 05 · Discontinued Analysis
- **Question:** What was historically discontinued?
- **Data:** Historical caps with `ideation_sheet='Discontinued'` (5 records) — shown as decision evidence
- **Editable:** Nothing
- **Missing:** No Product validation action on this page

### 06 · Cross-analysis / Target Scope
- **Question:** What does each Candidate become in TAO Studio V2?
- **Data:** 34 active candidates (table) with inline Roadmap Admission editing
- **Editable:** Roadmap Admission dropdown per row; 8+ filters
- **Actions:** Open CAP modal; change Admission inline (persisted + audited)
- **Missing:** No sheet-specific Product decision (e.g. "confirm this Candidate for V2")

### Product Backlog
- **Question:** What do we want the product to contain?
- **Data:** Active population (34 CAND-Fxx + 4 seed = 38 on governed DB) with filters
- **Editable:** Filters (MoSCoW, category, market, visibility, source, admission); Roadmap Admission inline dropdown
- **Actions:** Open CAP modal; change Admission
- **Missing:** No inline Product Review editing; no inline MoSCoW editing; no Feature assignment

### Roadmap
- **Question:** Which capabilities are we committing to, and when?
- **Data:** Active population with Roadmap timing (currently 0 timed — all awaiting Admission); Milestone lines M1–M6; Feature composition view
- **Editable:** Drag/resize bars (month snap, persisted); Milestone lines (drag); Milestone editor (name, date, position, scope); Quarter report modal; Outcome narratives (3 textareas, versioned)
- **Actions:** Edit timing; edit milestones; edit Outcome; + Milestone; quarter drill-down to CAP modal; filters
- **Missing:** No capability creation; no Feature creation; no drag-into-Roadmap from Backlog

### November Outcomes
- **Question:** What are the five November deliverables?
- **Data:** Static orientation text (5 outcome cards with links)
- **Editable:** Nothing
- **Missing:** Pure navigation layer — by design

### Reports / Deliverables
- **Question:** What are the November deliverables and can I generate them?
- **Data:** 5 report contracts (D1–D5) with section completeness + last generation
- **Editable:** D5 customer select
- **Actions:** Preview Report (opens publication HTML in new tab); Generate HTML (records snapshot); Generate Customer Migration Pilot Set (D5)
- **Missing:** No inline editing of report content; no DOCX output; no custom report builder

### Migration Path (tab: Migration Path)
- **Question:** How do customers move from 3.x to Studio?
- **Data:** VALUE / CAPABILITIES UNLOCKED band (derived from Roadmap timing); M1–M6 milestone band; Customer transition summary table
- **Editable:** + Milestone; Edit milestone (via milestone editor); capability availability is derived (read-only)
- **Missing:** No Feature-level migration view; no customer-specific milestone-by-milestone plan

### Migration Path (tab: Customer Plans)
- **Question:** How does each specific customer move?
- **Data:** Customer Migration Plans per customer (readiness, interval, required capabilities, blockers)
- **Editable:** Register customer; Edit plan (all migration-plan fields via API); Edit milestone
- **Missing:** No Customer↔Feature relationship; no customer-specific milestone-by-milestone plan; no multi-customer comparison view

### Sources & Evidence (tab: Source Registry)
- **Question:** What are our Sources?
- **Data:** 10 sources (9 governed + 1 historical) with artifact availability + extracted counts
- **Editable:** + Milestone (via roadmap); no source editing
- **Actions:** Open Source (artifact or unavailable notice); View Extracted (per-source evidence table)
- **Missing:** No Source creation; no Source metadata editing; no inline search across sources

### Sources & Evidence (tab: Capabilities)
- **Question:** What capabilities did the Sources produce?
- **Data:** Canonical capabilities with source/evidence traceability
- **Editable:** Nothing
- **Missing:** Same as Backlog but without the inline editing

### Sources & Evidence (tab: Customers)
- **Question:** Which customers are registered?
- **Data:** Customer list with readiness, interval, blockers
- **Editable:** Nothing
- **Missing:** No customer editing from this tab

### Universal CAP Modal
- **Question:** What is this capability?
- **Data:** Full capability record + enrichment + source capabilities + sources + Jira + budgets + timing + Product Review
- **Editable:** Edit button → full edit form (name, description, category, MoSCoW, Admission, visibility, owner, decision, budgets, markets checkboxes, Jira add/remove, Product Review, rationale)
- **Actions:** Save (optimistic concurrency); Jira add/remove; Close
- **After save:** Audit + version bump; modal re-renders detail
- **409 behaviour:** Conflict notice with "Show latest version" button
- **Missing:** No inline Ideation disposition editing; no Feature assignment from the modal

### Customer Plan Modal
- **Question:** What is this customer's Migration Plan?
- **Data:** Full plan (readiness + reason, context, need, dependencies, milestones, migration, validation)
- **Editable:** Edit plan → all plan fields (interval, window, environment, markets, functionality, outcome, value, dependencies, blockers, assumptions, exceptions, validation, feedback, notes); Add/remove required capabilities (via customer_capabilities API)
- **Actions:** Save (optimistic concurrency); Close
- **Missing:** No milestone-by-milestone customer plan; no Feature requirement assignment
