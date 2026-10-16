# PRODUCT_DECISIONS_PENDING — DEV candidate v1.0

Everything below **works as shipped** with a deterministic provisional rule; Product confirmation (or a change) is requested during UAT. None block DEV use.

| ID | Topic | Current behaviour (provisional) | Decision requested | Impact if changed |
|---|---|---|---|---|
| D-R1 | Roadmap middle level ("Big Rock / Market") | `Shared / common core` caps → one band per category; market-configured + market-specific caps → one band per governed market (a cap may appear in several market bands; 199 bar placements for 135 caps) | Confirm the grouping rule or supply Big-Rock definitions | Roadmap lane structure + bar counts |
| D-M1 | Migration "capability unlocked" semantics | **Unlocked by start of interval** = COMMITTED cap with `start+duration ≤ interval start`; **In flight** = window overlaps the interval | Confirm definitions (e.g. should partial overlap count as available?) | Migration band contents |
| D-R2 | Tail horizon window | Months 24–26 (Full=0–26, 0–6m=0–5, 7–24m=6–23) | Confirm | Horizon labels only |
| D-R3 | Roadmap default population | Roadmap Admission = COMMITTED (empty today — governed data has 133 UNSET + 2 CANDIDATE) | Product to commit admissions during UAT; confirm default filter | Default roadmap content |
| D2 | Milestones | Empty; create/edit UI + API live; historical M1–M6 recovered as test fixtures only | Supply the governed milestone list (IDs, names, dates) | Roadmap lines + Migration intervals |
| D3 | Customers | Empty; model + API + UI ready (blockers, `M1 -> M2` intervals, validation status) | Supply the governed customer dataset | Migration customer band |
| D5 | Identity | DEV uses the replaceable `X-User-Ref` header/chip (user_ref per person, audited) | Confirm the UAT user_ref convention; later: IdP integration via `app/identity.py` seam | Audit labels only — no entity coupling |
| ADM | Admission workflow | No approval workflow this phase: Product edits Admission directly; audit + actor + optimistic concurrency provide control | Confirm this remains acceptable for UAT and beyond | Workflow only if Product asks |

Also recorded (not decisions — confirmations): v2_mapping truncation to 60 chars in Cross-analysis cells (full value in the CAP drawer/export); decision label census is verbatim (`Develop` kept distinct from `DEVELOP / VALIDATE` — G5 rule).
