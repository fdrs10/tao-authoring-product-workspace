# PRODUCT_UAT_TEST_CASES — DEV candidate v1.0

Written for Product Managers. Every case states: **steps → expected result**.
Severity vocabulary: **Technical defect** = does not work · **Product decision** = works but needs Product validation · **Missing data** = not yet supplied · **Enhancement** = future improvement, not a blocker.

Legend: 🔵 Technical defect · 🟡 Product decision · ⚪ Missing data · 🟢 Enhancement

---

## T1 · Sources & Evidence
1. Open **SOURCES & EVIDENCE**. → 8 sources with human names (e.g. "TAO Studio - feature list", "Current Authoring Jira Backlog").
2. Click **Open Source** on `SRC-3X-001`. → Pane shows document metadata (type, owner, input form, status, upstream).
3. Click **View Extracted** on `SRC-3X-001`. → 83 extracted capabilities with original names/descriptions and a **Canonical CAP** link column.
4. In that table, click a **Canonical CAP** ID. → The universal CAP drawer opens with full capability info.
5. Click **Open Source** on `SRC-JIRA-001`. → 28 Jira tickets (delivery evidence) with status + linked-CAP counts.
6. Open the **Customers** tab. → Empty-state notice: governed dataset pending (⚪ D3).

## T2 · Ideation sheets
7. Visit **01 → 05** from the ideation index. → V2 Position (with the frozen reference figure), V1 carry-forward, 3.x migration, new needs, discontinued — each renders source-truth tables verbatim.
8. On 01, confirm the V2 equation figure renders (not a broken image).

## T3 · Cross-analysis + Admission (🟡 Product decision: direct admission editing is the approved model this phase)
9. Open **06 Cross-analysis**. → 135 rows; each row has markets, MoSCoW, decision, and an **Admission** dropdown.
10. Change a row's Admission to **CANDIDATE**. → Badge updates immediately; version bumps (audit records you).
11. Open **Product Backlog**, find the same CAP (set MoSCoW · All). → Same Admission value — one field, three views.

## T4 · Product Backlog
12. Default view → **Must** rows only (33 on governed data). Set *MoSCoW · All* → 135.
13. Filter by category / market / visibility / admission — every filter narrows without errors and never loses your place.

## T5 · Universal CAP modal (from every entry point)
14. Open a CAP from: Backlog row, Cross-analysis row, Roadmap bar, Source extracted table. → Same drawer everywhere.
15. In the drawer verify: description, MoSCoW, Admission, markets, Jira section, **budgets — NULL shows "not estimated", never "0"**.
16. **Edit** the CAP (e.g. notes), **Save**. → "Saved." + version bump.
17. Two people edit the same CAP: the second saver must see **"edit conflict … Show latest version"** — nothing is silently overwritten. (🔵 verified technically; confirm UX is acceptable — 🟡)

## T6 · Jira relationships (🔵 verified: unlink never deletes a ticket)
18. In a CAP drawer → Edit → **add a Jira key** → the link appears in the list. → Save → detail shows the ticket + status + target release.
19. Remove the link → drawer shows "No Jira links". Verify in Jira itself: the ticket still exists (only the link was removed).

## T7 · Roadmap
20. Open **ROADMAP**. Default = **COMMITTED** population → currently empty with an explanatory notice (🟡 D-R3: Product should commit admissions during UAT).
21. Set *Roadmap admission · All*. → Bars for all timed capabilities across 5 categories; market bands per the provisional grouping (🟡 D-R1 confirmation pending).
22. **Drag** a bar → month-snapped move; green "Saved CAP-xxxx (vN)" status; reload keeps it.
23. **Resize** via the bar's left/right edges. → Duration/start change precisely by whole months.
24. Expand a category band (＋). → One row per capability with its own bar; multiple bands can stay open; filters never close them.
25. **0–6m / 7–24m / Tail** horizons → report views of the same bars, clipped to the window (no separate timing to maintain).
26. Click a **quarter header** (e.g. 2026-Q4). → Report-style month grid with active capabilities + milestones; clicking a chip opens the CAP drawer.
27. **Outcome** tab → three narrative blocks (0–6 months / 7–24 months / Tail). Type, Save, reload → persisted with version.
28. **+ Milestone** → create with a governed ID/name/date (never invented by the app). A red vertical line appears, labelled once per category; drag it to reposition (⚪ real milestone list pending, D2).

## T8 · Migration Path
29. Open **MIGRATION PATH**. → Three bands: VALUE / MIGRATION PATH / CUSTOMER TRANSITION.
30. With a committed, timed capability: its CAP chip appears under the correct milestone interval (**Unlocked** vs **In flight**) — 🟡 D-M1 rule confirmation pending.
31. Change that capability's Roadmap timing → after reload the chip moves between intervals (Migration owns no timing).
32. Edit a milestone in Migration → the change is visible in the Roadmap too (one shared dataset).

## T9 · Customers (⚪ D3)
33. Customer table is empty with the pending-data notice. When Product supplies the governed list, transitions are expressed as milestone intervals (`M1 -> M2`), never TS codes, with blockers beyond capability.

## T10 · Cross-cutting
34. **Export**: `GET /api/export` returns the complete Product Truth JSON (IT can fetch it; no UI scraping).
35. At every step: no unexplained blank screens, no stuck overlays — after closing a pane/drawer you can always navigate.

---

### Result logging
Record per case: PASS / FAIL(🔵) / DECISION-NEEDED(🟡) / DATA-MISSING(⚪) / ENHANCEMENT(🟢), plus screenshot + your `user_ref`. Feed 🔵/🟡 into `KNOWN_DEFECTS_REGISTER.md` / `PRODUCT_DECISIONS_PENDING.md`.
