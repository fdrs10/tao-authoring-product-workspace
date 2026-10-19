# AS_IS_ENTITY_LIFECYCLE_AND_RELATIONSHIP_MAP

**Date:** 2026-10-16 · **Mode:** READ-ONLY · **Data model:** current schema (Alembic head = `0007_candidate_enrichment`)

---

## Entity inventory

| Entity | Table | PK | Active? | Description |
|---|---|---|---|---|
| Source | `sources` | source_id | ✅ | Governed Source registry (9 active + 1 historical) |
| Evidence Signal | `source_evidence` | evidence_id | ✅ | 426 signals — Source Truth layer |
| Capability Candidate | `capability_candidates` | candidate_id | ✅ | 34 reconciled candidates (governance + enrichment) |
| Canonical Capability | `capabilities` | cap_id | ✅ (active=CANDIDATE) / 📦 (HISTORICAL) | 34 CAND-Fxx (active) + 135 CAP-xxxx (historical) |
| Feature | `features` | feat_id | ✅ | 0 records — API exists, no data, no UI |
| Feature↔Capability | `feature_capabilities` | (feat_id, cap_id) | ✅ | M:N join |
| Milestone | `milestones` | milestone_id | ✅ | M1–M6 governed baseline |
| Customer | `customers` | customer_id | ✅ (empty, D3) | Model ready, data pending |
| Customer↔Capability | `customer_capabilities` | (customer_id, cap_id) | ✅ | M:N join |
| Market | `markets` | market_id | ✅ | 6 governed markets |
| Capability↔Market | `capability_markets` | (cap_id, market_id) | ✅ | M:N |
| Jira Ticket | `jira_tickets` | jira_key | ✅ | 28 records (delivery evidence) |
| Jira↔Capability | `capability_jira` | (cap_id, jira_key) | ✅ | M:N |
| Outcome | `roadmap_outcomes` | horizon | ✅ | 3 horizons (0-6m, 7-24m, tail) |
| Roadmap Timing | `roadmap_timing` | cap_id | ✅ | start_month + duration_months per capability |
| Audit Event | `audit_events` | audit_id | ✅ | Append-only; actor, before, after |
| Report Generation | `report_generations` | generation_id | ✅ | Versioned report snapshots |
| Source Capability (historical) | `source_capabilities` | source_capability_id | 📦 | Old 224-row evidence layer (pre-analysis) |
| Feature Composition (package) | (json field in source_evidence) | — | 📦 | Feature ID(s) from the package analysis |

## Relationship map

```
Sources (9)
├── source_evidence (426) ──── reconciled_family_id ──→ Capability Candidates (34)
│   └── current_canonical_cap_id ──→ capabilities (historical CAP-xxxx)
│
├── capability_sources ──→ capabilities (source-level lineage)
│
Capability Candidates (34)
├── cap_id ──→ capabilities (CAND-Fxx, population=SOURCE_ANALYSIS_CANDIDATE)
├── is_focus / focus_markets
├── ideation_disposition (ACTIVE / NOT SELECTED)
├── enrichment (jsonb: definition, context, evidence, delivery, review)
├── promotion_rationale (when promoted from evidence)
│
capabilities (active: 34 CAND-Fxx; historical: 135 CAP-xxxx)
├── capability_markets ──→ markets (6)
├── capability_sources ──→ sources
├── capability_jira ──→ jira_tickets (28)
├── roadmap_timing (start_month, duration_months, version)
├── customer_capabilities ←── customers (M:N)
├── feature_capabilities ←── features (M:N)
│
milestones (M1–M6)
└── (shared by Roadmap lines, Migration intervals, Customer Plan intervals)

customers
├── customer_capabilities ──→ capabilities (required capabilities)
├── earliest_milestone_interval (e.g. M3 -> M4)
├── derived: migration_plan.readiness / blocked / available
│
features
└── feature_capabilities ──→ capabilities (M:N)
```

---

## Lifecycle: CAND-Fxx → Product Review = CONFIRMED

**Current behaviour (verified):**

When Product changes `product_review_status = 'CONFIRMED'` on a CAND-Fxx:

1. `PATCH /api/capabilities/CAND-F01` → `product_review_status = 'CONFIRMED'`
2. `capabilities.product_review_status` changes from NULL to 'CONFIRMED'
3. `capabilities.version` increments (optimistic concurrency)
4. `audit_events` records actor, before (NULL), after ('CONFIRMED')
5. **The row remains `CAND-F01`** — cap_id does NOT change
6. **The row remains in `population='SOURCE_ANALYSIS_CANDIDATE'`** — no population transition
7. **It does NOT enter the Backlog automatically** — the Backlog already shows it (same table)
8. **It does NOT enter the Roadmap automatically** — Roadmap Admission remains NULL
9. **No new entity is created** — the existing capability row is updated in place

**What is NOT implemented:**

- No lifecycle state machine (ACTIVE → REVIEWED → ADMITTED → COMMITTED)
- No automatic population transition on review
- No automatic MoSCoW assignment
- No automatic Roadmap Admission on CONFIRMED
- No canonical re-numbering (CAND-Fxx → CAP-xxxx transition)
- No archiving of the old 135 on confirmation

---

## Where the journey breaks

| Entity | Can I see where it came from? | Can I see what it became? | Can I see which Customers need it? | Can I see it on the Roadmap? |
|---|---|---|---|---|
| Source Evidence (426) | ✅ source_id, provenance | ✅ reconciled_family_id → candidate | ✅ candidate → customer_capabilities | ⚠️ via candidate → roadmap_timing |
| Candidate (CAND-Fxx) | ✅ enrichment.evidence | ✅ (it IS a capability) | ✅ via customer_capabilities | ⚠️ only if roadmap_timing exists |
| Capability (historical CAP-xxxx) | ✅ capability_sources | 📦 historical — no active path | 📦 old customer_capabilities (historical) | 📦 old roadmap_timing (historical) |
| Feature (FEAT-xxxx) | ✅ feature_capabilities | ✅ composition of capabilities | ❌ no customer→feature link | ⚠️ derived window only |
| Customer | N/A | ✅ required capabilities | ✅ its own plan | ✅ via its plan's readiness |
| Milestone (M1–M6) | ✅ source_lineage | ✅ shared by all views | ✅ via customer intervals | ✅ roadmap lines |
