# AS_IS_CUSTOMER_FEATURE_MIGRATION_MODEL

**Date:** 2026-10-16 · **Mode:** READ-ONLY

---

## 1. Customer model (as implemented)

### Customer table columns
| Field | Column | Editable in UI? | Where |
|---|---|---|---|
| Customer ID | customer_id | ✅ (create only) | Customer Plans → Register customer |
| Name | name | ✅ | Customer Plans → Register/Edit |
| Current use | current_use | ✅ | Plan pane → Edit plan |
| Current environment | current_environment | ✅ | Plan pane → Edit plan |
| Relevant markets | relevant_markets | ✅ | Plan pane → Edit plan |
| Min functionality today | min_functionality_today | ✅ | Plan pane → Edit plan |
| Min functionality in Studio | min_functionality_studio | ✅ | Plan pane → Edit plan |
| Desired outcome | desired_outcome | ✅ | Plan pane → Edit plan |
| Value opportunity | value_opportunity | ✅ | Plan pane → Edit plan |
| Blockers | blockers | ✅ | Plan pane → Edit plan |
| Customer dependencies | customer_dependencies | ✅ | Plan pane → Edit plan |
| Assumptions | assumptions | ✅ | Plan pane → Edit plan |
| Exceptions | exceptions | ✅ | Plan pane → Edit plan |
| Customer feedback | customer_feedback | ✅ | Plan pane → Edit plan |
| Earliest milestone interval | earliest_milestone_interval | ✅ | Plan pane → Edit plan |
| Proposed migration window | proposed_migration_window | ✅ | Plan pane → Edit plan |
| Validation status | validation_status | ✅ | Plan pane → Edit plan |
| Product notes | notes | ✅ | Plan pane → Edit plan |
| Version | version | read-only (optimistic concurrency) | — |

### Derived (computed, not stored)
| Field | Derivation |
|---|---|
| Readiness status | BLOCKED / VALIDATION REQUIRED / PRODUCT DECISION REQUIRED / READY / EXCEPTION |
| Available by interval start | required caps where `start + duration ≤ interval_start_milestone.position` |
| Blocked capability IDs | required caps where the above is false |
| Blocked count | count of blocked |
| Milestones | shared M1–M6 from milestones table |
| Interval start milestone | first milestone_id in earliest_milestone_interval |

### NOT implemented
| Missing | Notes |
|---|---|
| Customer ↔ Feature relationship | No join table, no UI, no API |
| Milestone-by-milestone customer plan | Only `earliest_milestone_interval`; no per-interval capability/feature assignment |
| Customer-specific migration roadmap | No per-customer timeline view |
| Feature-level customer dependency | No `customer_features` table |
| "Feature X needed by M2 but Roadmap delivers at M4" detection | Derived only at capability level |

---

## 2. Feature model (as implemented)

### Feature table columns
| Field | Column |
|---|---|
| Feature ID | feat_id (FEAT-xxxx) |
| Name | name |
| Description | description |
| Owner / PM | owner |
| Status | status |
| Notes | notes |
| Version | version (optimistic concurrency) |
| Derived timing window | computed from constituent capabilities |

### Feature ↔ Capability
- M:N via `feature_capabilities(feat_id, cap_id)`
- A Feature contains 1..N capabilities
- A Capability may participate in multiple Features
- Unlinking removes only the relationship — Feature and Capability both survive

### Feature UI
| Action | Exists? | Where |
|---|---|---|
| View Feature list | ✅ | Roadmap → Features tab |
| Create Feature | ✅ | Roadmap → Features → + Feature |
| Edit Feature | ✅ | Roadmap → Features → Edit |
| Add Capability to Feature | ✅ | Roadmap → Features → Edit → Add link (input CAP-ID) |
| Remove Capability from Feature | ✅ | Roadmap → Features → Edit → remove link |
| Delete Feature | ✅ | API: `DELETE /api/features/{feat_id}` |
| Assign timing to Feature | ❌ | Derived coverage only — no independent Feature timing |
| Assign Feature to Customer | ❌ | NOT IMPLEMENTED |
| Link Jira Epic to Feature | ❌ | NOT IMPLEMENTED (by design) |
| Assign Markets to Feature | ❌ | NOT IMPLEMENTED |
| Assign MoSCoW to Feature | ❌ | NOT IMPLEMENTED |

### Feature gaps (from a PM perspective)
1. **No Feature creation from the browser** — the API exists but there is no dedicated Feature workspace. The only UI is the Roadmap Features tab which shows existing features and provides Edit (existing only).
2. **No Feature list outside the Roadmap** — a PM cannot browse Features independently.
3. **No Feature↔Customer relationship** — cannot answer "which Customers depend on Feature Y?"
4. **No Feature↔Jira relationship** — Jira Epics are not Features.
5. **No Feature timing** — derived coverage only.

---

## 3. Customer Migration Plan detail

### What the Plan shows today (per customer)
| Section | Content |
|---|---|
| Readiness | Derived status + reason |
| Context | Current use, environment, markets |
| Need | Min functionality today/studio, desired outcome, value opportunity |
| Dependencies | Required capabilities (CAP links + availability + dependency reason + features) |
| Common Migration Path | M1–M6 (shared) |
| Migration | Interval, window, dependencies, blockers, assumptions, exceptions |
| Validation | Validation status, product notes, customer feedback |

### What the Plan does NOT show today
| Missing | Notes |
|---|---|
| Milestone-by-milestone Customer Roadmap | No per-interval capability/feature assignment per customer |
| Feature requirements per customer | No Customer↔Feature model |
| Key vs standard capability distinction | No importance/importance_type field |
| Customer-specific delivery dates | Only the shared milestone dates |
| Customer-to-Customer comparison view | Each customer's plan is standalone |
| Conflict detection | "Customer needs X by M2 but Roadmap delivers X at M4" not surfaced |

### Model answer to "Can the application detect timing conflicts?"
**NOT IMPLEMENTED.** The derived readiness says BLOCKED if a required capability is not available by the interval start. But it does not say WHICH milestone the capability will be available at, nor does it show a customer-specific timeline with gap analysis.
