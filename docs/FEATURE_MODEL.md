# FEATURE_MODEL — Feature as a Product composition entity (UAT structural update §12–§15)

## Conceptual model position

```
Source Document → Source Capability → Cross-source Reconciliation
→ Canonical Capability → Feature Composition → Product Backlog → Roadmap → Migration Path
```

- **Capability** = Product Truth (canonical, CAP-xxxx, unchanged identity model).
- **Feature** = Product-managed **composition** of 1..N Canonical Capabilities — a planning construct for Product Managers.
- **Feature ≠ Jira Epic** (Jira = delivery/work evidence). **Feature ≠ Source Capability** (Source Capability = what one Source says).

## Identity & storage

- Stable governed IDs: **FEAT-0001, FEAT-0002, …** (regex-validated `^FEAT-[0-9]{4,}$`).
- `features(feat_id PK, name, description, owner, status, notes, version, created_at, updated_at)`
- `feature_capabilities(feat_id, cap_id, added_at, PK(feat_id, cap_id))` — **many-to-many** join; a Feature contains 1..N capabilities; a Capability may participate in multiple Features where Product explicitly decides. Unlinking removes **only the relationship** — Feature and Capability both survive (tested).
- Alembic `0003_uat_structural` (applied; downgrade drops the two tables only).

## API (all mutations: actor + audit + optimistic version)

| Endpoint | Behaviour |
|---|---|
| `GET /api/features` | list; each Feature embeds its capabilities + **derived** timing window |
| `POST /api/features` | create (409 on duplicate ID) |
| `GET/PATCH /api/features/{feat_id}` | read / version-guarded update (409 on stale) |
| `DELETE /api/features/{feat_id}` | delete the Feature; capabilities untouched |
| `POST/DELETE /api/features/{feat_id}/capabilities/{cap_id}` | link / unlink (409 duplicate link; 404 unknown feature/capability) |

## Derived coverage — not a second planning truth

`derived_timing_window` = min(start) / max(end) across the Feature's constituent capability timing. The Roadmap **Feature view** draws this as an outline explicitly labelled *derived*. **Feature timing semantics are not defined yet** — until Product defines them, Features carry **no independent timing** and cannot be dragged (capability bars remain the only editable timing truth).

## Composition governance (§15)

- Nothing auto-converts Source groupings into Features; no AI-determined composition.
- The UI creates Features only through the explicit Product editor (+ Feature → governed FEAT-id + name; constituent CAPs added/removed by explicit links).
- If AI grouping suggestions are introduced later, they must carry `PRODUCT REVIEW REQUIRED` until confirmed.

## Deliberately excluded (§13/§16)

Scoring attributes, Jira-Epic identity mapping, Source-Capability reuse, status automation beyond the plain `status` text field, feature-level budgets. Feature fields stay minimal by contract.
