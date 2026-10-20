# TO_BE_INFORMATION_ARCHITECTURE

**Date:** 2026-10-16

## Navigation structure

```
HOME
├── NEEDS YOUR ATTENTION (derived from data)
├── CONTINUE WORKING (action cards)
├── QUICK ACTIONS
└── RECENT CHANGES (from audit_events)

PRODUCT
├── Evidence (#/evidence) — 426-signal explorer + promote
├── Capabilities (#/capabilities) — 34 candidates + enrichment + Ideation lenses
│   ├── tabs: All | Focus | Needs Review | Confirmed | Not Selected
│   ├── subtabs (Ideation lenses): V1 | 3.x | New Needs | Discontinued | Cross-analysis
│   └── Candidate modal (universal editor)
├── Features (#/features) — Feature compositions
│   ├── list + create + edit
│   └── Feature editor (definition, capabilities, context, discussion)
└── Roadmap (#/roadmap) — timing + milestones + outcome
    ├── Capabilities | Features switch
    ├── Full / 0–6m / 7–24m / Tail
    ├── Milestone lines (drag + editor)
    └── Quarter drill-down

CUSTOMERS
├── Customers (#/customers) — customer list + plans
│   ├── list + create + edit
│   ├── Customer plan (context, needs, dependencies, validation)
│   └── Customer×Feature matrix
└── Migration (#/migration) — Common Migration Path
    ├── M1–M6 + intervals + value derivation
    └── Migration Path | Customer Plans switch

OUTPUT
└── Deliverables (#/reports) — D1–D5/D5a
    ├── contracts + completeness + generate
    └── preview + print/save PDF
```

## Key design decisions

1. **Ideation lenses are tabs within Capabilities** — not separate pages. A PM opens Capabilities and switches between All/Focus/Needs Review views and the Ideation analysis lenses.
2. **Sources are accessed from Evidence** — the Source Registry is accessible from the Evidence Explorer header.
3. **Backlog is a view within Capabilities** (or a separate tab) — not a duplicate navigation item.
4. **Reports are the primary output** — the PM's normal work progressively completes them.
5. **Every entity has ONE editor** — reachable from any screen that references it.
