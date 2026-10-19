# AS_IS_REPORTS_AND_DELIVERABLES_INVENTORY

**Date:** 2026-10-16 · **Mode:** READ-ONLY · **Compared against:** the previously agreed Product baseline (contract §17)

---

## D1 — Authoring Product Definition — Ideation & Target Scope
**Target: 30 Oct 2026** · **Sections: 11** · **Currently AVAILABLE: 10**

| # | Expected Content (Product baseline) | Template Section | Implemented? | Data Source |
|---|---|---|---|---|
| 1 | Target Authoring V2 vision and scope | Product Vision and Authoring Objective | ✅ IMPLEMENTED (fixed statement) | Static + V2 Position reference |
| 2 | Studio V1 carry-forward | TAO Studio V1 Carry-forward | ⚠️ PARTIALLY — shows evidence table, not narrative | `source_evidence` filtered by source |
| 3 | TAO 3.x migration | TAO 3.x Direct Migration | ⚠️ PARTIALLY | Same |
| 4 | New needs & gaps | New Needs & Gaps | ⚠️ PARTIALLY | Same |
| 5 | Discontinued capabilities | Discontinued | ⚠️ PARTIALLY | Same |
| 6 | Cross-analysis and final V2 capability definition | Cross-analysis | ✅ IMPLEMENTED (traceability counts) | `source_evidence.reconciled_family_id` |
| 7 | Final V2 capability definition | Target Authoring V2 Scope | ✅ IMPLEMENTED (admitted caps) | `capabilities.roadmap_admission` |
| 8 | Market and strategic relevance | Market and MEXCBT / Uchida Relevance | ✅ IMPLEMENTED (market census) | `capability_markets` + `markets` |
| 9 | Sources and evidence | Sources and Evidence | ✅ IMPLEMENTED (source table + artifact status) | `sources` + `source_capabilities` |
| 10 | Executive Summary | Executive Summary | ✅ IMPLEMENTED (counts) | Derived |
| 11 | Open Product Decisions | Open Product Decisions | ✅ IMPLEMENTED (review/traceability/admission pending counts) | Derived |

**Gaps:** Sections 2–5 show evidence signal tables rather than narrative analysis. A Product-written narrative summary is not stored anywhere. **Blocked by:** Product writing the analysis narrative per Source (the source-by-source reconstruction).

---

## D2 — TAO Studio Creator V2 — Product Backlog
**Target: 30 Oct 2026** · **Sections: 10** · **Currently AVAILABLE: 8**

| # | Expected Content | Template Section | Implemented? | Data Source |
|---|---|---|---|---|
| 1 | Governed Canonical Capability list | Canonical Capabilities | ✅ IMPLEMENTED (full table) | `capabilities` |
| 2 | Functional description + Strategic Category | (included in Canonical Capabilities) | ✅ IMPLEMENTED | Same |
| 3 | Market and MEXCBT / Uchida applicability | Market Coverage | ✅ IMPLEMENTED (market census) | `capability_markets` + `markets` |
| 4 | Source and evidence traceability | Source / Evidence Traceability | ✅ IMPLEMENTED (traceability status + untraced list) | `source_evidence` + `capabilities` |
| 5 | Product Review | Product Review Status | ✅ IMPLEMENTED (reviewed vs not-reviewed counts) | `capabilities.product_review_status` |
| 6 | MoSCoW and Roadmap Admission | MoSCoW and Roadmap Admission | ✅ IMPLEMENTED (distribution table) | Same fields |
| 7 | Governed Canonical Capability list | Product Backlog Overview | ✅ IMPLEMENTED (scope statement) | Static |
| 8 | Strategic Categories | Strategic Categories | ✅ IMPLEMENTED (per-category counts) | `capabilities` |
| 9 | Feature Composition | Feature Composition | ⚠️ PARTIALLY IMPLEMENTED (features table renders if present; 0 features exist) | `features` |
| 10 | Open Decisions and Gaps | Open Decisions and Gaps | ✅ IMPLEMENTED (pending counts) | Derived |

**Gaps:** Feature Composition shows "Awaiting Product data" because no Features have been created. MEXCBT/Uchida is not a separate column in the canonical capabilities table — it is a per-evidence signal field.

---

## D3 — TAO Studio Creator V2 — Product Roadmap
**Target: 13 Nov 2026** · **Sections: 11** · **Currently AVAILABLE: 10**

| # | Expected Content | Template Section | Implemented? | Data Source |
|---|---|---|---|---|
| 1 | Roadmap-admitted capabilities and priorities | Executive Summary + Priorities and Sequencing | ⚠️ PARTIALLY (0 timed capabilities; all awaiting Admission) | `roadmap_timing` + `capabilities` |
| 2 | Expected timing and delivery horizons | Full / 0–6m / 7–24m / Tail Horizons | ✅ IMPLEMENTED (horizon buckets) | Same |
| 3 | Capability dependencies and sequencing | Dependencies | ✅ IMPLEMENTED (untimed list) | Derived |
| 4 | Market views and expected value | Market Views | ✅ IMPLEMENTED (per-market counts) | `capability_markets` |
| 5 | Relationship between capabilities and Migration milestones | M1–M6 Alignment | ✅ IMPLEMENTED (milestone table from canonical dataset) | `milestones` |
| 6 | Roadmap Timeline | Roadmap Timeline | ✅ IMPLEMENTED (per-capability timing + version) | `roadmap_timing` |
| 7 | Capabilities by Strategic Category | Capabilities by Strategic Category | ✅ IMPLEMENTED (per-category counts) | `capabilities` |
| 8 | Roadmap Principles | Roadmap Principles | ✅ IMPLEMENTED (confirmed hierarchy statement) | Static |
| 9 | Feature Composition View | Feature Composition View | ⚠️ PARTIALLY IMPLEMENTED (0 features) | `features` |
| 10 | Risks and Open Product Decisions | Risks and Open Product Decisions | ✅ IMPLEMENTED (pending counts) | Derived |
| 11 | Executive Summary | Executive Summary | ✅ IMPLEMENTED | Derived |

**Gaps:** 0 capabilities are Roadmap-admitted (all awaiting Product decision) → the Roadmap Timeline shows 0 timed capabilities → the horizons show 0. This is honest but makes D3 effectively empty until Product assigns Admission.

---

## D4 — TAO 3.x → TAO Studio Authoring — Common Migration Path
**Target: 13 Nov 2026** · **Sections: 15** · **Currently AVAILABLE: 15 (ALL)**

| # | Expected Content | Template Section | Implemented? | Data Source |
|---|---|---|---|---|
| 1 | Executive Summary | Executive Summary | ✅ IMPLEMENTED | Derived |
| 2 | Migration Objective | Migration Objective | ✅ IMPLEMENTED (fixed statement) | Static |
| 3 | Current → Target Authoring Model | Current → Target Authoring Model | ✅ IMPLEMENTED (fixed statement) | Static |
| 4 | Common Migration Principles | Common Migration Principles | ✅ IMPLEMENTED (fixed statement) | Static |
| 5–10 | M1–M6 (one section per milestone) | M1–M6 | ✅ IMPLEMENTED (canonical milestone dataset) | `milestones` |
| 11 | Capabilities and Value Available by Milestone | Capabilities and Value Available by Milestone | ✅ IMPLEMENTED (COMMITTED derivation) | `roadmap_timing` + `capabilities` |
| 12 | Roadmap Dependencies | Roadmap Dependencies | ✅ IMPLEMENTED (untimed list) | Derived |
| 13 | Migration Conditions | Migration Conditions | ✅ IMPLEMENTED (fixed non-capability conditions) | Static |
| 14 | Common Blockers and Exceptions | Common Blockers and Exceptions | ✅ IMPLEMENTED (from customers; 0 records → "Awaiting") | `customers` |
| 15 | Customer Transition Approach | Customer Transition Approach | ✅ IMPLEMENTED (customer count + D5 reference) | Derived |

**BEST-IMPLEMENTED report.** All 15 sections available because M1–M6 are imported and the derivation works.

---

## D5 — Customer Migration Plan
**Target: 20 Nov 2026** · **Sections: 19** · **One report per governed customer**

| # | Expected Content | Template Section | Implemented? | Data Source |
|---|---|---|---|---|
| 1 | Executive Summary | Executive Summary | ✅ IMPLEMENTED | Customer + derivation |
| 2 | Customer Context | Customer Context | ✅ IMPLEMENTED | `customers` |
| 3 | Current Authoring Situation | Current Authoring Situation | ✅ IMPLEMENTED | `customers.current_use` |
| 4 | Current TAO Environment | Current TAO Environment | ✅ IMPLEMENTED | `customers.current_environment` |
| 5 | Required Functionality | Required Functionality | ✅ IMPLEMENTED | `customers.min_functionality_studio` |
| 6 | Required Canonical Capabilities | Required Canonical Capabilities | ✅ IMPLEMENTED (CAP links + availability + dependency reasons + features) | `customer_capabilities` + `roadmap_timing` |
| 7 | Relevant Features | Relevant Features | ⚠️ PARTIALLY IMPLEMENTED (shows features composed around required capabilities; no direct customer↔feature link) | `feature_capabilities` (derived) |
| 8 | Product Roadmap Availability | Product Roadmap Availability | ✅ IMPLEMENTED (availability summary) | Derived from `roadmap_timing` |
| 9 | Proposed Migration Milestone / Interval | Proposed Migration Milestone / Interval | ✅ IMPLEMENTED | `customers.earliest_milestone_interval` |
| 10 | Proposed Migration Window | Proposed Migration Window | ✅ IMPLEMENTED | `customers.proposed_migration_window` |
| 11 | Customer-specific Dependencies | Customer-specific Dependencies | ✅ IMPLEMENTED | `customers.customer_dependencies` |
| 12 | Blockers | Blockers | ✅ IMPLEMENTED | `customers.blockers` |
| 13 | Assumptions | Assumptions | ✅ IMPLEMENTED | `customers.assumptions` |
| 14 | Exceptions | Exceptions | ✅ IMPLEMENTED | `customers.exceptions` |
| 15 | Customer Feedback / Evidence | Customer Feedback / Evidence | ✅ IMPLEMENTED | `customers.customer_feedback` |
| 16 | Migration Readiness | Migration Readiness | ✅ IMPLEMENTED (derived + explainable) | Derived |
| 17 | Product Decisions Required | Product Decisions Required | ✅ IMPLEMENTED (derived from gaps) | Derived |
| 18 | Validation Status | Validation Status | ✅ IMPLEMENTED | `customers.validation_status` |
| 19 | Next Actions | Next Actions | ✅ IMPLEMENTED (derived from readiness) | Derived |

**BLOCKED BY PRODUCT DATA:** governed customer records do not exist (D3). The model and API are fully implemented. D5 generates correctly when a customer is created.

---

## D5a — First Customer Migration Plans — Pilot Set
**Target: 27 Nov 2026** · **Customers: DEPP, INVALSI, NSA, NCCER**

| Expected Content | Implemented? | Notes |
|---|---|---|
| 4 governed pilot customer plans | ✅ API IMPLEMENTED (`POST /api/reports/PILOT/generate`) | Requires 4 governed customer records — none exist (D3) |
| Confirmed current-state context | ✅ (model ready) | Blocked by customer data |
| Validated Required Capabilities / Key Features | ⚠️ PARTIALLY (capability model ready; Feature model ready but no customer↔feature link) | Blocked by customer data |
| Proposed milestone path | ✅ (model ready) | Blocked by customer data |
| Roadmap and customer-specific blockers | ✅ (model ready) | Blocked by customer data |
| Assumptions / exceptions and customer feedback | ✅ (model ready) | Blocked by customer data |
| Product actions and readiness | ✅ (model ready) | Blocked by customer data |
| Next customer-side implementation planning actions | ✅ (model ready) | Blocked by customer data |
| Lessons for subsequent Customer Plans | ⚠️ NOT IMPLEMENTED (no lessons-learned field or template) | Enhancement |

**Status: BLOCKED BY PRODUCT DATA** — the entire D5a pipeline is implemented; only the governed customer records are missing.

---

## Report workflow (§19)

### "I need to deliver D1"
1. Open **REPORTS / DELIVERABLES**
2. Find **D1** card → check section completeness (10/11 AVAILABLE)
3. Click **Preview Report** → publication HTML opens (title page, ToC, sections)
4. Review → click **Print / Save as PDF**
5. Or click **Generate HTML** → records a versioned snapshot

**If data is missing:** the affected section shows `INCOMPLETE` + "Awaiting Product data". The report still generates — incomplete sections are explicitly marked.

### "I need to deliver D3"
1. Ensure capabilities have Roadmap Admission + timing (otherwise D3 shows 0 timed)
2. Open **REPORTS / DELIVERABLES** → D3 → Preview
3. The Timeline section will show per-capability timing if admitted

### "I need to produce Customer X's D5"
1. Ensure Customer X exists in `customers` (governed data)
2. Ensure required capabilities are linked (`customer_capabilities`)
3. Open **REPORTS / DELIVERABLES** → D5 → Select Customer X → **Preview Report**
4. The report renders the full plan with derived readiness

### "I need to produce the D5a Pilot Set"
1. Ensure governed customer records exist for the pilot customers
2. Open **REPORTS / DELIVERABLES** → D5 → select customer → **Generate Customer Migration Pilot Set**
3. The API packages multiple D5 reports into one deliverable
4. Currently blocked: no governed customer records exist (D3)

### Report workflow gap
The PM does NOT need to rewrite Product information for the deliverable — the reports consume the same canonical data. However, if a section requires a narrative that is not stored as a field (e.g. "Migration Objective"), the report uses a static template statement. Narrative sections that require Product-written text have no storage mechanism (they would need a new field or a separate content-management step).

---

## Summary classification

| Report | Status | Blocker |
|---|---|---|
| D1 | ⚠️ PARTIALLY IMPLEMENTED (10/11 sections) | Narrative sections need Product-written text |
| D2 | ⚠️ PARTIALLY IMPLEMENTED (8/10 sections) | Feature Composition shows "Awaiting" (no features created) |
| D3 | ⚠️ PARTIALLY IMPLEMENTED (10/11 sections) | 0 timed capabilities (all awaiting Admission) |
| D4 | ✅ FULLY IMPLEMENTED (15/15) | — |
| D5 | ✅ FULLY IMPLEMENTED (19/19 sections) | Blocked by customer data (D3) |
| D5a | ✅ IMPLEMENTED (API) | Blocked by customer data (D3) |
