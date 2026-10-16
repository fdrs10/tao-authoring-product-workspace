# OVERNIGHT_READINESS_REPORT — Final QA & UAT Preparation

**Date:** 2026-10-16 (overnight run) · **Baseline:** tag `dev-candidate-v1.0` = commit `04f520845a8c0a12438fb3e5caed43ad116c462d` (frozen; pushed; QA commits land after it — tag not moved)

# VERDICT: READY WITH WARNINGS

**Reasons:** the full Product workflow (Sources → Ideation → Cross-analysis → Backlog → Admission → Roadmap → Migration) is functionally complete and verified end-to-end on governed data; 80/80 automated tests pass; both defects found overnight were fixed with regression tests. The warnings are known and bounded: Roadmap default view is empty until Product commits admissions (D-R3), milestone/customer governed datasets are pending (D2/D3), and the actual cloud deployment awaits the IT inputs listed in §8 (identical to PHASE_6_REPORT §9).

---

## 1. Repository / tag state

- `origin/main` = `04f5208` at freeze → tag `dev-candidate-v1.0` (annotated, pushed; tag object `cf42d4b`).
- Overnight work is committed **after** the tag (defect fixes, launcher, QA docs) — the accepted baseline is untouched.

## 2. Tests executed

| Suite | Result |
|---|---|
| Full automated suite (`pytest tests`) | **80/80** in one invocation (26 API · 38 UI E2E incl. §55 guard · 10 ESM gate · 6 Phase-6) |
| Canonical import validation (governed dev DB) | **26 PASS / 0 FAIL** |
| Empty-DB pipeline (`scripts/ops/pipeline_from_empty.sh`) | PASS (migrate → import → validate → boot → smoke, 135 caps) |
| Two new overnight regression tests (QA-1, QA-2 fixes) | PASS |

## 3. Functional areas verified (browser sweep on governed data, 1440×900, §55 guard live)

13 areas + CAP modal from 3 entry points — **all PASS**: Sources & Evidence (8 sources, tabs), source drill-down (metadata + extracted 83 + Jira pane 28), Ideation 01–05, V2 Position figure, Cross-analysis (135 rows + inline admission), Product Backlog (Must=33 / All=135 / category filter), Roadmap default empty state (D-R3), Roadmap All (199 bar placements, D-R1), band expansion, horizon 0–6m, Outcome, Quarter view (+chips), Migration Path (3 bands), Customers empty-state, universal CAP modal (budgets/jira sections present everywhere).
Scenario workflows A–E executed on an isolated scratch DB: **all PASS** — source→extracted→CAP (A); admission propagation cross→API→backlog→roadmap filter (B); Jira link → status/target-release visible → unlink → ticket survives (C); timing change → Migration derivation moves unlocked→in-flight (D); two-user stale edit → 409 version_conflict, bob's write stands, audit records actor+before/after (E).

## 4. Data-integrity results (governed dev DB)

135 capabilities · 224 source capabilities (SAME 179 / SUPPORTS-EVOLVES 36 / OVERLAP 9) · 8 sources · 28 Jira tickets + 32 links (4 unlinked = Epics/placeholders — correct) · 696 capability-market links · 6 markets with exact v38.6 palette · 5 strategic categories verbatim · MoSCoW 33/75/22/5 · Admission 133 NULL + 2 CANDIDATE (D-R3 context) · budgets 135 NULL / **0 zeros** · timing 135 rows (months 0–6, durations 1–6, 0 NULLs) · CAP-0135 absent (never a reconciliation target) · exactly the 5 `PRODUCT_SCOPE_REVIEW_REQUIRED` caps (CAP-0071/0126/0128/0131/0133) · decisions verbatim incl. `Develop` vs `DEVELOP / VALIDATE` (G5 honoured) · zero dangling references, zero duplicates. **No missing or contradictory data found beyond the known D2/D3 pending datasets.**

## 5. Visual regression

22 desktop screenshots in `docs/evidence/overnight/` (sources, drill-down, extracted, Jira pane, ideation 01–05, cross-analysis, backlog ×2, roadmap ×3, outcome, quarter, migration, customers, modals). Reviewed against v10/v35.6/v38.6 references: hierarchy, palette, month grid, milestone lines (labelled once per category), three-band migration layout — all consistent. **No overlapping text, broken layouts, invisible controls or horizontal overflow found** (scroll-width asserted ≤ +2px). One recorded enhancement: dense lanes overlap bars (QA-3, v10 drilldown mitigates).

## 6. Technical defects found → corrected

| ID | Defect | Fix | Test |
|---|---|---|---|
| QA-1 | Drill-down overlay covered the sticky nav — navigation trapped while a pane was open (pointer intercepted; hashchange could never fire) | overlay starts below the 41 px header + clears on real navigation | `test_source_pane_does_not_block_navigation` |
| QA-2 | Roadmap "Admission · All" omitted the param → API applied its COMMITTED default → empty roadmap | All sends explicit empty admission; UNSET stays distinct | `test_roadmap_admission_all_shows_all_states` |

Both reproduced first, fixed minimally, committed separately (`db60b85`), full suite re-run. No Product semantics touched. Remaining items are documented, not fixed: QA-3/4/5 (enhancements), D2/D3 (missing data), D-R1/D-M1 (🟡 Product confirmation pending).

## 7. Local application startup (ready for tomorrow)

```bash
cd /Users/felixdiaz/Projects/tao-authoring-product-workspace
./start-local.sh          # → http://127.0.0.1:8080
```

Checks Docker → starts PostgreSQL (compose, idempotent) → upgrades migrations **only if behind** (never re-imports/overwrites) → starts the app → prints the URL + DB status; failures print the last log lines. Verified: cold start (DB stopped), warm re-run (port busy → reports URL), app left running now.

**Exact URL: http://127.0.0.1:8080** (currently running; log `/tmp/tao-authoring-local.log`).

## 8. Cloud deployment blockers (IT checklist — no resources created, per contract)

- [ ] GCP **project ID** (DEV)
- [ ] **Region** (e.g. europe-west1)
- [ ] **Cloud SQL instance** decision (name/tier/private-IP vs Auth-Proxy)
- [ ] **IAM**: runtime SA + deployer SA; secret mechanism (Secret Manager + WIF vs key)
- [ ] **DB secret** `tao_app` password in GitHub Environment `gcp-dev` (+ Cloud SQL)
- [ ] **DEV ingress policy**: allow-unauthenticated vs IAP/IP-restriction
- [ ] (optional day-1) source-document **bucket name** + `google-cloud-storage` dependency approval

Automation is wired (`deploy.yml`, gated on CI + `gcp-dev` environment); it hard-fails with a pointer until these exist. Nothing was deployed.

## 9. UAT package

`docs/uat/PRODUCT_UAT_READINESS.md` · `PRODUCT_UAT_TEST_CASES.md` (35 cases, PM-readable, 4-category vocabulary) · `KNOWN_DEFECTS_REGISTER.md` (2 fixed, 3 enhancements, verified-OK list) · `PRODUCT_DECISIONS_PENDING.md` (D-R1/D-M1 provisional rules 🟡, D2/D3 ⚪, D5/ADM confirmations).

## 10. Commit list (overnight, after the tag)

- `db60b85` fix: two QA defects — trapped navigation + Roadmap 'All states' empty
- (this commit) start-local.sh + docs/uat/* + overnight evidence + this report
