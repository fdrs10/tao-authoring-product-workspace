# TO_BE_CUSTOMER_FEATURE_MIGRATION_MODEL

**Date:** 2026-10-16

## Customer↔Feature (new)

The Customer Migration Plan evolves from `earliest_milestone_interval` only to a **milestone-by-milestone Customer Plan** over the shared M1–M6.

### New relationship: `customer_features`

| Column | Purpose |
|---|---|
| customer_id | FK → customers |
| feat_id | FK → features |
| importance | KEY / REQUIRED / RELEVANT |
| required_for_migration | boolean |
| required_by_milestone | e.g. 'M2' — the milestone by which this Feature is needed |
| rationale | why Product assigned this Feature to this Customer |
| validation_status | PRODUCT_HYPOTHESIS / CUSTOMER_VALIDATED |
| customer_feedback | evidence from the Customer |
| notes | free text |
| version | optimistic concurrency |
| created_at / updated_at | timestamps |

### New: Milestone-by-milestone Customer Plan

The Customer Migration Plan evolves from a single `earliest_milestone_interval` to:

```
For each interval (M1→M2, M2→M3, …, M5→M6):
  Required Capabilities (from customer_capabilities, with timing check)
  Required Features (from customer_features, with required_by_milestone)
  Product availability (derived from roadmap_timing)
  Customer actions (from customer_dependencies)
  Product actions (from roadmap commitments)
  Blockers (capability gaps + customer-specific blockers)
  Assumptions
  Validation status
```

### Conflict detection (§32)

For each required Feature:
- `required_by_milestone = M2`
- Product Roadmap delivers the Feature's constituent capabilities at month X
- If X > M2.position_month → **ROADMAP BLOCKER**: "Feature FEAT-xxxx is needed by M2 but constituent capabilities are not available until month X"

Distinguish:
- **ROADMAP BLOCKER** — Product timing is the constraint
- **CUSTOMER-SPECIFIC BLOCKER** — customer-side condition (integration, workflow, etc.)

### Migration intervals

The Customer Plan uses the SAME M1–M6 milestones. No Customer-specific milestones are created. Each interval shows:
- Capabilities required and available
- Features required and available
- Blockers (roadmap + customer-specific)
- Customer actions
- Product actions
- Validation status

### No duplicated truth

- Product Roadmap timing is the ONLY timing truth
- Customer Plans consume it via derivation
- Feature coverage is derived from constituent capabilities
- No Customer-specific milestone dates are stored
- M1–M6 are shared by all views
