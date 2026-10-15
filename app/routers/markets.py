"""Markets API — governed reference data for legends, filters and edits."""

from fastapi import APIRouter, Depends
import psycopg

from ..db import db_conn

router = APIRouter(prefix="/api/markets", tags=["markets"])


@router.get("")
def list_markets(conn: psycopg.Connection = Depends(db_conn)):
    with conn.cursor() as cur:
        cur.execute("SELECT market_id, name, color FROM markets ORDER BY name")
        cols = [d.name for d in cur.description]
        rows = [dict(zip(cols, r)) for r in cur.fetchall()]
    return {"count": len(rows), "items": rows}
