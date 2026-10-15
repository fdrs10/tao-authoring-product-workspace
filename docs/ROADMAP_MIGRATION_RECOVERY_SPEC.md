# Roadmap + Migration — Recovery Spec (Phase 5 Gate Document)

**Status:** RECOVERED · **Date:** 2026-10-15
**Sources physically inspected this session:**
- `legacy/TAO_Studio_Authoring_Action_Plan_Roadmap_v10.html` (93 KB, 404 lines; JS fully read)
- `legacy/TAO_Authoring_v35_6_MIGRATION_DIAGRAM(1).zip` (md5 `e873d77d55dcbd9f7006f64149bcedad`, **unchanged**) → extracted to working dir only (`~/.kimchi/docs/v35_6_extract/`); visible-text sequence + JS data model read
- `legacy/TAO_Authoring_v38_6_GOLDEN_BASELINE_REPAIRED.html` — consulted **only** for later-added concepts (horizons, Outcome, admission filter), per contract
- v33 family: **absent from `/legacy`** (matrix item E) — v10 verified as the behaviour reference; v33 remains nice-to-have corroboration

---

## 1. Behaviour found in Roadmap v10

**Timeline model.** 27 month slots, Oct 2026 → Dec 2028 (`months[]`, index 0–26); 9 quarter headers `2026 Q4 … 2028 Q4` (`quarters[]`). Bar geometry: `left = start/27*100%`, `width = dur/27*100%`.

**Hierarchy (default Full view).** `Main Category` → `Big Rock` → features. Category cell shows name + "N big rocks · N features". Each big rock = one lane: label cell (colour-coded left border) + `track` (month grid 27 cells).

**Collapse/expand.** Independent per big rock: `expandedBigRocks` Set keyed `catId::bigRockId`; `+/−` button toggles; expanded lane renders a `drilldown` block beneath it — one row per feature (label + ✎ + compact bar on a 27-cell drill track) — plus "No features in this big rock yet." and a footer add-button. Multiple branches can be open at once (explicit user action only). Expansion state survives re-renders.

**Drag / resize / snap (proven interaction).** `attachDrag()` binds `pointerdown/pointermove/pointerup` with pointer capture on `.bar` elements; handles `.handle.left/.right` select mode:
- `delta = Math.round((clientX - sx) / (trackWidth/27))` → **month snapping** (integer months)
- move: `start = clamp(0, 27-dur, start+delta)`, `dur` unchanged
- left resize: `ns = clamp(start, start+dur-1, start+delta)`; `dur = start+dur-ns`
- right resize: `dur = clamp(1, 27-start, dur+delta)`
- on `pointerup`: if moved → persist + re-render (v10: localStorage — replaced by API here)
- click (without drag) opens the item editor; a `dragged` flag suppresses the click after a drag

**Milestones on tracks.** Red vertical line per applicable milestone at `((month+.5)/27*100)%`; `title` = name · month · notes; draggable horizontally (same snap math); **label rendered once per category** (only on the first big rock's track). Scope filter: `global` (all tracks) / `category` / `big rock`. Milestones overview tab lists whole-roadmap / per-category / per-big-rock rows with draggable markers.

**Horizon view.** Modal `openHorizon(startMonth, count, title)`: quarter + month column headers; one row per Category×Big Rock; bars **clipped** to the window (`visStart = max(start, w0)`, `visEnd = min(start+dur, w1)`); milestone chips inside window; click-through to item.

**Quarter view.** Modal `openQuarter(qi)`: `month-detail` grid — columns = 3 months of the quarter, rows = Category×Big Rock; per cell the features active that month (`start <= m < start+dur`) with commitment/decision meta; milestones of the quarter as buttons; click-through to item.

**Scope view.** `openScope(type, catId, bigRockId)`: category (or single big rock) complete timeline: quarter grid, all its bars, applicable milestones.

**Design rules tab.** 8 rule cards (6+18 horizon, value before feature, transition explicit, migration ≠ parity, …) — static content, recoverable as an info panel.

**Persistence (v10).** `localStorage` keys `taoRoadmapV9…` + expanded-state key; Export/Reset buttons. → **NOT copied** (see §5).

## 2. Behaviour found in Migration v35.6

**Layout (Slide 3, the approved model).** Three stacked bands:
1. **VALUE / CAPABILITIES UNLOCKED**
2. **MIGRATION PATH** — "3.x → transition states → Target Authoring"; TAO 3.x AUTHORING → TAO STUDIO AUTHORING; "DEPENDENCY DECREASES" / "CAPABILITY & VALUE INCREASE"
3. **CUSTOMERS READY TO MOVE** — "Customer transition projects"

**Milestones.** `MILESTONES = M1…M6` with date, title, state (TS1/TS2/TS3/Target), text — e.g. M1 'Target Authoring agreed' Dec 2026; M6 'TAO 3.x Authoring EOL' Dec 2028. **These are example content, not governed data** (contract §10).

**Milestone intervals.** `migrationIntervals = 7 × {values:[], customers:[]}` — one band per interval between consecutive milestones (plus lead-in and post-EOL). Each band holds manually authored "Value / capabilities unlocked" bullets and "Customers ready to move" names. "Edit migration interval" per milestone.

**Customer transition project form.** name; current use/situation; desired outcome; value opportunity; required common capabilities; **migration blockers**; earliest viable transition state (select: Not assessed / TS1 · Foundation / TS2 · Governed / TS3 · Scale / Target Authoring — **historical vocabulary**); validation status (Not assessed / Hypothesis / Customer validated / Migration committed); notes. Six fake customers A–F seeded.

**Persistence.** localStorage. → **NOT copied**.

## 3. Behaviour added later in v38.6 (consulted, not the render reference)

- Horizon band buttons: `Full | 0–6m | 7–24m | Tail` — views over the same data.
- **Roadmap | Outcome switch**; Outcome = three narrative blocks: "0–6 months", "7–24 months", "Tail / long term" (`state.outcomes` in localStorage there → **API persistence here**).
- Admission filter incl. UNSET handling; `.outcome-only` mutual exclusion of Roadmap/Outcome panels.
- Filter vocabulary note: v38.6 shows visibility values ('Migration-only', 'Internal / platform') that **do not exist in canonical data** — canonical governs (`Shared / common core`, `Shared / market-configured`, `Market-specific`).

## 4. Behaviour that MUST be recovered

| # | Behaviour | Source |
|---|---|---|
| R1 | Full Roadmap default view, desktop-width, 3-level hierarchy Category → Big Rock/Market → Capability, bar tracks (no cards) | v10 |
| R2 | Independent branch expand/collapse; multiple open; preserved across edits/filters | v10 |
| R3 | Drag move + left/right resize + month snapping; persisted timing via API with optimistic version (409 never silently overwrites) | v10 + contract §7 |
| R4 | Horizons Full / 0–6m / 7–24m / Tail as views over the same data (window-clipped rows) | v38.6 + v10 horizon modal |
| R5 | Roadmap \| Outcome switch; narratives for 0–6m / 7–24m / Tail; server-persisted, versioned, audited | v38.6 + contract §6 |
| R6 | Red vertical milestone lines, labelled once, shared dataset, editable via API (409-safe) | v10 + §10 |
| R7 | Quarter/timeframe report-style focused view (timeframe, cat, group, CAP-ID, capability, description, MoSCoW, visibility, Jira/status/release, timing, milestones) | v10 + §11 |
| R8 | CAP modal reuse from Roadmap (Sources, MoSCoW, Admission, Jira, budgets, timing, audit) | §8 |
| R9 | Market legend + governed colours wherever dots appear | §17 |
| R10 | Filters (Market, MoSCoW, Visibility, Admission) that never mutate Product Truth and never reset timing/expansion/outcomes | §16 |
| R11 | Migration vertical 3-band model (VALUE / MIGRATION PATH / CUSTOMER TRANSITION), two views aligned on ONE milestone dataset | v35.6 + §12 |
| R12 | Migration capability availability DERIVED from Roadmap timing + milestones (no duplicate timing) | §13 |
| R13 | Customer transition expressed as milestone interval (M3→M4); TS codes never canonical | §14 (API guard already enforces) |
| R14 | Migration blockers beyond capability availability (workflow, governance, data, metadata, integrations, training, contracts, procedures, adoption, organisational readiness) — modelled as free-text `blockers` + `validation_status`; availability ≠ readiness | v35.6 + §15 |
| R15 | Empty-state honesty: milestones/customers empty until governed data (no invented names/dates in production UI) | §10/§14/D3 |
| R16 | Design-rules content preserved as an info panel | v10 |

## 5. Behaviour that must NOT be copied (later regressions / non-canonical)

1. **localStorage persistence of roadmap/timing/milestones/customers/outcomes** (v10, v35.6, v38.6) — replaced by server persistence + version + actor + audit (§18).
2. **Invented baseline content as production data**: v10 `baseline` categories/big rocks/features; v35.6 M1–M6 milestone names/dates; fake customers A–F. Recovered **only as test fixtures** clearly marked reference fixtures.
3. **TS1/TS2/TS3 as canonical transition model** — v35.6's customer TS select is not restored; canonical = `earliest_milestone_interval` ("M3 -> M4"); the API already 422s TS codes.
4. **Commitment types** (Product bet ◇ / Customer ■ / Contractual ◆ / Transition ↔) and v10's Jira-level *ticket* bars with their own timing — no canonical fields; visual language replaced by canonical Admission/MoSCoW/Decision + market dots. Jira contributes evidence only (key/status/target release), never timing (§9).
5. **Random `uid()` IDs** — canonical CAP-ID/M-ID governance only.
6. **"+ Add Feature / + Big Rock / + Main category"** creation from the Roadmap — capability/milestone creation is governance-controlled; no create endpoint for capabilities (deliberate). Milestone POST exists for Product use; the UI form never prefills invented names/dates.
7. **Export/Reset buttons** — server data is authoritative; local reset has no meaning.

## 6. Mapping historical local data → canonical API entities

| Historical (v10/v35.6) | Canonical entity / field | Notes |
|---|---|---|
| Main Category | `capabilities.strategic_category` (5 governed values) | identity preserved verbatim (no G5-style normalisation) |
| Big Rock | **derived middle band** — see D-R1 | canonical has no big_rock column; contract names the level "Big Rock / Market" |
| Feature / item | CAP (`cap_id`, `working_name`) | CAP-ID immutable |
| item.start/dur (0–26) | `roadmap_timing.start_month/duration_months` (+`version`) | same 27-month window; PATCH `/api/roadmap/{cap_id}` |
| milestone {name, month, type, notes, scope} | `milestones` {name, position_month, milestone_date, description, scope_type, scope_ref, version} | shared dataset for Roadmap+Migration |
| M1–M6, customers A–F | **test fixtures only** (seeded in e2e DB, marked reference fixtures) | never imported into dev/prod canonical data |
| segment tag / market relevance | `capability_markets` → market dots + legend | Phase 4 components reused |
| v35.6 interval `values[]` | **derived** at render time from `roadmap_timing` vs interval window (+ admission) | no stored duplicate (§13) |
| v35.6 interval `customers[]` | derived from `customers.earliest_milestone_interval` | e.g. 'M3 -> M4' |
| v35.6 TS select | **dropped** (canonical refuses TS codes) | transition-state narrative lives in Outcome/milestone description text |
| v38.6 `state.outcomes` | **NEW** `roadmap_outcomes` table + `/api/outcomes` | Alembic `0002` |
| Jira (v10 ticket timing) | `jira_tickets.status/target_release` displayed; never drives timing | §9 |

## 7. Derived rules (deterministic, testable)

**D-R1 middle band rule** ("Big Rock / Market"). Within a strategic category, capabilities are grouped:
- `visibility = 'Shared / common core'` → single band **"Shared / common core (all markets)"** (appears once);
- otherwise → one band **per governed market** the capability maps to (market-specific: 1 market; market-configured: its configured markets — a capability may legitimately appear in several market bands; this is Product truth, not duplication).
Data basis: 4 caps market-specific (1 market each), 31 market-configured (⌀ 3.1), 100 common-core (6 markets each) — the rule keeps the default view desktop-width without 600 duplicated bars.

**D-R2 horizon windows.** Full = months 0–26; 0–6m = 0–5; 7–24m = 6–23; Tail = 24–26 (remainder; contract fixes the first two, v38.6 fixes the labels).

**D-R3 roadmap population.** Default admission filter = COMMITTED. Additional options: All (any state incl. UNSET), CANDIDATE, BACKLOG, DEFERRED, NOT PLANNED, UNSET — UNSET stays distinct from BACKLOG (API `admission=UNSET` → `IS NULL`).

**D-M1 migration derivation.** Intervals: lead-in `[0, M1)`, between consecutive milestones `[Mi, Mi+1)`, post-EOL `[M6, 27)`. For each interval:
- **Unlocked by the start of this interval**: COMMITTED capability with `start_month + duration_months ≤ interval_start`
- **In flight during this interval**: window overlaps the interval.
Changing Roadmap timing changes these lists on next load (no stored duplicate). Admission filter applies (default COMMITTED).

**D-R5 milestone scope mapping.** `scope_type='global'` → line on every track; `scope_type='category'` (scope_ref = category name) → lines within that category; label rendered once per category group (v10 behaviour).

## 8. Schema / API extensions

1. **Alembic `0002_roadmap_outcomes`** — table:
   `roadmap_outcomes(horizon text PK CHECK (horizon IN ('0-6m','7-24m','tail')), narrative text, version bigint NOT NULL DEFAULT 1, updated_at timestamptz DEFAULT now(), updated_by text)`.
2. **`app/routers/outcomes.py`** — `GET /api/outcomes` (3 rows, created on demand as NULL narratives), `PATCH /api/outcomes/{horizon}` (optimistic `version`, actor, audit). Registered in `main.py` before the static catch-all.
3. Existing endpoints reused unchanged: `/api/roadmap`, `PATCH /api/roadmap/{cap_id}` (409 version_conflict), `/api/milestones` GET/POST/PATCH, `/api/customers*`, `/api/markets`.

## 9. Genuine ambiguities requiring Product decision (non-blocking; defaults chosen)

| ID | Question | Default chosen for Phase 5 |
|---|---|---|
| D-R1 | Is the market-band rule the intended "Big Rock / Market" replacement? | Rule in §7-D-R1 |
| D-R2 | Tail window definition | months 24–26 |
| D-R3 | Roadmap default population is COMMITTED, but governed data currently has **0 COMMITTED** caps (133 NULL, 2 CANDIDATE) — default view will be empty until Product commits items. Ship empty-state + filter? | Yes; empty-state explains, filter switch is one click |
| D-R4 | Outcome narrative granularity | one versioned text block per horizon (v38.6 model) |
| D-M1 | Migration "unlocked" definition | completed-before-interval vs in-flight split (§7-D-M1) |
| D-M2 | Milestone scope semantics in canonical data | global/category only (scope_ref = category name); market-scope deferred until governed milestones exist |

None of these force invented behaviour; implementation proceeds with the defaults and they are listed for Phase 6 review.

---

**Gate satisfied.** Implementation follows: migration 0002 → outcomes router → `web/js/views/roadmap.js` → `web/js/views/migration.js` (reusing Phase 4 components) → tests (§19 matrix) → regression → checkpoint.
