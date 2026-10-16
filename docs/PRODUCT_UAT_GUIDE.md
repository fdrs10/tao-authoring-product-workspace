# Product UAT Guide — shared DEV environment

**Audience:** the Product team using the shared DEV deployment.
**Workflow under test:** Sources → Ideation → Cross-analysis → Backlog → Admission → Roadmap → Migration.
**Rule:** Product Truth lives in the API/PostgreSQL. Never keep canonical data outside the app; your `user_ref` is only a personal label on shared edits (audit + versioning protect everyone).

---

## 0. Getting started

1. Open the DEV URL (from IT/Deployment Runbook §4). You land on **IDEATION**.
2. Set your identity once: click the **`dev-user` chip** (top right) and enter your name (e.g. `jane.doe`) — every edit is audited under this label.
3. Navigation: **IDEATION · ROADMAP · MIGRATION PATH · SOURCES & EVIDENCE** (+ **Product Backlog** from the ideation index).

## 1. Sources & Evidence

- **SOURCES & EVIDENCE → Sources**: all governed sources with human names; **Open Source** = drill-down with extracted capabilities → canonical mapping; **View Extracted** = the full mapping table.
- **SRC-JIRA-001** behaves as a source (Operational / Delivery Evidence): its rows are current Jira backlog items with live status.
- **Customers tab**: intentionally empty — the governed customer dataset has not been supplied; nothing is invented (D3).

## 2. Ideation (six working areas)

Index **01–06**: 01 V2 Position (with the frozen V2 equation reference) · 02 V1 carry-forward · 03 3.x direct migration · 04 New needs & gaps · 05 Discontinued · 06 Cross-analysis.

## 3. Cross-analysis + Product Backlog

- **06 Cross-analysis**: the canonical 135-capability universe with markets, MoSCoW, decision, V2 mapping.
- **Product Backlog** (from the index): default view = **Must**; set *MoSCoW · All* for the full universe; filter by category/market/admission/visibility/source.
- **Roadmap Admission** is editable inline in Cross-analysis, in Backlog, and in the CAP editor — **one and the same field**. Change it directly (D2 decision this phase: no approval workflow); audit + versioning record who changed what.
- Every **CAP-ID** opens the same universal drawer: sources, MoSCoW, admission, Jira links (add/remove — unlinking never deletes a Jira ticket), budgets (**NULL = "not estimated", never 0**), description, notes.

## 4. Roadmap

- **Full** view: Strategic Category → Big Rock/Market → capability bars on the 27-month window (Oct 2026 → Dec 2028).
- **Drag** a bar to move; **grab its left/right edge** to resize; timing snaps to whole months and saves through the API (a green status line confirms; a conflict warning means someone else saved first — your change was **not** applied; reload and redo).
- **0–6m / 7–24m / Tail** = report views over the same data (edit only in Full).
- **Outcome**: Product narrative per horizon (0–6 months / 7–24 months / Tail) — versioned, server-saved.
- **+ Milestone**: add governed milestones with a real ID (e.g. `M1`) — names/dates come from Product only; the app never invents them (D2).
- **Milestone lines** are red and labelled once per category; drag to reposition; click to edit.
- Filters (admission/market/MoSCoW/visibility) never reset your expansion state or timing. Default population = **COMMITTED**; switch *Admission · All* to see everything (**UNSET stays distinct from BACKLOG**).

## 5. Migration Path

- Three bands: **VALUE / ROADMAP CAPABILITIES UNLOCKED** → **MIGRATION PATH / MILESTONES** → **CUSTOMER TRANSITION PROJECTS**.
- Capability availability is **derived from Roadmap timing** — move work on the Roadmap and Migration follows; Migration owns no timing (do not duplicate capabilities here).
- Customer transitions are expressed as **milestone intervals** (`M1 -> M2`) — never TS codes. Customers stay empty until the governed dataset arrives (D3).
- Required capabilities ≠ readiness: blockers (data, training, governance, …) live in the customer record.

## 6. UAT checklist (compact)

| # | Check | Where | Expect |
|---|---|---|---|
| 1 | Sources list + drill-down | Sources & Evidence | Human names, SRC-JIRA-001 rows live |
| 2 | Ideation sheets render | Ideation 01–05 | Verbatim source-truth data; V2 Position intact |
| 3 | Backlog default = Must; All reachable | Backlog | Counts match the universe (135) |
| 4 | Edit Admission from Cross-analysis | 06 | Badge updates; API version bumps |
| 5 | Same Admission from Backlog | Backlog | Same field, same value |
| 6 | CAP drawer: NULL budget | any CAP-ID | "not estimated" — never "0" |
| 7 | Jira add/remove | CAP drawer | Link added/removed; ticket itself survives (Jira keeps it) |
| 8 | Drag a roadmap bar | Roadmap Full | Green "Saved CAP-xxxx … (vN)"; reload keeps position |
| 9 | Resize via edges | Roadmap Full | Month-precise, persisted |
| 10 | Two people edit timing | Roadmap | Second saver sees conflict warning; first write wins; no silent overwrite |
| 11 | Horizons | 0–6m/7–24m/Tail | Same bars clipped to window; no separate timing |
| 12 | Outcome narrative | Roadmap → Outcome | Saves, survives reload, version bumps |
| 13 | Quarter report | click a quarter header | Report-style month grid, click-through to CAP |
| 14 | Milestone create + drag | Roadmap / Migration | Red line moves; appears in BOTH views |
| 15 | Migration derivation | Migration | Unlocked/in-flight chips follow Roadmap timing changes |
| 16 | Customer interval | Migration | `M1 -> M2` format; blockers column; no TS codes |
| 17 | Empty-state honesty | Migration (no data) | Explicit "not supplied — never invented" notices (D2/D3) |
| 18 | Filters don't reset context | Backlog/Roadmap | Expansion, timing, outcomes unchanged |

Log findings with: page, CAP-ID/step, your `user_ref`, expected vs actual, screenshot.

## 7. Known honest limitations on DEV

- **Milestones/customers**: governed datasets pending (D2/D3) — functionality is live, data is not supplied.
- **Identity**: temporary `user_ref` convention until IdP integration (documented swap point in `app/identity.py`).
- Roadmap bars appear only for capabilities **with timing** (135 seeded timings exist; admission decides visibility).


## November Outcomes & Customer Migration Plans (structural update)

- **NOVEMBER OUTCOMES** (nav): orientation over the five outcomes — Authoring Product Definition (Ideation & Target Scope), Product Backlog, Product Roadmap, Common Migration Path, Customer Migration Plans — with links, dependencies and required Product input.
- **Migration Path | Customer Plans** switch inside MIGRATION PATH: the common path (M1–M6, shared) stays on the first tab; per-customer plans live on the second.
- Customer Migration Plans: register a customer (Product-supplied ID/name), link required CAP-xxxx, propose an interval (M3 -> M4 — TS codes refused), record blockers/assumptions/exceptions/window/validation. Readiness is derived from Roadmap truth: READY FOR PROPOSED INTERVAL / BLOCKED BY ROADMAP CAPABILITY (blocking CAPs listed) / CUSTOMER VALIDATION REQUIRED / PRODUCT DECISION REQUIRED / MIGRATION EXCEPTION. Plan edits persist with actor + version; stale edits 409.
- No invented customers, dates or requirements — the honest empty state remains until Product supplies governed data.
