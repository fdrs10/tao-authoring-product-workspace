# SOURCE_ANALYSIS_FUNNEL_MODEL — the governed Product funnel

**Date:** 2026-10-16 · **Source of record:** `TAO_Authoring_Capability_Evidence_Focus_Guide_v1_4_VERIFIED` (md5 `e4d70bb9…`)

```
9 GOVERNED SOURCES
   SRC-3X-001 · SRC-V1-001 · SRC-GAP-001 · SRC-NEW-001 · SRC-COMP-001
   SRC-JIRA-001 · SRC-OECD-001 · SRC-NYSED-001 · SRC-STRATEGY-001
        ↓  extraction (per-Source rules, literal where the Source is literal)
426 SOURCE EVIDENCE SIGNALS            (source_evidence — Source Truth layer)
        ↓  Capability Analysis (consolidation / disposition / provenance)
34 CAPABILITY CANDIDATES               (capability_candidates + capabilities
        ↓                                 population = SOURCE_ANALYSIS_CANDIDATE)
15 CROSS-MARKET FOCUS CAPABILITIES     (is_focus — a Product recommendation view)
        ↓
IDEATION → PRODUCT BACKLOG → ROADMAP ADMISSION → ROADMAP → MIGRATION → CUSTOMER PLANS
```

## Layers

| Layer | Storage | Nature |
|---|---|---|
| Source Registry | `sources` (+ evidence_class/authority/extraction_rule) | 9 governed Sources with materialised artifacts |
| Evidence | `source_evidence` (426) | **Source Truth** — what each Source says; never canonical |
| Capability Analysis | `reconciliation_register` (package) + candidate consolidation | how 426 signals became 34 families |
| Candidates | `capability_candidates` + `capabilities` (population=`SOURCE_ANALYSIS_CANDIDATE`) | **active working population** for Ideation/Backlog/Roadmap/Migration/Reports |
| Historical baseline | `capabilities` (population=`HISTORICAL_BASELINE_V1`, 135) | preserved reference — never active |

## Population rule (§6/§19)

`GET /api/capabilities` default returns the **ACTIVE** population: `SOURCE_ANALYSIS_CANDIDATE` rows when any exist, otherwise the non-historical population (pre-ingestion environments). `?population=historical` → the 135 baseline; `?population=all` → everything. The historical baseline is never mixed into the active view (tested).

## Governance actions (§8/§9)

| Action | Endpoint | Rules |
|---|---|---|
| Promote evidence → Candidate | `POST /api/candidates/{id}/promote` | evidence_id + name + **rationale** required; new family id (F-sequence); full lineage to the Source Evidence; audit; active count +1 |
| Remove from Ideation | `PATCH /api/candidates/{id}` | `ideation_disposition = NOT SELECTED FOR IDEATION` + rationale; optimistic version (409 stale); record kept, audit written |
| Restore | same PATCH with `ACTIVE FOR IDEATION` | audited |

MEXCBT / Uchida is a first-class dimension at every layer: per-signal `mexcbt_relevance`, per-candidate `mexcbt_signals`, dedicated Focus set, and independent filters on the Evidence, Analysis, Candidates and Ideation views.
