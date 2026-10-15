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
    return {"count": len(rows), "items": rows}


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
