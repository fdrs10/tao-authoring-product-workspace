# AS-IS_PRODUCT_MANAGER_OPERATING_MODEL

**Date:** 2026-10-16 · **Mode:** READ-ONLY FUNCTIONAL ANALYSIS · **HEAD:** `a48fa10` · **DB:** governed `tao_authoring`

---

## Executive Summary

The application is a functional Product workspace with a clear governed data model. A Product Manager can browse 9 Sources, 426 evidence signals, 34 Candidates and their enrichment, view analysis lenses, edit Roadmap Admission and MoSCoW, and generate reports. However, several important workflows are **backend-only** (accessible via API but with no usable UI), and the Ideation 01–06 sheets are **read-only analysis lenses** rather than Product decision workspaces.

---

## 1. What exists today

### Active Product population
- **34 Capability Candidates** (`CAND-F01`…`CAND-F34`) — the governed active Ideation population, extracted from the final Source-analysis package (426 signals consolidated into 34 families).
- **15 Focus Capabilities** — Product recommendation subset (cross-market leverage), not a filter on truth.
- **135 historical capabilities** (`population=HISTORICAL_BASELINE_V1`) — preserved, separately inspectable, never in active views.

### Governed datasets
- **9 Sources** (incl. 2 new: NYSED, STRATEGY) with materialised artifacts.
- **426 evidence signals** with per-signal family linkage (`reconciled_family_id`).
- **6 milestones** (M1–M6, editable Product baseline).
- **28 Jira records** (delivery evidence; coverage-audited against the 34).
- **1 customer** (e2e test fixture; governed customer dataset still empty, D3).

---

## 2. What a PM can actually do (functional summary)

### CAN DO (usable UI exists)
| Action | Where | How |
|---|---|---|
| Browse the 426 evidence signals | Sources → Extracted Authoring Evidence tab | Table with 426 rows; no search/filter in this tab |
| Browse the 34 Candidates | Ideation 00 | Table with search + 8 filters + "Showing X of Y" |
| Open a Candidate modal | Any CAP-ID link | Universal modal: detail + edit + Jira + budgets + enrichment |
| Edit a Candidate (name, description, category, markets, MoSCoW, Admission, notes, budgets) | Candidate modal → Edit → Save | Persisted via API (optimistic concurrency) |
| Change Roadmap Admission inline | Cross-analysis, Backlog | Dropdown per row; persisted; audit |
| Change Product Review | Candidate modal → Edit → Product Review | Dropdown; persisted; audit |
| Change Ideation disposition | `PATCH /api/candidates/{id}` (API only) | ACTIVE/NOT SELECTED + rationale; audit |
| Promote evidence → Candidate | `POST /api/candidates/{id}/promote` (API only) | Evidence ID + name + rationale; audit |
| Create a Feature | `POST /api/features` (API only) | FEAT-xxxx; link capabilities |
| Link capabilities to a Feature | `POST /api/features/{id}/capabilities/{cap_id}` (API only) | M:N |
| Edit Milestones M1–M6 | Roadmap or Migration → click milestone line → edit | Name, date, position, scope; persisted; audit |
| Generate Reports D1–D5 | Reports / Deliverables → Preview | Publication HTML; print/save PDF |
| Record a generation snapshot | Reports → Generate HTML | versioned snapshot in report_generations |
| View Customer Migration Plan | Migration → Customer Plans → Open Plan | Full plan: context, dependencies, readiness |
| Edit Customer Plan fields | Customer Plan → Edit plan | All migration-plan fields; versioned; audit |
| View Jira coverage audit | `/api/jira-coverage` | 28 records classified A–E |

### CANNOT DO (no usable UI or NOT IMPLEMENTED)
| Action | Status | Workaround |
|---|---|---|
| Search/filter all 426 evidence signals from the UI | ❌ The Sources → Evidence tab shows a flat table, no search/filter | API: `GET /api/evidence?source=…&mexcbt=…&q=…` |
| Promote evidence → Candidate from the UI | ❌ No button in the Sources → Evidence tab; API exists | API: `POST /api/candidates/{id}/promote` |
| Create a Feature from the UI | ❌ No Feature creation workspace | API: `POST /api/features` |
| Edit a Feature from the UI | ❌ No Feature editing workspace | API: `PATCH /api/features/{id}` |
| Link capabilities to a Feature from the UI | ❌ No Feature↔Capability UI | API: `POST /api/features/{id}/capabilities/{cap_id}` |
| See which Customers require a Capability | ❌ No reverse lookup | API: `GET /api/customers` + `customer_capabilities` |
| Assign Key Features to a Customer | ❌ No Customer↔Feature relationship | API: customer_capabilities + features (derived) |
| Build a Customer-specific Migration Roadmap across M1–M6 | ❌ Customer Plan has only `earliest_milestone_interval` (e.g. `M3 → M4`); no milestone-by-milestone customer plan | — |
| Detect "Customer needs Feature X by M2 but Roadmap delivers at M4" | ❌ Derived availability is capability-level only; no Feature-level timing | — |
| View complete end-to-end journey for an entity | ❌ No "View Journey" feature; lineage is inspectable per-layer but not unified | — |

---

## 3. The funnel today

```
9 Sources (Sources & Evidence tab)
→ 426 Evidence Signals (Sources → Evidence tab; API: /api/evidence)
→ 34 Capability Candidates (Ideation 00; API: /api/candidates)
→ 15 Focus Capabilities (Ideation 00 → Focus toggle)
→ Product Review (Candidate modal → Edit → Product Review)
→ Target Scope (Cross-analysis 06)
→ Product Backlog (Backlog page)
→ Features (API only — no UI)
→ Roadmap Admission (Cross-analysis / Backlog / Modal — inline dropdown)
→ Roadmap (Roadmap page)
→ Common Migration Path M1–M6 (Migration Path tab)
→ Customer Migration Plans (Migration → Customer Plans tab)
→ Deliverables D1–D5 (Reports / Deliverables)
```

## 4. Where the workflow breaks

1. **Evidence → Candidate promotion** exists in the API but has **no UI button** on the Sources → Evidence tab. A PM must use the API directly.
2. **Features** have a full API (CRUD, M:N, audit) but **zero UI** — no workspace, no editor, no list. The Roadmap Feature view renders features if they exist but there is no way to create or manage them from the browser.
3. **Customer↔Feature** relationship does not exist in the data model or UI.
4. **Customer-specific Migration Roadmap** (milestone-by-milestone per customer) does not exist. The current model has only `earliest_milestone_interval` (e.g. `M3 → M4`).
5. **Ideation 01–06 sheets** are read-only analysis lenses — they show evidence and candidate consolidation but do not let Product make sheet-specific decisions (except Admission in 06).
6. **The 135 historical baseline** is correctly excluded from active views but there is **no dedicated "Historical Baseline" browser** — Product can only inspect it via `?population=historical` API calls.
7. **D1–D5 reports** are generated correctly from canonical data, but **D5a Pilot Set** requires governed customer records that do not exist yet (D3).
