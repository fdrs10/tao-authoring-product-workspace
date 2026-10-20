# TO_BE_COLLABORATION_AND_DECISION_MODEL

**Date:** 2026-10-16

## Three concepts — never conflated

| Concept | Storage | Purpose | Immutable? |
|---|---|---|---|
| **Decision Rationale** | Entity field (e.g. `product_rationale`, `promotion_rationale`) | Why Product made a decision | Part of Truth; versioned with the entity |
| **Discussion** | `comments` table | Human conversation about an entity | Editable; can be resolved |
| **Audit History** | `audit_events` table | System record of what changed | Immutable; append-only |

## Ownership

Each Capability, Feature and Customer has an `owner` field. The owner is the PM responsible for that object. Ownership does not restrict editing (all PMs can edit), but it identifies who is accountable.

## Review workflow (lightweight)

1. PM A creates or edits an object
2. PM A (or the system) flags it as `NEEDS REVIEW`
3. PM B opens the object, sees the flag, reviews, sets `CONFIRMED` or `CONFIRMED_WITH_CHANGES`
4. Audit records the review action

No approval engine. No workflow engine. Just a status field + audit trail.

## Implementation

The existing `product_review_status` field on capabilities covers Capability review. For Features and Customers, a `validation_status` or `review_status` field serves the same purpose.

The `comments` table provides discussion. Comments are polymorphic (`entity_type` + `entity_id`) so they apply to any entity type.

The `audit_events` table already records all mutations with actor, before, after and changed fields. No changes needed.

## Recent Changes

The Home page "RECENT CHANGES" section queries `audit_events` for the most recent N events, grouped by entity type. No new storage needed.
