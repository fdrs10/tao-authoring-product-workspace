# SOURCE_DOCUMENT_COVERAGE_REPORT

**Generated:** 2026-10-16 · **By:** `scripts/import/materialize_source_documents.py` (idempotent) · **Data:** `data/reports/source_document_coverage.json`
**Principle (§3):** PostgreSQL keeps Source metadata/lineage (Product Truth); document storage keeps artifacts only. Open Source opens the **actual artifact** or states **"Source document unavailable"** — never a fake action, never an invented URL.

| Source ID | Human name | Original artifact | Repository/storage location | Openable | Extracted Source Capabilities | Problem/Action |
|---|---|---|---|---|---|---|
| SRC-3X-001 | TAO Authoring - feature list | Confluence copy/paste (not materialised) | — | **NO** | 83 | Original paste never materialised into the handoff. Action: Product supplies it as a source package (§25/§26). |
| SRC-COMP-001 | TAO AI Competitor Intelligence Report | User-provided report text, Aug 2026 (not materialised) | — | **NO** | 14 | Same as above. |
| SRC-GAP-001 | TAO Authoring - TAO Studio gap analysis | `data/raw/SRC_GAP_TAO_3X_VS_STUDIO_V1.txt` | `data/source-documents/SRC-GAP-001/SRC_GAP_TAO_3X_VS_STUDIO_V1.txt` (`local://SRC-GAP-001/…`) | **YES** (inline text) | 0 | Connected. |
| SRC-HTML-001 | Existing TAO Authoring HTML capability seed | `TAO_Authoring_v36_9_FIXED_REFERENCE_DIAGRAM.html` (referenced upstream) | — | **NO** | 0 | v36.9 file not present in `/legacy` (only v35.6/36.1/37.0/38.6/v10). Action: Product supplies the referenced HTML. |
| SRC-JIRA-001 | Current Authoring Jira Backlog | `data/raw/JIRA_current_backlog.csv` | `data/source-documents/SRC-JIRA-001/JIRA_current_backlog.csv` (`local://SRC-JIRA-001/…`) | **YES** (CSV download) | 0 (delivery evidence, by design) | Connected. |
| SRC-NEW-001 | TAO Authoring Strategic Initiative | User-provided text (not materialised) | — | **NO** | 21 | Same as 3X/COMP. |
| SRC-OECD-001 | OECD Digital Education Outlook 2026 | `data/raw/SRC-OECD-001_OECD_Digital_Education_Outlook_2026.pdf` | `data/source-documents/SRC-OECD-001/OECD_Digital_Education_Outlook_2026.pdf` (`local://SRC-OECD-001/…`) | **YES** (PDF, 11 MB) | 15 | Connected. |
| SRC-V1-001 | TAO Studio - feature list | Confluence copy/paste; upstream refs `TAO3.x-Studio.pdf`, `tao-studio-sales-capability-map.pdf`, module packages (none in repo) | — | **NO** | 91 | Originals referenced but not materialised. Action: Product supplies. |

**Totals:** 8 sources · 3 openable · 5 unavailable · 224 extracted Source Capabilities (V1 91, 3X 83, NEW 21, OECD 15, COMP 14 — GAP/HTML/JIRA register evidence only, by design).

**Rule honoured:** extracted `*_CAPS.csv` files are **derived datasets** (already represented as Source Capabilities in PostgreSQL) and are never presented as the original artifact.

**Next-stage readiness:** when Product supplies a source package (§25), the materializer pattern applies unchanged: artifact → `data/source-documents/<SRC-ID>/`, `document_uri = local://<SRC-ID>/<name>`, metadata updated by the controlled import — never ad-hoc SQL.
