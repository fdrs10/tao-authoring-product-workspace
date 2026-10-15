# KINCHI MASTER HANDOFF — TAO Studio Authoring Product Workspace

**Handoff date:** 2026-10-15  
**Functional reference:** `legacy/TAO_Authoring_v38_6_GOLDEN_BASELINE_REPAIRED.html`  
**Clean canonical ancestor:** `legacy/TAO_Authoring_v37_0_CANONICAL_DATA_WORKSPACE.html`  
**Target:** multi-user web application, repository-first, 100% deployable on Google Cloud Run + Cloud SQL PostgreSQL.

## 0. Non-negotiable mission
Do **not** redesign the approved Product model. Do **not** rebuild the Roadmap from scratch. Do **not** treat Jira tickets as capabilities. Do **not** broaden scope beyond the **Authoring function**.

Reimplement the approved behaviour cleanly, fix the known defects, preserve canonical data/lineage, and move persistence from embedded/local browser state to PostgreSQL.

## 1. Product data is the first priority
The repository contains the actual governed working data. Before UI work, import and verify:

- `135` canonical capability records in `data/canonical/capabilities.json`.
- `28` Jira backlog records in `data/canonical/jira_tickets.json`.
- Source register in `data/canonical/sources.json`.
- Full source-level and cross-analysis tables in `data/source_extracts/`.
- The two Excel workbooks under `data/raw/` are audit/reference artifacts and must not be silently rewritten.

Current canonical category distribution: {'Standards & Portability': 50, 'Create & Design': 23, 'Manage & Govern': 25, 'AI-assisted Authoring': 19, 'Collaborate & Assure Quality': 18}.  
Current MoSCoW distribution: {'Must': 33, 'Should': 75, 'Could': 22, "Won't": 5}.  
Current Admission distribution in the HTML snapshot: {'UNSET': 133, 'Candidate': 2}.

### Identity model
`Source document -> Source capability ID -> canonical CAP-ID -> Ideation treatment -> Cross-analysis -> Product Backlog -> Roadmap Admission -> Roadmap timing -> Migration Path -> Customer transition`

Source-local IDs are lineage only. **Canonical CAP-ID is the single downstream identity.** Never create independent Roadmap or Migration copies.

## 2. Authoring-only scope gate
Only register capabilities that belong to, enable, govern, or materially support **Authoring**. Examples in scope: item/test authoring, assembly, content banking, authoring metadata/taxonomy, authoring workflow/review/QA, authoring permissions, authoring interoperability, AI-assisted authoring, blueprinting/templates, authoring-related psychometrics.

Out of scope as capabilities unless a direct Authoring dependency is explicitly modeled: proctoring, candidate/session management, delivery operations, learner administration, payments/commerce, generic platform administration, commercial onboarding.

## 3. Strategic categories — fixed unless Product explicitly changes them
1. Create & Design
2. Manage & Govern
3. Collaborate & Assure Quality
4. Standards & Portability
5. AI-assisted Authoring

Markets — preserve stable identity/colors everywhere market dots appear:
- Traditional / K-12
- Professional / Credentialing
- Higher Education
- Governed Formative
- Assessment-led Learning
- MEXCBT / Uchida

Every view that shows market dots must show the compact market legend.

## 4. Source ingestion contract
One source = one source record + one physical/raw document where available + one source-capability extraction.

For structured source tables, preserve original capability name and original description literally. For narrative sources, extracted names/descriptions may be authored, but the supporting evidence/reference must be preserved.

Source UI must provide:
- `SRC-ID · human document name`
- owner/type/date/version
- `View/Open source`
- `View extracted capabilities`
- source-local capability ID -> canonical CAP-ID mapping

Do not fake an original document when only pasted text/extraction is available. Label a materialized record accurately.

## 5. Canonical capability contract
Each canonical capability must support at least:
- CAP-ID immutable
- working name
- functional description (clear, specific, not a Jira umbrella)
- Strategic Category
- markets (0..n)
- MoSCoW
- Visibility
- scope
- origin
- owner
- decision/classification
- V2 mapping
- sources/evidence (many-to-many)
- Roadmap Admission
- Jira links (many-to-many)
- Jira status/target release surfaced from linked tickets
- Analysis budget hours
- Execution budget hours
- Total budget hours = Analysis + Execution
- notes
- roadmap timing where admitted/planned

A capability may be high-level, but it must still describe one coherent ability. Names such as “improvements”, “facelift”, “feedback”, or broad Jira containers do not automatically become capabilities.

## 6. Jira is evidence/delivery tracking, not capability truth
A Jira ticket may map to zero, one, or many CAPs. A CAP may map to zero, one, or many Jira tickets.

Known strict reconciliation decisions:
- PCR-117 -> EVIDENCE_ONLY
- PCR-139 -> NEEDS_DECOMPOSITION
- PCR-201 -> NON_CAPABILITY
- PCR-215 -> NEEDS_DECOMPOSITION
- CAP-0135 was retired because “Professional authoring UX/UI improvements” was too ambiguous. **Never reuse CAP-0135.**

Preserve Jira key, URL/deep link, Summary, Description, Status, Target Release, Lifecycle, Due Date, Assignee, estimates where available.

## 7. Ideation model
Main navigation remains conceptually:
`IDEATION | ROADMAP | MIGRATION PATH | SOURCES & EVIDENCE`

Ideation contains:
1. V2 Position / Product Definition
2. V1 TAO Studio Carry-forward
3. 3.x Direct Migration to V2
4. New Needs & Gaps / Developments
5. Discontinued
6. Cross-analysis

V2 equation:
`V1 Carry-forward + 3.x Direct Migration + New Needs/Gaps - Discontinued = V2 Authoring Target Scope -> Cross-analysis -> Final canonical capabilities`

Cross-analysis is **not** a summand.

### Product Backlog
Cross-analysis must expose a sibling/secondary view: **Product Backlog**. It is the complete canonical Target Product capability universe, before mandatory timeline placement.

### Roadmap Admission
Every canonical CAP has one of:
- Committed
- Candidate
- Backlog
- Deferred
- Not planned

MoSCoW and Admission are independent. A MUST is not automatically committed. Default policy may propose MUST as Candidate.

Admission must be editable from **Cross-analysis and Product Backlog**, and the same value must be reflected everywhere.

## 8. Roadmap — recover, do not redesign
Use the historical Roadmap code as behavioural reference, especially:
- `legacy/TAO_Studio_Authoring_Action_Plan_Roadmap_v10.html`
- historical v33/v35 references if supplied later.

Required hierarchy: `Strategic Category -> Big Rock -> Feature`.
Required behaviours:
- independent category expansion
- independent Big Rock expansion
- multiple branches open simultaneously
- depth modes Categories / Outcome / Big Rocks / Features
- horizons Full / 0–6m / 7–24m / Tail
- drag feature bars
- left/right resize
- month snap
- persistence through backend
- milestones as vertical red lines, label once in header
- professional quarter/focused-timeframe report
- filters supplementary, never replacement for hierarchy
- default full view must fit without unnecessary horizontal scrolling

Roadmap consumes canonical CAPs. Default active planning view should use `Admission = Committed`, with filter to inspect others.

## 9. Migration Path
Preserve vertical model: left `VALUE / CAPABILITIES UNLOCKED`, centre `MIGRATION PATH`, right `CUSTOMER TRANSITION PROJECTS`.

Same milestone entities as Roadmap. No second milestone list.
Capabilities unlocked derive from Roadmap timing; do not maintain independent timing.
Customer transition uses real milestone intervals (`M2 -> M3`, etc.), not abstract TS1/TS2/TS3.

Customer records require at minimum: name, current use, minimum functionality used today, minimum expected in Studio, desired outcome, value opportunity, required CAP-IDs, blockers, earliest viable milestone interval, validation status, notes.

## 10. Universal capability modal
Wherever a CAP-ID appears, it must be clickable and open the **same canonical capability detail modal**. Modal must show full metadata, markets + legend, sources with document names, source lineage, Jira tickets/status/releases, Admission, budgets, roadmap timing, notes.

Edit Capability must actually support adding/removing Jira links. This is a known defect in the legacy HTML and must be fixed, not copied.

## 11. Known defects in v38.6 — acceptance blockers
See `docs/KNOWN_DEFECTS.md`. Important examples:
- Add Jira Link button does not reliably add editable rows.
- Jira Current Backlog source cannot reliably be opened/drilled into as specified.
- Source document/extraction navigation is incomplete.
- Roadmap Admission must be editable in Cross-analysis as well as Product Backlog.
- Full regression of filters/modals/navigation is required.

## 12. Cloud target
Target architecture:
`Browser -> Cloud Run web/API -> Cloud SQL PostgreSQL`

Requirements:
- shared state, no localStorage as product truth
- authenticated users
- autosave
- optimistic concurrency/version field
- audit history: who/what/when/before/after
- database migrations
- health/readiness endpoints
- Cloud SQL socket support
- secrets via Secret Manager/env, never committed
- stateless Cloud Run containers
- source documents in durable object storage or approved document URLs; database stores metadata/links, not giant PDFs unless explicitly chosen

## 13. Repository rule
The repository is the system-of-change. All code, schema, migrations, tests, documentation, seed/import scripts and non-confidential source artifacts belong here. Do not commit credentials.

Start by importing the frozen baseline data and making regression tests pass before visual polishing.
