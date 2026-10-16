#!/usr/bin/env python3
"""Materialise recoverable Source documents + emit the coverage report.

Contract (UAT STRUCTURAL UPDATE §3/§4):
- The original artifact is Product evidence. Where a governed copy physically
  exists in this repository it is connected to its Source (document_uri) and
  copied faithfully into the artifact store (data/source-documents/<SRC-ID>/).
- Where the original was Confluence paste / supplied text that was never
  materialised, document_uri stays empty: the UI shows
  "Source document unavailable". Extract CSVs are derived datasets, NOT the
  original artifact, and are never passed off as one.
- Idempotent: re-running makes no further changes.
"""

import json
import os
import shutil
import sys
from pathlib import Path

import psycopg

REPO_ROOT = Path(__file__).resolve().parents[2]
STORE = REPO_ROOT / "data" / "source-documents"
REPORT = REPO_ROOT / "data" / "reports" / "source_document_coverage.json"


def main() -> int:
    url = (os.environ.get("DATABASE_URL")
           or os.environ.get("DB_URL", ""))
    if url.startswith("postgresql+psycopg://") or url.startswith("postgresql+psycopg2://"):
        url = "postgresql://" + url.split("://", 1)[1]
    if not url:
        print("ERROR: DATABASE_URL required", file=sys.stderr)
        return 2

    # governed artifact locations inside the repository (verified to exist)
    recoverable = {
        "SRC-OECD-001": ("data/raw/SRC-OECD-001_OECD_Digital_Education_Outlook_2026.pdf",
                         "OECD_Digital_Education_Outlook_2026.pdf"),
        "SRC-GAP-001": ("data/raw/SRC_GAP_TAO_3X_VS_STUDIO_V1.txt",
                        "SRC_GAP_TAO_3X_VS_STUDIO_V1.txt"),
        "SRC-JIRA-001": ("data/raw/JIRA_current_backlog.csv",
                         "JIRA_current_backlog.csv"),
    }

    with psycopg.connect(url, autocommit=True) as conn, conn.cursor() as cur:
        cur.execute("SELECT source_id, title, document_uri FROM sources ORDER BY source_id")
        sources = cur.fetchall()
        report_rows = []
        for source_id, title, uri in sources:
            sc_count = cur.execute(
                "SELECT count(*) FROM source_capabilities WHERE source_id=%s",
                (source_id,)).fetchone()[0]
            problem, action = "", ""
            new_uri = uri
            if source_id in recoverable:
                rel, dest_name = recoverable[source_id]
                src_path = REPO_ROOT / rel
                if not src_path.is_file():
                    problem, action = "listed artifact missing", "investigate repository"
                else:
                    dest = STORE / source_id / dest_name
                    if not dest.is_file() or dest.read_bytes() != src_path.read_bytes():
                        dest.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copyfile(src_path, dest)  # faithful byte copy
                        action = "artifact copied to store"
                    want = f"local://{source_id}/{dest_name}"
                    if uri != want:
                        cur.execute("UPDATE sources SET document_uri=%s "
                                    "WHERE source_id=%s", (want, source_id))
                        action = (action + "; " if action else "") + "document_uri connected"
                    new_uri = want
            else:
                problem = ("original was Confluence paste / supplied analysis text; "
                           "never materialised into the handoff")
                action = "Product to supply the original artifact (source package)"
            report_rows.append({
                "source_id": source_id,
                "human_name": title,
                "original_artifact": (
                    recoverable[source_id][0] if source_id in recoverable
                    else ("(external Jira export was registered with document_uri)" if uri else "not materialised")),
                "repository_location": new_uri or None,
                "openable": bool(new_uri),
                "extracted_source_capabilities": sc_count,
                "problem_or_action": problem or action or "connected",
            })
        report = {
            "generated_by": "scripts/import/materialize_source_documents.py",
            "principle": "PostgreSQL keeps Source metadata/lineage (Product Truth); "
                         "object/document storage keeps artifacts only",
            "rows": report_rows,
        }
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        REPORT.write_text(json.dumps(report, indent=1))
        print(json.dumps(report, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
