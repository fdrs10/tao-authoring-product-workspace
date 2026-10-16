"""Sources & Evidence API (Phase 3).

Sources are *governed reference data*: read-only via API in this phase
(import pipeline owns writes). Endpoints:
- GET /api/sources                    register + extracted-capability counts
- GET /api/sources/{source_id}        full metadata + document location
- GET /api/sources/{source_id}/capabilities
                                       extracted Source Capabilities with
                                       reconciliation -> canonical CAP
Source Truth is preserved verbatim; Product interpretation lives only on
the canonical side (§18).
"""

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
import psycopg

from ..db import db_conn

router = APIRouter(prefix="/api/sources", tags=["sources"])

SRC_COLS = """
  source_id, title, source_type, owner, source_date, version_label,
  document_uri, summary, input_form, upstream_reference, status, version
"""


@router.get("")
def list_sources(conn: psycopg.Connection = Depends(db_conn)):
    sql = f"""
      SELECT {SRC_COLS},
        (SELECT count(*) FROM source_capabilities sc
          WHERE sc.source_id = s.source_id) AS extracted_capability_count
      FROM sources s ORDER BY s.source_id
    """
    with conn.cursor() as cur:
        cur.execute(sql)
        cols = [d.name for d in cur.description]
        rows = [dict(zip(cols, r)) for r in cur.fetchall()]
    for row in rows:
        row["document_available"] = _document_path(row.get("document_uri")) is not None
    return {"count": len(rows), "items": rows}


def _document_path(document_uri: str | None):
    """Resolve a registered document_uri to a repo file path, or None.

    Supported references: 'local://<source>/<name>' (artifact store) and
    legacy repo-relative 'data/...' paths (governed raw files). Path escapes
    are refused. Absent files → None (Source document unavailable).
    """
    if not document_uri:
        return None
    repo = Path(__file__).resolve().parents[2]
    if document_uri.startswith("local://"):
        rel = document_uri.split("://", 1)[1]
        candidate = repo / "data" / "source-documents" / rel
    else:
        candidate = (repo / document_uri).resolve()
    try:
        candidate = candidate.resolve()
        candidate.relative_to(repo)
    except (ValueError, OSError):
        return None
    return candidate if candidate.is_file() else None


@router.get("/{source_id}/document")
def get_source_document(source_id: str,
                        conn: psycopg.Connection = Depends(db_conn)):
    """Open Source: stream the registered original artifact.

    404 (machine-readable) when the Source has no recoverable artifact —
    the UI shows 'Source document unavailable' and never a fake action.
    """
    from fastapi.responses import FileResponse

    with conn.cursor() as cur:
        cur.execute("SELECT document_uri FROM sources WHERE source_id=%s",
                    (source_id,))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404,
                                detail={"error": "source_not_found",
                                        "source_id": source_id})
        uri = cur.fetchone()[0]
    path = _document_path(uri)
    if path is None:
        raise HTTPException(
            status_code=404,
            detail={"error": "source_document_unavailable",
                    "source_id": source_id,
                    "message": "the original artifact could not be recovered; "
                               "see docs/SOURCE_DOCUMENT_COVERAGE_REPORT.md"})
    return FileResponse(path, filename=path.name)


@router.get("/{source_id}")
def get_source(source_id: str, conn: psycopg.Connection = Depends(db_conn)):
    with conn.cursor() as cur:
        cur.execute(f"SELECT {SRC_COLS} FROM sources WHERE source_id=%s",
                    (source_id,))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404,
                                detail=f"source {source_id} not found")
        cols = [d.name for d in cur.description]
        src = dict(zip(cols, cur.fetchone()))
        cur.execute(
            """SELECT s.source_capability_id FROM source_capabilities s
               WHERE s.source_id=%s""", (source_id,))
        src["extracted_capability_count"] = cur.rowcount
    return src


@router.get("/{source_id}/capabilities")
def source_capabilities(source_id: str,
                        conn: psycopg.Connection = Depends(db_conn)):
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM sources WHERE source_id=%s", (source_id,))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404,
                                detail=f"source {source_id} not found")
        cur.execute(
            """SELECT sc.source_capability_id, sc.source_id,
                      sc.original_name, sc.original_description,
                      sc.source_category, sc.evidence_reference,
                      sc.source_confidence, sc.extraction_type,
                      sc.review_status, sc.notes,
                      sc.canonical_cap_id, sc.reconciliation_relationship,
                      c.working_name AS canonical_cap_name
               FROM source_capabilities sc
               LEFT JOIN capabilities c ON c.cap_id = sc.canonical_cap_id
               WHERE sc.source_id=%s
               ORDER BY sc.source_capability_id""", (source_id,))
        cols = [d.name for d in cur.description]
        rows = [dict(zip(cols, r)) for r in cur.fetchall()]
    return {"source_id": source_id, "count": len(rows), "items": rows}
