# AS_IS_DOCUMENTATION_STATUS

**Date:** 2026-10-16 · **Classification:** CURRENT / PARTIALLY STALE / STALE / TECHNICAL ONLY / PRODUCT-MANAGER USABLE

---

| Document | Status | Classification | Notes |
|---|---|---|---|
| `PRODUCT_UAT_GUIDE.md` | PARTIALLY STALE | PRODUCT-MANAGER USABLE | Good walkthrough but written before the controlled ingestion; candidate counts and population changed (4→34; evidence now 426). Scenario paths still valid. |
| `REFERENCE_IMPLEMENTATION_MATRIX.md` | CURRENT | TECHNICAL ONLY | Up-to-date with all addenda; useful for architecture reference, not for PM daily use. |
| `REPORT_TEMPLATE_CONTRACTS.md` | CURRENT | TECHNICAL ONLY | Accurate section contracts for D1–D5. |
| `REPORTS_DELIVERABLES_MODEL.md` | CURRENT | TECHNICAL ONLY | Accurate model description. |
| `CUSTOMER_MIGRATION_PLAN_MODEL.md` | CURRENT | TECHNICAL ONLY | Accurate model + derivation rules. |
| `SOURCE_ANALYSIS_FUNNEL_MODEL.md` | CURRENT | TECHNICAL ONLY | Accurate funnel description. |
| `CAPABILITY_CANDIDATE_GOVERNANCE.md` | CURRENT | TECHNICAL ONLY | Accurate governance rules. |
| `CAPABILITY_MODAL_INFORMATION_MODEL.md` | CURRENT | TECHNICAL ONLY | Accurate modal information model. |
| `FEATURE_MODEL.md` | CURRENT | TECHNICAL ONLY | Accurate Feature model. |
| `SOURCE_DOCUMENT_COVERAGE_REPORT.md` | CURRENT | TECHNICAL ONLY | Accurate artifact coverage. |
| `SOURCE_ANALYSIS_INGESTION_INVENTORY.md` | CURRENT | TECHNICAL ONLY | Accurate package inventory. |
| `CLOUD_HANDOFF_CURRENT_HEAD.md` | PARTIALLY STALE | TECHNICAL ONLY | Needs updating after the population-rule fixes; the bootstrap pipeline changed. |
| `DEPLOYMENT_RUNBOOK.md` | PARTIALLY STALE | TECHNICAL ONLY | Pre-population-rule; bootstrap steps need updating. |
| `DATA_OPERATIONS_RUNBOOK.md` | CURRENT | TECHNICAL ONLY | Accurate backup/restore/import procedures. |
| `NOVEMBER_PRODUCT_OUTCOMES.md` | CURRENT | PRODUCT-MANAGER USABLE | Clear outcome descriptions. |
| `CUSTOMER_MIGRATION_UAT_GUIDE.md` | CURRENT | PRODUCT-MANAGER USABLE | Good walkthrough. |
| `PRODUCT_UAT_TEST_CASES.md` | PARTIALLY STALE | PRODUCT-MANAGER USABLE | Some test cases assume pre-ingestion counts. |
| `KNOWN_DEFECTS_REGISTER.md` | PARTIALLY STALE | PRODUCT-MANAGER USABLE | QA-1/QA-2 fixed; new findings from this analysis not yet added. |
| `PRODUCT_DECISIONS_PENDING.md` | CURRENT | PRODUCT-MANAGER USABLE | Accurate pending-decision list. |
| `SOURCE_RECONSTRUCTION_CONTRACT.md` | CURRENT | TECHNICAL ONLY | Accurate but the reconstruction has not started. |
| `AS_IS_PRODUCT_MANAGER_OPERATING_MODEL.md` | CURRENT | PRODUCT-MANAGER USABLE | This analysis. |
| `AS_IS_APPLICATION_SCREEN_AND_ACTION_INVENTORY.md` | CURRENT | PRODUCT-MANAGER USABLE | This analysis. |
| `AS_IS_ENTITY_LIFECYCLE_AND_RELATIONSHIP_MAP.md` | CURRENT | TECHNICAL ONLY | This analysis. |
| `AS_IS_CUSTOMER_FEATURE_MIGRATION_MODEL.md` | CURRENT | TECHNICAL ONLY | This analysis. |
| `AS_IS_REPORTS_AND_DELIVERABLES_INVENTORY.md` | CURRENT | PRODUCT-MANAGER USABLE | This analysis. |
| `AS_IS_PM_SCENARIO_WALKTHROUGHS.md` | CURRENT | PRODUCT-MANAGER USABLE | This analysis. |

## Missing documentation

| Missing | Why it matters |
|---|---|
| Product Manager Quick Start Guide (1 page: "how do I do X?") | PMs need a simple action→screen map |
| Feature workspace guide | Features have no UI yet; when they do, a guide will be needed |
| Data dictionary (field-level: what each column means in Product terms) | PMs see field names but may not understand the governed semantics |
| Evidence-to-Candidate mapping explanation | The consolidation logic (why 426 became 34) is in the analysis package but not explained in-app |
