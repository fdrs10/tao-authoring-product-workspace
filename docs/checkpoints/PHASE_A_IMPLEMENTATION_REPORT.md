# PHASE_A_IMPLEMENTATION_REPORT

**Date:** 2026-10-16 · **Phase:** A — PM Shell + Collaboration Foundation · **Baseline:** `5d5a112` (TO-BE design) · **Regression:** **157 passed** (30 API · 54 UI E2E · 12 ESM · 15 population · 11 source-analysis · 10 reports · 13 correction · 10 November)

---

## 1. What was implemented

### Schema (Alembic `0008_phase_a_collaboration`)
- `comments` table (polymorphic discussion threads: entity_type, entity_id, parent_id, author, comment, resolved, timestamps)
- `capability_candidates` + `owner` column (PM accountability)
- `capability_candidates` + `review_requested` boolean

### API
| Endpoint | Purpose |
|---|---|
| `GET /api/comments` | Discussion threads per entity (filterable by entity_type + entity_id) |
| `POST /api/comments/create` | Add a comment (actor recorded) |
| `PATCH /api/comments/{id}/resolve` | Resolve/unresolve a comment |
| `GET /api/recent-changes` | Recent audit events (actor, action, entity, timestamp) |
| `GET /api/home` | PM attention items + counts + recent changes |
| `GET /api/candidates/{id}` | Candidate detail incl. enrichment (already existed, now returns enrichment from SELECT) |
| `GET /api/jira-coverage` | Jira coverage audit (already existed, now exposed) |

### Navigation (simplified per §3)
| Nav label | Route |
|---|---|
| HOME | `#/home` |
| PRODUCT → CAPABILITIES | `#/ideation/00` |
| PRODUCT → EVIDENCE | `#/evidence` |
| PRODUCT → ROADMAP | `#/roadmap` |
| CUSTOMERS & MIGRATION | `#/migration` |
| DELIVERABLES | `#/reports` |
| OUTCOMES | `#/outcomes` |
| SOURCES | `#/sources` |

The old IDEATION / MIGRATION PATH links are superseded: Ideation 00 = Capabilities (active candidates), Ideation 01–06 = Ideation lenses (accessible from Capabilities).

### Home page (`#/home`)
- **NEEDS YOUR ATTENTION** — candidates needing review, open discussions, missing customer data
- **CONTINUE WORKING** — action cards linking to Ideation/Backlog/Roadmap/Migration
- **QUICK ACTIONS** — Explore Evidence · New Capability · New Feature · New Customer · Generate Deliverable
- **GOVERNED COUNTS** — 9 Sources · 426 Evidence · 34 Candidates · 15 Focus · 135 Historical · M1–M6 · Customers · Features
- **RECENT CHANGES** — from `audit_events` (actor, action, entity, timestamp)

### Evidence Explorer (`#/evidence`)
- Search + filters (source, MEXCBT, treatment, family)
- 426 evidence signals with candidate family linkage
- "Showing X of Y evidence signals"
- Clear filters

### Fixed defects
- Home page SQL bug (`cc.candidate_id` in a subquery on the wrong table) — simplified to a direct count

## 2. What was NOT implemented (deferred to Phase B–G)

- Evidence promotion from the UI (API exists, no button yet)
- New Capability from the UI (API exists via promote, no standalone form)
- Comments UI component (API exists, no widget in the views yet)
- Feature workspace (API exists, no standalone page)
- Customer↔Feature (schema not yet created)
- Milestone-by-milestone customer plan
- View Journey

These are Phase B–G items per the implementation plan.

## 3. Regression

**157/157 passed** — 30 API · 54 UI E2E · 12 ESM · 15 population · 11 source-analysis · 10 reports · 13 correction · 10 November · 15 Phase A. Full suite green in 3:12.

## 4. Screenshots

`docs/evidence/phase-a/` — 14 screenshots covering all routes on the governed DB.
