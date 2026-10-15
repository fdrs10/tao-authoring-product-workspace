# Known Defects / Mandatory Fixes

1. **Edit Capability -> Add Jira Link**: button currently may do nothing. Must create an editable Jira relationship row and persist it.
2. **Sources -> Jira Current Backlog**: must open source record and show all Jira rows/extracted mappings.
3. **Sources document access**: every source must expose human name + document/source record + extracted source capabilities.
4. **Cross-analysis Roadmap Admission**: editable there, same canonical field as Product Backlog.
5. **Universal CAP modal**: CAP-ID clickable in every capability-bearing view.
6. **Prioritised Summary**: must be derived strictly from the capabilities rendered in the decision blocks above under the same filters; never a separate population.
7. **Customer transitions**: real milestone intervals only; no TS1/TS2/TS3 UI.
8. **Market legend**: required anywhere colored market dots appear.
9. **Authoring-only scope**: review canonical data and reject non-Authoring capabilities; dependencies may be modeled separately.
10. **Navigation/filter regression**: every Ideation page, Roadmap, Migration and Sources filter must have automated acceptance coverage.
11. **Do not reproduce historical white-screen failures**: JS/runtime errors must fail CI; browser smoke test must confirm first render.
