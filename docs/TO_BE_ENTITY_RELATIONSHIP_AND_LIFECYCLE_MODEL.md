# TO_BE_ENTITY_RELATIONSHIP_AND_LIFECYCLE_MODEL

**Date:** 2026-10-16 · **Schema changes from AS-IS:** Alembic `0008_collaboration` + `0009_customer_features`

## Entity lifecycle states

```
Evidence Signal
├── UNREPRESENTED (not consolidated into any Candidate)
├── CONSOLIDATED (reconciled_family_id → Candidate)
└── PROMOTED (explicitly promoted to Product consideration by PM)

Capability Candidate (= active Capability)
├── ideation_disposition: ACTIVE FOR IDEATION | NOT SELECTED FOR IDEATION
├── product_review_status: NULL | REVIEW_REQUIRED | CONFIRMED | CONFIRMED_WITH_CHANGES | REJECTED
├── population: SOURCE_ANALYSIS_CANDIDATE (never HISTORICAL in active views)
└── cap_id: CAND-Fxx (stable; CAP-xxxx renaming deferred to Product decision)

Feature
├── status: Draft | Committed | (Product-defined)
└── lifecycle: create → compose capabilities → assign customers → derive timing

Customer
├── validation_status: Not assessed | Hypothesis | Customer validated | Migration committed
└── readiness (derived): BLOCKED / VALIDATION REQUIRED / PRODUCT DECISION REQUIRED / READY / EXCEPTION
```

## New relationships (TO-BE)

| Relationship | Table | Cardinality | Purpose |
|---|---|---|---|
| Customer ↔ Feature | `customer_features` | M:N | Key Features per customer (KEY/REQUIRED/RELEVANT) |
| Comment ↔ any entity | `comments` | 1:N polymorphic | Discussion threads |
| Evidence → Candidate promotion | tracked via `provenance` + audit | 1:1 | Full lineage preserved |

## Schema changes

### `0008_collaboration`
```sql
CREATE TABLE comments (
  comment_id bigserial PRIMARY KEY,
  entity_type text NOT NULL,
  entity_id text NOT NULL,
  parent_id bigint REFERENCES comments(comment_id),
  author text NOT NULL,
  comment text NOT NULL,
  resolved boolean NOT NULL DEFAULT false,
  created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX idx_comments_entity ON comments (entity_type, entity_id);
```

### `0009_customer_features`
```sql
CREATE TABLE customer_features (
  customer_id text NOT NULL REFERENCES customers(customer_id),
  feat_id text NOT NULL REFERENCES features(feat_id),
  importance text NOT NULL DEFAULT 'REQUIRED'
    CHECK (importance IN ('KEY','REQUIRED','RELEVANT')),
  required_for_migration boolean NOT NULL DEFAULT false,
  required_by_milestone text,
  rationale text,
  validation_status text DEFAULT 'PRODUCT_HYPOTHESIS',
  customer_feedback text,
  notes text,
  version bigint NOT NULL DEFAULT 1,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (customer_id, feat_id)
);
```

### `0010_candidate_enrichment_fields`
```sql
ALTER TABLE capability_candidates
  ADD COLUMN functional_definition text,
  ADD COLUMN what_it_enables text,
  ADD COLUMN user_problem text,
  ADD COLUMN functional_scope text,
  ADD COLUMN out_of_scope text,
  ADD COLUMN owner text,
  ADD COLUMN strategic_category text;
```

## Legacy handling

The 135 historical caps remain in `capabilities` with `population='HISTORICAL_BASELINE_V1'`. They are queryable via `?population=historical` but excluded from all active views by the population rule. They are **not deleted, not renumbered, not merged** without an explicit Product decision.
