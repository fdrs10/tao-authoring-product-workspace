# AS_IS_PM_SCENARIO_WALKTHROUGHS — Final gap table

**Date:** 2026-10-16 · **This is the single summary table from the AS-IS analysis.**

| Function | Exists? | Backend? | UI? | Editable? | Audited? | Usable by PM? | Where / Evidence |
|---|---|---|---|---|---|---|---|
| **Evidence** | | | | | | | |
| Evidence Explorer (browse 426) | YES | YES | PARTIAL | NO | N/A | PARTIAL | Sources → Evidence tab (flat table, no search/filter) |
| Search / filter 426 | NO | YES (API params) | NO | N/A | N/A | NO | API: GET /api/evidence?source=…&mexcbt=…&q=… |
| Open single evidence record | NO | N/A | NO | N/A | N/A | NO | No evidence-detail modal; only row in a table |
| See evidence's Source | YES | YES | YES | N/A | N/A | YES | source_id column in evidence table |
| See evidence → Candidate | YES | YES | PARTIAL | N/A | N/A | PARTIAL | reconciled_family_id shown in analysis lens |
| Understand consolidation | PARTIAL | YES | PARTIAL | N/A | N/A | PARTIAL | Candidate enrichment explains why; evidence table shows treatment |
| **Promote Evidence → Candidate** | YES | YES | NO | NO | YES | NO | API: POST /api/candidates/{id}/promote |
| **Candidate / Capability** | | | | | | | |
| View 34 Candidates | YES | YES | YES | N/A | N/A | YES | Ideation 00 workspace |
| Open Candidate modal | YES | YES | YES | N/A | N/A | YES | Universal CAP modal from any CAP-ID link |
| Edit name / definition / scope | YES | YES | YES | YES | YES | YES | CAP modal → Edit → Save |
| Change Strategic Category | YES | YES | YES | YES | YES | YES | CAP modal → Edit → Strategic Category |
| Change Markets | YES | YES | YES | YES | YES | YES | CAP modal → Edit → Market checkboxes |
| Change MEXCBT / Uchida | NO | NO | NO | N/A | N/A | NO | Per-evidence signal field; no candidate-level MEXCBT editing |
| See Sources | YES | YES | YES | N/A | N/A | YES | CAP modal → Sources & Evidence table |
| See supporting Evidence | YES | YES | YES | N/A | N/A | YES | CAP modal → Source capability lineage table |
| See Jira | YES | YES | YES | N/A | N/A | YES | CAP modal → Jira section + deep links |
| See Focus rationale | PARTIAL | YES | PARTIAL | N/A | N/A | PARTIAL | focus_markets shown; no explicit focus rationale field |
| Change Product Review | YES | YES | YES | YES | YES | YES | CAP modal → Edit → Product Review dropdown |
| Change Ideation disposition | YES | YES | NO | YES | YES | NO | API: PATCH /api/candidates/{id} |
| Set MoSCoW | YES | YES | YES | YES | YES | YES | CAP modal → Edit → MoSCoW; Cross-analysis; Backlog |
| Set Roadmap Admission | YES | YES | YES | YES | YES | YES | Cross-analysis / Backlog inline; CAP modal |
| Candidate → Capability lifecycle | YES | YES | YES | YES | YES | YES | In-place update; no transition needed (same entity) |
| **Features** | | | | | | | |
| Feature workspace | NO | YES | NO | N/A | N/A | NO | Roadmap → Features tab (view only); no standalone workspace |
| Create Feature | YES | YES | NO | YES | YES | NO | API: POST /api/features |
| Edit Feature | YES | YES | PARTIAL | YES | YES | PARTIAL | Roadmap → Features → Edit |
| Feature ↔ Capability M:N | YES | YES | YES | YES | YES | PARTIAL | Roadmap → Features → Edit → add/remove via CAP-ID input |
| Feature timing | NO | NO | NO | N/A | N/A | NO | Derived coverage only — no independent Feature timing |
| **Customers** | | | | | | | |
| Customer workspace | YES | YES | YES | YES | YES | YES | Migration → Customer Plans tab |
| Create Customer | YES | YES | YES | YES | YES | YES | Migration → Customer Plans → Register customer |
| Edit Customer (all plan fields) | YES | YES | YES | YES | YES | YES | Customer Plan → Edit plan |
| Customer ↔ Capability | YES | YES | PARTIAL | YES | YES | PARTIAL | API: POST/DELETE customer_capabilities; shown in Plan |
| Customer ↔ Feature | NO | NO | NO | N/A | N/A | NO | NOT IMPLEMENTED |
| **Migration** | | | | | | | |
| Common Migration Path (M1–M6) | YES | YES | YES | YES (milestones) | YES | YES | Migration Path tab |
| Customer Migration Plan | YES | YES | YES | YES (plan fields) | YES | YES | Migration → Customer Plans → Open Plan |
| Customer milestone-by-milestone plan | NO | NO | NO | N/A | N/A | NO | Only earliest_milestone_interval |
| Roadmap/customer conflict detection | NO | YES (derived) | PARTIAL | N/A | N/A | PARTIAL | Readiness = BLOCKED shows reason; no gap visualisation |
| **Roadmap** | | | | | | | |
| Roadmap (bars, drag, resize, snap) | YES | YES | YES | YES | YES | YES | Roadmap → Capabilities tab |
| Roadmap honest empty state | YES | YES | YES | N/A | N/A | YES | Shows "Awaiting Product Roadmap Admission" |
| **Reports** | | | | | | | |
| D1 generation | YES | YES | YES | N/A | YES | YES | Reports → D1 → Preview / Generate |
| D2 generation | YES | YES | YES | N/A | YES | YES | Reports → D2 → Preview / Generate |
| D3 generation | YES | YES | YES | N/A | YES | YES | Reports → D3 → Preview / Generate |
| D4 generation | YES | YES | YES | N/A | YES | YES | Reports → D4 → Preview / Generate |
| D5 generation (per customer) | YES | YES | YES | N/A | YES | YES | Reports → D5 → Select customer → Preview / Generate |
| D5a Pilot Set generation | YES | YES | YES | N/A | YES | PARTIAL | Reports → D5 → Pilot Set (requires governed customers) |
| **Traceability** | | | | | | | |
| View Journey / end-to-end traceability | NO | PARTIAL | NO | N/A | N/A | NO | Lineage exists per-layer; no unified "View Journey" |
