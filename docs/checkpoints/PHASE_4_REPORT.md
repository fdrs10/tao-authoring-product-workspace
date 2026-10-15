# Phase 4 Checkpoint — Frontend Foundation

**Date:** 2026-10-15 · **Status:** COMPLETE · **Tests:** 37/37 (17 API + 20 UI E2E), single combined pytest invocation

## 1. What was built

### Backend additions (small, read-only)
| Endpoint | Purpose |
|---|---|
| `GET /api/markets` | 6 governed markets with v38.6 palette (`#4388bd #8061b5 #2f99aa #669b3c #d77619 #c95c5c`) for market dots/legends (§12/§26) |
| capability list | `jira` array embedded (delivery evidence per §14/§30) |

`app/main.py` now serves the SPA: `StaticFiles` at `/static` + catch-all fallback to `index.html`. **Route order matters and is now explicit:** routers → `/health` → `/health/db` → static mount → catch-all. A regression where the catch-all swallowed `/health` (200 + HTML body) was caught by the Phase 3 API suite and fixed by registering static last.

### Frontend (`web/` — vanilla ES modules, no build step)
Served by FastAPI; API is the only source of canonical state (§19: nothing canonical in JS or localStorage — only the personal `X-User-Ref` preference).

| Module | Scope |
|---|---|
| `js/main.js` | hash router (`#/ideation/01`, `#/sources`, `#/roadmap`, `#/migration`, `#/backlog`), nav, `open-cap`/`cap:changed` wiring |
| `js/api.js` | fetch client, `X-User-Ref` identity (default `dev-user`, §53.10), 409 error objects with `detail.current_version` |
| `js/ui.js` | badges (MoSCoW, admission incl. `NOT PLANNED`, REVIEW_REQUIRED), market dots + colour legend, table/notice primitives |
| `js/components/capmodal.js` | **universal CAP drawer** (§7–§11): detail/edit, NULL budget renders `not estimated` (never 0), 409 conflict state with "Show latest version" recovery, Jira add/remove (unlink ≠ delete ticket), scope-review flag shown not resolved |
| `js/views/ideation.js` | 6-item vertical index (01–06, §27); sheet 01 = V2 Position/Product Definition with `assets/v2-position.png`; sheets 02–05 render source-truth tables; sheet 06 = cross-analysis |
| `js/views/crossAnalysis.js` | §13/§29 canonical universe, inline Roadmap-Admission select (same field as Backlog/editor; `UNSET` preserved) |
| `js/views/backlog.js` | §30 Target Authoring universe; default MoSCoW=MUST with "full universe" note; filters: category/market/admission/visibility/source; count note |
| `js/views/sources.js` | §5/§20: human source names, drill-down pane, extracted→canonical mapping, **SRC-JIRA-001 as a source (Operational / Delivery Evidence)**, Customers tab empty with D3 notice (no invented records) |
| `js/views/roadmap.js`, `migration.js` | **intentional Phase 5 placeholders** (need Roadmap & Migration reference recovery first) |

## 2. Test suite (`tests/ui/`, Playwright + chromium)
- Throwaway `tao_authoring_e2e` DB, deterministic seed, uvicorn on `:8099` with **explicit subprocess env** (conftest does not mutate `os.environ`; both suites run green in one invocation — 37/37).
- **§55 blank-screen guard:** any `pageerror` fails the owning test at teardown.
- 20 tests covering: shell/nav, ideation index, V2 position, sheet rows, sources list + SRC-JIRA-001 drill-down, modal from cross-analysis, edit/save, NULL-budget≠0, zero-budget, scope-review mark, Jira add/remove (ticket preserved), admission edit from cross-analysis **and** backlog (same canonical field), backlog MUST default + filters, 409 conflict + recover, market legend colours.

## 3. Defects found & fixed during bring-up (root causes, not symptoms)
1. **`missing ) after argument list`** — `crossAnalysis.js` closed the table builder with `})}` instead of `}))` (brace where a paren belonged). Node 24 accepted it; Chromium rejected it. Localised by bisecting dynamic imports in-browser.
2. **`capLink is not defined`** — missing import in `capmodal.js` (drawer lineage rows).
3. **Selects invisible to save()** — `sel()` put the field name in `data-name` while save queried `[name=…]`; now real `name` attributes.
4. **Filter-reset race** — inline admission edits and Jira add/remove dispatched a global `cap:changed` that re-ran the whole route (reset user filters, raced modal DOM). Removed from inline paths; modal re-fetches its own fresh data.
5. **Conftest env bleed** — `tests/ui/conftest.py` set `DATABASE_URL` at module import; combined runs retargeted the in-process API TestClient to the e2e DB (409/renamed-row failures). Fixed by passing env explicitly to the uvicorn subprocess only.

Test-side corrections (selectors, not product): `[data-src]`/`[data-key]` attribute names, row-scoped cap links, `adm-badge` testid for unambiguous badge assertions.

## 4. Semantic invariants honoured (verified by tests)
- NULL Roadmap Admission ≠ BACKLOG — select shows `UNSET`; editing another field never touches it (`test_patch_null_semantics_preserved`, UI badge `UNSET`).
- NULL budget ≠ 0 — drawer shows `not estimated`; total derivation A+E with NULL→0 (D-item from Phase 3 stands).
- Jira ≠ Capability — add/remove links only; `test_add_and_remove_jira_link` asserts the ticket survives unlink (`GET /api/jira/PCR-TEST-1` → 200).
- No G5 label normalisation — market names and badges render verbatim (`MEXCBT / Uchida`, `NOT PLANNED`, `Develop` untouched).
- CAP-0135 never appears; no capability creation endpoint (governance deferred by design).
- 5 `PRODUCT_SCOPE_REVIEW_REQUIRED` caps show the mark, never auto-resolve.

## 5. Known gaps / deferred
- Roadmap (§31+) and Migration (§33+) views are placeholders — their reference implementations must be recovered (v35.6 zip / Roadmap HTML) before UI work, per the no-redesign rule.
- Capability **create** endpoint deliberately absent (ID governance); drawer edit-only.
- Multi-user identity remains the replaceable `X-User-Ref` abstraction (D5); no auth yet.
- `moscowBadge as MB` duplicate import in `crossAnalysis.js` is unused — harmless, cleanup candidate.

## 6. Commits
- `6a9b189` api: markets endpoint + jira array on capability list
- `f2d4285` web: Phase 4 SPA shell — API-authoritative frontend
- `f94e064` test: Playwright E2E suite — 20/20 pass

## 7. Recommendation for Phase 5
Recover **Roadmap** (from `legacy/TAO_Studio_Authoring_Action_Plan_Roadmap_v10.html`) and **Migration** (v35.6 zip) references, then implement `#/roadmap` and `#/migration` against the existing nullable `roadmap_admission` / milestone-empty schema — no schema redesign expected. The API surface (capabilities PATCH with version concurrency, audit events) already supports everything the Roadmap view needs.
