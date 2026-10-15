# Functional Acceptance Suite

## Smoke
- App loads with non-empty first screen; browser console has no uncaught errors.
- Main nav opens Ideation, Roadmap, Migration Path, Sources & Evidence.

## Ideation
- All six Ideation pages open.
- Filters Market/MoSCoW/Visibility/Decision work.
- Prioritised Summary equals union of currently rendered decision rows under filters.
- Cross-analysis and Product Backlog show same canonical CAP identities.
- Roadmap Admission edit in Cross-analysis immediately appears in Product Backlog and Roadmap eligibility.

## Capability
- Clicking any CAP-ID opens the same detail modal.
- Add/remove Jira link works and persists.
- Analysis/Execution budgets accept hours; Total = sum.
- Sources show `SRC-ID · document name`.

## Sources
- Open source/source record works.
- View extracted capabilities works and shows source-local -> canonical mapping.
- Jira source shows all imported Jira tickets plus reconciliation treatment.

## Roadmap
- Default Full view.
- Independent category/Big Rock expansion.
- Drag/left resize/right resize/month snap persist.
- Milestone labels appear once.
- Quarter report works.
- Admission filter works.

## Migration
- Same milestones as Roadmap.
- Capabilities unlocked derive from Roadmap timing.
- Customers use milestone intervals.
- Market legend visible.

## Scope
- No non-Authoring capability admitted without explicit Product decision.
