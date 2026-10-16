# CUSTOMER_MIGRATION_UAT_GUIDE — Product walkthrough for the November outcomes

**Start:** `./start-local.sh` → http://127.0.0.1:8080 → **NOVEMBER OUTCOMES** in the main navigation.

---

## A. The five November outcomes (orientation page)

1. Open **NOVEMBER OUTCOMES**. → Five outcome cards with purpose, working-area link, main dependency, and what Product input is still required.
2. Click through each link. → Lands in the correct working area (Ideation, Backlog, Roadmap, Migration).
3. Note the flow strip: Sources → Source Capabilities → Ideation → Target Scope → Backlog → Roadmap → Migration Path → Customer Plans.

**Remember:** ONE Product Roadmap · ONE common Migration Path · MULTIPLE Customer Migration Plans.

## B. Authoring Product Definition — Ideation & Target Scope (Outcome 1)

- Ideation index 01–06: V2 Position (reference figure), V1 Carry-forward, 3.x Direct Migration, New Needs & Gaps, Discontinued → **06 Cross-analysis** (what does the final V2 capability become?).
- Use the filter layer (search, category, market, MoSCoW, visibility, product review, review flag, admission, decision, source) — **Clear filters** and **"Showing X of Y capabilities"** included; filtering never mutates data.
- Target Scope ≠ Roadmap commitment: Admission is the explicit gate.

## C. Product Backlog (Outcome 2)

- Open **Product Backlog** (default Must; *MoSCoW · All* for 135). Columns: CAP | Capability | Category | Markets | MoSCoW | **Admission (editable)** | Visibility | Source(s) (hover = identities).
- Open a CAP drawer: full traceability (sources, source capabilities, provenance, Product Review — editable), budgets (NULL = "not estimated"), Jira evidence.

## D. Product Roadmap (Outcome 3)

- **Capabilities** view: Strategic Category → Capability; **M1–M6 milestone lines** labelled once per category (drag to reposition; edit via click).
- Drag/resize capability bars (month snapping; persisted; 409 on conflict). Horizons 0–6m / 7–24m / Tail are report views. **Features** switch shows Product compositions with **derived** coverage.
- Market is a **filter + legend** — never lanes; each capability renders once at Market = All.

## E. Common Migration Path (Outcome 4)

- **MIGRATION PATH → Migration Path tab**: VALUE / ROADMAP CAPABILITIES UNLOCKED (derived from Roadmap timing) → M1–M6 milestones + intervals → customer transition summary.
- Editing a milestone here propagates to the Roadmap and every Customer Plan (one dataset).

## F. Customer Migration Plans (Outcome 5)

1. Switch to the **Customer Plans** tab. With no governed customers: honest empty state (D3) — plans cannot be invented.
2. **+ Register customer** with Product-supplied ID/name.
3. Link required canonical capabilities (API: `POST /api/customers/{id}/capabilities` with the CAP-ID).
4. **Open Migration Plan** → readiness (e.g. BLOCKED BY ROADMAP CAPABILITY with the blocking CAPs identified), context & need, dependencies (CAP links open the universal modal), shared M1–M6, migration fields (interval `M3 -> M4`, window, dependencies, blockers, assumptions, exceptions), validation.
5. **Edit plan** → fields persist with actor + version; concurrent edits return 409 (never silent overwrite).

**Readiness states (derived, explainable — no scores):** READY FOR PROPOSED INTERVAL · BLOCKED BY ROADMAP CAPABILITY · CUSTOMER VALIDATION REQUIRED · PRODUCT DECISION REQUIRED · MIGRATION EXCEPTION. Change Roadmap timing → readiness re-derives.

## G. UAT checklist

| # | Check | Expect |
|---|---|---|
| 1 | November Outcomes page | 5 outcomes, links work, no data entry |
| 2 | Ideation filters | Combine + Clear + "Showing X of Y"; data unchanged |
| 3 | Backlog columns | Visibility + Source(s) visible; Admission editable |
| 4 | Roadmap Market=All | Each CAP once; no market lanes |
| 5 | Roadmap K-12 filter | Only applicable CAPs |
| 6 | Milestone M1–M6 | Lines in Roadmap; same 6 in Migration; edit propagates |
| 7 | Customer Plans empty state | Honest D3 notice; no invented customers |
| 8 | Fixture customer plan | Context/need/dependencies/migration/validation sections render; CAP links open modal |
| 9 | Readiness derivation | BLOCKED/CUSTOMER VALIDATION/READY states follow Roadmap timing + validation |
| 10 | Stale plan edit | 409; second saver's text stands |

Known honest states: customers/milestones-beyond-M1–M6 are Product-supplied (D2/D3); identity remains `user_ref` until IdP; no Jira API integration.
