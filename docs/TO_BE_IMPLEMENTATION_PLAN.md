# TO_BE_IMPLEMENTATION_PLAN

**Date:** 2026-10-16

## AS-IS → TO-BE mapping

| TO-BE capability | AS-IS status | Action | Phase |
|---|---|---|---|
| Home page | NEW | Create `#/home` with attention/continue/quick/recent | A |
| Simplified navigation (7 areas) | EXTEND | Restructure existing nav | A |
| Comments/discussion | NEW | `comments` table + API + UI component | A |
| Owner on key entities | EXTEND | Add `owner` to candidates/features (customers have it) | A |
| Recent changes from audit | REUSE | Query `audit_events` — no new storage | A |
| Evidence Explorer (search/filter 426) | EXTEND | Enhance Sources → Evidence tab with search/filters | B |
| Evidence detail modal | NEW | Evidence detail with promote action | B |
| Promote to Candidate from UI | EXTEND | Add promote button to Evidence detail | B |
| + New Capability from UI | NEW | Create capability form (PRODUCT_CREATED origin) | B |
| Universal Capability editor (enhanced) | REUSE | Existing modal + enrichment sections (already implemented) | B |
| Ideation lenses (editable) | EXTEND | Lens-specific disposition/treatment editing | B |
| Features workspace | EXTEND | Roadmap Features tab → standalone workspace with creation | C |
| Feature editor (enhanced) | REUSE | Existing Feature editor (already implemented) | C |
| Customer workspace | EXTEND | Migration Customer Plans → standalone Customers page | D |
| Customer↔Feature | NEW | `customer_features` table + API + UI | D |
| Customer×Feature matrix | NEW | Cross-customer view | D |
| Milestone-by-milestone customer plan | EXTEND | Derive per-interval availability from roadmap + customer_features | E |
| Conflict detection | NEW | Compare required_by_milestone vs roadmap availability | E |
| Product narrative blocks | EXTEND | Use roadmap_outcomes / candidate descriptions | F |
| Deliverable readiness mapping | REUSE | Already implemented in reports layer | F |
| View Journey | NEW | Derive from governed relationships (read-only) | G |

## Schema impact

| Migration | Tables | Columns |
|---|---|---|
| `0008_collaboration` | `comments` (new) | comment_id, entity_type, entity_id, parent_id, author, comment, resolved, created_at |
| `0009_customer_features` | `customer_features` (new) | customer_id, feat_id, importance, required_for_migration, required_by_milestone, rationale, validation_status, customer_feedback, notes, version, timestamps |
| `0010_candidate_enrichment_fields` | `capability_candidates` | +functional_definition, +what_it_enables, +user_problem, +functional_scope, +out_of_scope, +owner, +strategic_category |

## API impact

| New/changed | Endpoint | Method |
|---|---|---|
| Comments CRUD | `/api/comments` | GET/POST/PATCH |
| Candidate enrichment fields | `PATCH /api/candidates/{id}` | extend body |
| New Capability from UI | `POST /api/candidates/{id}/promote` (already exists) or dedicated | — |
| Customer↔Feature CRUD | `/api/customer-features` | GET/POST/PATCH/DELETE |
| Milestone-by-milestone derivation | `GET /api/customers/{id}/migration-plan` (enhanced) | — |

## UI impact

| Change | Files |
|---|---|
| Home page | `web/js/views/home.js` (new) |
| Navigation restructure | `web/index.html`, `web/js/main.js` |
| Evidence Explorer | `web/js/views/evidence.js` (new, replaces Sources → Evidence tab) |
| Capabilities workspace | `web/js/views/ideation.js` → `web/js/views/capabilities.js` (rename/extend) |
| Features workspace | `web/js/views/features.js` (new, extracted from roadmap) |
| Customer workspace | `web/js/views/customers.js` (new, extracted from migration) |
| Comments component | `web/js/components/comments.js` (new) |
| View Journey | `web/js/components/journey.js` (new) |

## Phased implementation

| Phase | Scope | Regression risk |
|---|---|---|
| A: PM Shell + Collaboration | Home, nav, comments, owner, rationale enforcement | LOW (additive) |
| B: Evidence + Capability workflow | Evidence explorer, promote, new capability, editor upgrade | MEDIUM (touches existing views) |
| C: Features | Features workspace (extraction from roadmap) | LOW (new view) |
| D: Customers | Customer workspace (extraction from migration) | MEDIUM (touches existing view) |
| E: Migration | Milestone-by-milestone derivation + conflict detection | MEDIUM (derivation logic) |
| F: Deliverables | Narrative blocks + readiness mapping | LOW (additive) |
| G: View Journey + UAT | Journey component + full PM scenario walkthrough | LOW (read-only view) |
