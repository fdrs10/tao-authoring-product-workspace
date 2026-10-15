# REFERENCE IMPLEMENTATION MATRIX

**Date:** 2026-10-15 · **Status:** controlled implementation reference (contract §48) · **Scope:** Phase 4+ frontend
**Rule (§49):** newest HTML ≠ best implementation of every module. Product/Data model comes from governed datasets + Phase 1 reconciliation; behaviour per module comes from the designated reference below — nothing reimplemented from memory.

## Modules

| # | Module | Product Truth | Behaviour Reference | Visual Reference | Known Defects | Implementation Rules | Missing Artifacts |
|---|---|---|---|---|---|---|---|
| 1 | **Sources & Evidence** | canonical sources/source capabilities + SRC-JIRA-001 (§5) | KINCHI effective handoff (prototype incomplete — §20) | v38.6 (spaces only) | Defect 2: source/Jira-backlog opening + drill-down incomplete; Defect 3: Source CAP → canonical CAP navigation | Sources\|Capabilities\|Customers entry points; human names not opaque IDs; Source→document and Source→sourcecap→CAP navigation; never invent documents | — |
| 2 | **Canonical Capability Modal (universal)** | canonical CAP | KINCHI effective requirements (§22–24) | v38.6 (as interaction seed only) | Defect 1: Add Jira Link broken; Defect 7: modality uneven | Same modal from **every** place a CAP-ID appears; 0..N Jira edit; NULL≠0 budgets; admission nullable | — |
| 3 | **Ideation (6 working areas)** | canonical data (ideation_sheet, decision) | v38.6 + v37.0 + effective requirements | v38.6 (compact density) | Prioritised Summary independence (Defect 5); summary regressions | Compact vertical Ideation index; Prioritised Summary = union of rendered decision blocks only; never own population | — |
| 4 | **Cross-analysis** | canonical data | effective requirements (prototype incomplete) | effective requirements | Defect 4: Roadmap Admission editable missing there | Admission edit from Cross-analysis, Backlog, and modal — one field, three views | — |
| 5 | **Product Backlog** | canonical data | effective requirements (prototype incomplete) | effective requirements | prototype incomplete | Filters: Strategic Cat / Market / MoSCoW / Admission / Visibility / Source; default MUST ok, All must be revealable; Jira columns where available | — |
| 6 | **Roadmap** | canonical CAP + roadmap_timing (135) | **v10 Roadmap HTML** (proven pointer drag/resize/snap — verified 2×pointerdown/2×pointermove/2×pointerup, 23 drag cfgs) + recovery markers verified in v38.6 (Strategic Cat ×10, 0–6, 7–24, Tail, Outcome, resize ×27) | v10 + v38.6 header pattern | DO NOT REBUILD (§32); Defect: rebuild pressure | Recover: 3-level hierarchy Category→Big Rock/Market→Feature(CAP), independent branch expansion, several-open, Full/0–6m/7–24m/Tail/Outcome, drag, L/R resize, month snap, persistence from backend, red vertical milestones labelled once, compact report quarter view | **v33 family ABSENT** from /legacy (see below) |
| 7 | **Quarter View** | Roadmap data (derived) | historical stable roadmap (v10) | v10 | must be report-style | Compact product-report layout: timeframe, Strategic Cat, Big Rock/Market, CAP-ID, capability, short desc, MoSCoW, Visibility, Jira/status/release, timing, milestones — no giant cards/modals | — |
| 8 | **Migration Path** | Roadmap timing + milestones + customers | **v35.6 vertical migration** (zip; verified VALUE / MIGRATION PATH / CAPABILIT… structure strings) | v35.6 | Defect 6: TS1/TS2/TS3 codes | Vertical 3-column VALUE/CAPABILITIES UNLOCKED | MIGRATION PATH | CUSTOMER TRANSITION PROJECTS; milestone intervals only (M3→M4), real milestone names; market legend always visible | — |
| 9 | **V2 Position** | Product composition equation (§28) | approved reference image | **assets/V2_POSITION_REFERENCE.png** | — | Never redesign again; preserve recognisable geometry | — |

## Required reference artifacts — physical verification (§47) ✅ done 2026-10-15
- A. `legacy/TAO_Authoring_v38_6_GOLDEN_BASELINE_REPAIRED.html` — **present** (2.0 MB, data-bearing)
- B. `legacy/TAO_Authoring_v37_0_CANONICAL_DATA_WORKSPACE.html` — **present** (clean canonical ancestor)
- C. `legacy/TAO_Authoring_v36_1_PROFESSIONAL_INTEGRATED.html` — **present**
- D. `legacy/TAO_Studio_Authoring_Action_Plan_Roadmap_v10.html` — **present** (contract names "..._v10(1).html"; same v10 numbered artifact, verified drag behaviours)
- E. **v33 Roadmap family — MISSING.** Names identified: `TAO_Authoring_Function_Ideation_Action_Plan_Migration_Roadmap_v33_36_COLLAPSIBLE_GAP_REGISTER.html`, `..._v33_35_HEADER_VERSION_CLEANUP.html`
- F. `legacy/TAO_Authoring_v35_6_MIGRATION_DIAGRAM(1).zip` — **present** (extracts to `TAO_Authoring_v35_6_MIGRATION_DIAGRAM.html`; vertical structure verified)
- G. `assets/V2_POSITION_REFERENCE.png` — **present**

## Missing artifact report (per §50 — only specific authoritative references)
| Artifact | Module requiring it | Why existing artifacts are insufficient | Blocking? |
|---|---|---|---|
| `TAO_Authoring_Function_Ideation_Action_Plan_Migration_Roadmap_v33_36_COLLAPSIBLE_GAP_REGISTER.html` (and v33_35 if available) | Roadmap + Quarter View | Contract names the v33 family + v10 as the *stable* behaviour references. v10 is present and verified (drag/resize/snap), so v33 is **nice-to-have corroboration**, not required to recover required behaviours. | **NO** for Phase 2. **Possibly yes** before Phase 7 (Roadmap) if v10 turns out to lack branch-expansion/quarter-report details — request Product supply then, and only then. |

No other missing artifacts.

## Phase 3 addendum (2026-10-15)
The API/shared-state contract introduced no new reference dependencies and no changes to any module's designated behaviour reference. Non-blocking technical note for Phase 9 CI hardening: `fastapi.testclient` emits a `StarletteDeprecationWarning` on httpx 0.28 (see Phase 3 test suite); evaluate `httpx2` when CI is hoisted. No action this phase.
