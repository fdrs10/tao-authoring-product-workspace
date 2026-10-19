# AS_IS_PM_SCENARIO_WALKTHROUGHS

**Date:** 2026-10-16 · **Mode:** READ-ONLY · **Each scenario documents the CURRENT workflow, gaps marked honestly**

---

## Scenario A — "I found something important among the 426 and want to bring it into Product consideration"

**START:** PM browses Sources & Evidence → Extracted Authoring Evidence

**CURRENT PATH:**
1. Sources & Evidence → tab "Extracted Authoring Evidence" → flat table of 426 signals
2. ⚠️ **No search, no filter, no pagination** — PM must scroll through all 426 rows
3. PM finds a signal → clicks its Source Capability ID (not a link, just text)
4. Evidence detail is not available inline — the PM must cross-reference with the Source's View Extracted tab
5. To promote: PM must use the API directly (`POST /api/candidates/F01/promote { evidence_id, name, rationale }`)
6. ⚠️ **No "Promote to Candidate" button exists in the UI**
7. After API promotion: the Candidate appears in Ideation 00 and the funnel count increments

**Data changed:** `capability_candidates` + `capabilities` + `audit_events`
**Final result:** new Candidate in the active population
**Missing:** Evidence Explorer UI with search/filter/promote; no evidence-detail modal; no inline "why was this consolidated/not selected" explanation

---

## Scenario B — "I want to create a completely new Capability"

**CURRENT PATH:**
1. Ideation 00 → open any existing Candidate → Edit → change fields → Save
2. ⚠️ **No "Create New Capability" button exists anywhere in the UI**
3. To create: PM must use the API (`POST /api/candidates/{id}/promote` from evidence, or direct SQL)
4. There is no "New Capability" modal or form

**Missing:** Capability creation workspace; CAP-ID generation for new (non-promoted) capabilities

---

## Scenario C — "I want to edit an existing Candidate/Capability"

**CURRENT PATH:**
1. Ideation 00 → click CAP-ID (e.g. CAND-F01) → universal CAP modal opens
2. Modal shows: canonical fields + enrichment sections + source lineage + Jira + budgets + timing
3. Click **Edit** → form appears with all editable fields
4. Edit: working name, description, strategic category, MoSCoW, Admission, visibility, owner, decision, ideation sheet, budgets, markets (checkboxes), Jira (add/remove), Product Review, rationale
5. Click **Save** → persisted with optimistic concurrency (409 on stale) + audit
6. ⚠️ **No Ideation disposition editing from the modal** (API only)
7. ⚠️ **Description is a consolidated text, not a Product-written definition**

**Data changed:** `capabilities` (version++, audit)
**Final result:** enriched Candidate definition updated
**Missing:** Ideation disposition editing; no "create new version" workflow; no field-level change highlighting

---

## Scenario D — "I want to create a Feature from several Capabilities"

**CURRENT PATH:**
1. ⚠️ **No Feature creation button exists in the UI**
2. Roadmap → Features tab shows existing Features (currently 0)
3. To create: PM must use the API (`POST /api/features { feat_id, name }`)
4. To add capabilities: API (`POST /api/features/{id}/capabilities/{cap_id}`)
5. After creation: the Feature appears in the Roadmap → Features tab

**Data changed:** `features` + `feature_capabilities` + `audit_events`
**Final result:** Feature exists with derived timing window
**Missing:** Feature creation workspace; Feature browser; Feature detail modal; Feature↔Customer link

---

## Scenario E — "I want to change an existing Feature"

**CURRENT PATH:**
1. Roadmap → Features tab → Edit button on a Feature
2. Modal: edit name, description, owner, status, notes
3. Add/remove capabilities via input + button
4. Save → persisted with optimistic concurrency

**Data changed:** `features` (version++, audit)
**Final result:** Feature updated
**Missing:** No Feature list outside the Roadmap; no Feature detail page; no Feature→Customer view

---

## Scenario F — "I want to make something more important"

Three different mechanisms, all separate:

| Mechanism | What it does | Where |
|---|---|---|
| **MoSCoW** | Assign Must/Should/Could/Won't to a Candidate | CAP modal → Edit → MoSCoW |
| **Roadmap Admission** | Admit a Candidate to the Roadmap (COMMITTED/CANDIDATE/DEFERRED/etc.) | Cross-analysis row dropdown or Backlog row dropdown or CAP modal |
| **Focus status** | Mark a Candidate as cross-market Focus | Not editable from the UI — set by the analysis package |

These are three separate decisions. The application does not conflate them.
**Missing:** No priority explanation; no workflow connecting MoSCoW → Admission; no "promote to Must" action that also sets Admission

---

## Scenario G — "I want to add a new Customer"

**CURRENT PATH:**
1. Migration Path → Customer Plans tab → **+ Register customer**
2. Modal: enter Customer ID (governed) + Customer name
3. Save → persisted with audit

**Data changed:** `customers` (create)
**Final result:** Customer appears in the Customer Plans list
**Missing:** No customer detail editing from the creation modal (only name + ID); all other fields edited via the Plan editor

---

## Scenario H — "I want to define that Customer's Required Capabilities and Key Features"

**CURRENT PATH:**
1. Migration Path → Customer Plans → Open Plan (customer)
2. **Required Capabilities:** edited via API (`POST /api/customers/{id}/capabilities/{cap_id}`) — ⚠️ **no UI button for this**
3. The plan shows required capabilities with availability derivation
4. **Key Features:** ❌ **NOT IMPLEMENTED** — no Customer↔Feature relationship
5. Blockers/dependencies: edited via **Edit plan** → text fields

**Data changed:** `customer_capabilities` + `customers`
**Final result:** Customer Plan shows required capabilities with availability
**Missing:** UI for required-capability editing; Customer↔Feature relationship; Key vs standard distinction

---

## Scenario I — "I want to build that Customer's Migration Plan across M1–M6"

**CURRENT PATH:**
1. Migration Path → Customer Plans → Open Plan
2. The plan shows: derived readiness + required capabilities + availability
3. **Earliest viable interval:** single field (e.g. `M3 -> M4`)
4. ⚠️ **No milestone-by-milestone customer plan exists**
5. The plan does NOT show "what is required between M1 and M2" / "what is required between M2 and M3"
6. The plan does NOT show a customer-specific timeline
7. The plan derives availability from the Product Roadmap but does not build a customer-specific sequence

**Data changed:** None (read-only derived view + editable plan fields)
**Final result:** Customer plan with readiness + required capabilities
**Missing:** Milestone-by-milestone customer plan; customer-specific migration roadmap; Feature requirements per interval; timeline visualisation

---

## Scenario J — "I want to know which Customers depend on a particular Feature"

**CURRENT PATH:**
1. ⚠️ **NOT IMPLEMENTED** — no Customer↔Feature relationship exists
2. The PM can see which Capabilities a Feature composes (Roadmap → Features → constituent list)
3. The PM can see which Customers require which Capabilities (Customer Plans)
4. But there is no reverse lookup: Feature → Capabilities → Customers

**Missing:** Customer↔Feature relationship; Feature→Customer reverse lookup; Feature-level customer dependency analysis

---

## Scenario K — "I need to produce one of the November deliverables"

**CURRENT PATH:**
1. REPORTS / DELIVERABLES → find the report card (D1–D5)
2. Check section completeness (X/Y AVAILABLE)
3. Click **Preview Report** → publication HTML opens in a new tab
4. Review the content
5. Click **Print / Save as PDF** (in-page button)
6. Or click **Generate HTML** → records a versioned snapshot

**Data source:** canonical DB — the PM does not rewrite Product information
**If data is missing:** the affected section shows "Awaiting Product data" / "Product decision required" explicitly
**Final result:** versioned snapshot in `report_generations`

**Missing:** No DOCX; no multi-report bundling (except Pilot Set); no custom report builder; no delivery tracking; no approval workflow

---

## Scenario L — "I need to produce the D5a Pilot Set"

**CURRENT PATH:**
1. Ensure governed customer records exist for the pilot customers
2. REPORTS / DELIVERABLES → D5 card → Select Customer (dropdown, governed only)
3. Click **Generate Customer Migration Pilot Set**
4. The API packages the selected D5 reports into one deliverable
5. Preview/Print as for individual reports

**Blocked by:** governed customer records (D3) — DEPP/INVALSI/NSA/NCCER do not exist
**Missing:** No multi-select for pilot set; no pilot-set template; no delivery tracking

---

# SUMMARY: End-to-end traceability gaps

```
Source Evidence (426)
→ [✅] lineage to Source
→ [✅] reconciled_family_id → Candidate
→ [⚠️] no UI to browse/search/filter evidence
→ [⚠️] no UI promote button (API only)

Candidate (34)
→ [✅] enrichment with evidence citations
→ [✅] Product Review editable (modal)
→ [⚠️] no Ideation disposition editing (modal)
→ [✅] MoSCoW + Admission editable
→ [❌] no Feature assignment from modal

Feature
→ [❌] no Feature creation from UI
→ [✅] Feature editing (Roadmap tab)
→ [❌] no Customer↔Feature link
→ [⚠️] derived timing only

Customer
→ [✅] full plan editing
→ [✅] required capabilities (API)
→ [❌] Key Features not assignable
→ [❌] no milestone-by-milestone plan
→ [⚠️] readiness derived at capability level only

Reports
→ [✅] consume canonical data automatically
→ [⚠️] narrative sections need Product-written text (no storage)
→ [✅] versioned snapshots
```
