# FINAL MORNING PRODUCT HANDOFF

**Date:** 2026-10-16 · **HEAD:** `91e79e7` · **Regression:** 160/160 · **Tag:** `dev-candidate-v1.0` (frozen)

---

## 1. WHERE DO I START?

```bash
cd /Users/felixdiaz/Projects/tao-authoring-product-workspace
./start-local.sh
```

Open **http://127.0.0.1:8080** → the app lands on **HOME**.

Verify you are on the right version: click **HOME** and check the governed counts line shows **34 Active Candidates · 426 Evidence Signals · 9 Sources**.

---

## 2. WHAT SHOULD I DO FIRST?

**Human Product Review of the 34 Candidates.**

1. Click **CAPABILITIES** in the nav (lands on Ideation 00).
2. You will see 34 rows (the active Candidate population).
3. For each Candidate, click the **CAP-ID** link (e.g. `CAND-F01`) to open the universal editor.
4. Review the enrichment, then click **Edit** to make decisions.
5. Work through all 34 before moving to any other activity.

Use the **Focus** filter (15 Candidates) to prioritise your first pass.

---

## 3. FOR EACH CANDIDATE — REVIEW IN THIS ORDER

| Order | Decision | Where in the modal | What to consider |
|---|---|---|---|
| 1 | **Functional definition** | OVERVIEW → Full description | Is the consolidated definition accurate? Rewrite if needed. |
| 2 | **Strategic Category** | OVERVIEW → Strategic Category | Assign one of the 5 governed categories (currently "Awaiting Product data"). |
| 3 | **Markets** | OVERVIEW → Market checkboxes | Confirm which markets this Candidate applies to. |
| 4 | **Product Review** | PRODUCT DECISION → Product Review | Set to CONFIRMED, CONFIRMED_WITH_CHANGES, REJECTED, or REVIEW_REQUIRED. |
| 5 | **Decision rationale** | PRODUCT DECISION → Decision rationale | Write why you made this review decision. |
| 6 | **MoSCoW** (optional) | PRODUCT DECISION → MoSCoW | Only if you are ready to prioritise. Leave unset if not. |
| 7 | **Roadmap Admission** (optional) | PRODUCT DECISION → Roadmap Admission | Only if you are ready to admit to the Roadmap. Leave unset if not. |
| 8 | **Ideation disposition** | API only (not yet in modal) | ACTIVE FOR IDEATION or NOT SELECTED. |

After each edit: click **Save** → version bumps → audit records your change.

---

## 4. WHAT SHOULD I NOT DECIDE YET?

| Decision | Why wait |
|---|---|
| **Feature composition** | Features are Product-created compositions — compose them after Candidate review is complete. |
| **MoSCoW on all 34** | Only set MoSCoW on Candidates you have confirmed. Unreviewed Candidates should not carry priority. |
| **Roadmap Admission** | Only set Admission on confirmed Candidates. Admission drives the Roadmap — do not commit unreviewed work. |
| **Roadmap timing** | Timing follows Admission. Do not set timing on unadmitted Candidates. |
| **Customer requirements** | Governed customer dataset (D3) is still pending. Do not invent customers or their requirements. |
| **CAND→CAP renaming** | The CAND-Fxx → CAP-xxxx identity policy is an explicit Product/system design decision. Do not rename unilaterally. |

---

## 5. WHAT HAPPENS AFTER I CONFIRM A CANDIDATE?

**Current system behaviour (verified):**

1. `product_review_status` changes to `CONFIRMED` (or `CONFIRMED_WITH_CHANGES` / `REJECTED`)
2. `version` increments (optimistic concurrency)
3. `audit_events` records: actor, before (NULL), after ('CONFIRMED'), timestamp
4. **The row remains `CAND-Fxx`** — the CAP-ID does NOT change
5. **The row remains in `population='SOURCE_ANALYSIS_CANDIDATE'`** — no automatic transition
6. **It does NOT get MoSCoW or Roadmap Admission automatically** — those remain separate Product decisions
7. **It appears in the Backlog** (it was already there — the Backlog shows the active population)
8. **It appears in Reports D1/D2** (the reports consume the active population)

**Unresolved CAND→CAP identity policy:** the application does NOT rename CAND-Fxx to CAP-xxxx on confirmation. This is a deliberate design gap — the final identity policy requires a Product decision. The candidate's lineage (CAND-F01, source evidence, enrichment) is preserved regardless.

---

## 6. HOW DO MULTIPLE PMs WORK TOGETHER?

| Mechanism | How it works |
|---|---|
| **Owner** | Each Candidate has an `owner` field (editable in the modal). Set it to your name. |
| **Rationale** | Every material decision (Product Review, MoSCoW, Admission, promotion) records your rationale in the audit trail. |
| **Comments** | Each Candidate has a DISCUSSION section in the modal. Add comments; other PMs see them. Resolve when addressed. |
| **Request Review** | Click "Request Review" to flag a Candidate for another PM's attention. The flag is visible in audit. |
| **Optimistic concurrency** | If two PMs edit the same Candidate, the second save gets a 409 with the current version. Reopen and reapply. |
| **History** | Home → RECENT CHANGES shows the latest audit events across all entities. |

**Set your identity:** click the **dev-user** chip (top right) → enter your name → all your edits are audited under that name.

---

## 7. HOW DO I KNOW WHEN THE 34-CANDIDATE REVIEW IS FINISHED?

Measurable completion criteria:

1. **All 34 Candidates have `product_review_status` set** (not NULL, not empty)
   - Check: Ideation 00 → filter Product Review → "Not reviewed" → count should be 0
2. **All 34 have a Strategic Category assigned** (not "Awaiting Product data")
   - Check: Ideation 00 → filter Strategic Category → each category shows its candidates
3. **All 34 have a Decision Rationale recorded**
   - Check: open each Candidate modal → Decision rationale field is populated
4. **No Candidates with unresolved DISCUSSION comments**
   - Check: open each Candidate modal → DISCUSSION section → all comments resolved

The Home page **NEEDS YOUR ATTENTION** section shows the count of Candidates awaiting review. When it drops to 0, the review is complete.

---

## 8. WHAT HAPPENS NEXT?

The exact Product sequence from completed Candidate Review:

```
1. Candidate Review COMPLETE (all 34 have Product Review + rationale)
2. → Feature Composition (compose confirmed Candidates into Features)
3. → Roadmap Admission (set Admission on confirmed Candidates)
4. → Roadmap Timing (set timing on admitted Candidates)
5. → D2 — Product Backlog becomes deliverable (all fields populated)
6. → D3 — Product Roadmap becomes deliverable (admitted + timed)
7. → D1 — Authoring Product Definition becomes deliverable (Target Scope decided)
8. → Customer dataset (D3: governed customer records)
9. → Customer Migration Plans per Customer (D5)
10. → D5a Pilot Set (DEPP / INVALSI / NSA / NCCER when governed data exists)
```

**Steps 2–5 are in the application.** Steps 8–10 require Product to supply the governed customer dataset (D3).

---

## 9. DELIVERABLE STATUS TODAY

| Report | Sections | Status | What Product work is blocking it |
|---|---|---|---|
| **D1** — Authoring Product Definition | 10/11 | INCOMPLETE | Target Scope decisions (no capabilities admitted yet); Source artifact for 5 of 9 Sources |
| **D2** — Product Backlog | 8/10 | INCOMPLETE | Feature Composition (0 Features created); Product Review (0 reviewed) |
| **D3** — Product Roadmap | 9/11 | INCOMPLETE | 0 Roadmap-admitted capabilities; 0 timed capabilities; 0 Features |
| **D4** — Common Migration Path | 15/15 | **AVAILABLE** | Nothing blocking — fully derivable from current data |
| **D5** — Customer Migration Plan | 0/19 | INCOMPLETE | Requires governed customer records (D3) |
| **D5a** — Pilot Set | 0 | BLOCKED | Requires D5 + governed pilot customers (DEPP, INVALSI, NSA, NCCER) |

**D4 is the only fully deliverable report today.** D1/D2/D3 become deliverable as Product completes the Candidate Review + Feature Composition + Admission steps.

---

## 10. HOW DO I RUN THE APP TODAY?

```bash
cd /Users/felixdiaz/Projects/tao-authoring-product-workspace
./start-local.sh
```

Then open **http://127.0.0.1:8080**

Verify you are on the right version:
```
curl http://127.0.0.1:8080/api/runtime-info
```

Expected: `"git_head": "a48fa10"` (or later) and `"database": "tao_authoring"`.

The app is currently **running** (PID from the last `./start-local.sh`). If it is not running, `./start-local.sh` will restart it.
