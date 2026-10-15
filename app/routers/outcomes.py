"""Roadmap Outcome API (Phase 5, contract §6/§18).

- GET   /api/outcomes              the three horizon narratives
                                   ('0-6m', '7-24m', 'tail'); rows created
                                   on demand with NULL narrative — no
                                   invented content.
- PATCH /api/outcomes/{horizon}    optimistic-concurrency update
                                   (version + actor + audit_events).

Recovered from v38.6's Roadmap | Outcome switch (narratives were in
localStorage there); shared Product state is server-persisted here.
"""

from fastapi import APIRouter, Depends, HTTPException
import psycopg

from ..audit import record_audit
from ..db import db_conn
from ..identity import Actor, get_actor
from ..models import OutcomePatch

router = APIRouter(prefix="/api", tags=["outcomes"])

HORIZONS = ("0-6m", "7-24m", "tail")

OUTCOME_COLS = "horizon, narrative, version, updated_at, updated_by"


def _ensure_rows(cur: psycopg.Cursor) -> None:
    cur.execute(
        """INSERT INTO roadmap_outcomes (horizon)
           SELECT h FROM unnest(%s::text[]) AS h
           ON CONFLICT (horizon) DO NOTHING""", (list(HORIZONS),))


@router.get("/outcomes")
def get_outcomes(conn: psycopg.Connection = Depends(db_conn)):
    with conn.cursor() as cur:
        _ensure_rows(cur)
        cur.execute(f"SELECT {OUTCOME_COLS} FROM roadmap_outcomes "
                    "ORDER BY array_position(%s::text[], horizon)",
                    (list(HORIZONS),))
        cols = [d.name for d in cur.description]
        rows = [dict(zip(cols, r)) for r in cur.fetchall()]
    conn.commit()
    return {"count": len(rows), "items": rows}


@router.patch("/outcomes/{horizon}")
def patch_outcome(horizon: str, body: OutcomePatch,
                  conn: psycopg.Connection = Depends(db_conn),
                  actor: Actor = Depends(get_actor)):
    if horizon not in HORIZONS:
        raise HTTPException(status_code=404,
                            detail=f"unknown horizon {horizon!r} "
                                   f"(expected one of {list(HORIZONS)})")
    with conn.cursor() as cur:
        _ensure_rows(cur)
        cur.execute(f"SELECT {OUTCOME_COLS} FROM roadmap_outcomes "
                    "WHERE horizon=%s", (horizon,))
        cols = [d.name for d in cur.description]
        before = dict(zip(cols, cur.fetchone()))
        if before["version"] != body.version:
            conn.rollback()
            raise HTTPException(
                status_code=409,
                detail={"error": "version_conflict",
                        "current_version": before["version"],
                        "requested_version": body.version,
                        "message": "stale outcome edit refused; refetch and reapply"})
        cur.execute(
            """UPDATE roadmap_outcomes
               SET narrative=%s, version=version+1, updated_at=now(),
                   updated_by=%s
               WHERE horizon=%s""",
            (body.narrative, actor.user_ref, horizon))
        record_audit(cur, "roadmap_outcome", horizon, "update",
                     actor.user_ref, {"narrative": before["narrative"]},
                     {"narrative": body.narrative}, ["narrative"])
    conn.commit()
    return {"updated": True, "horizon": horizon, "version": body.version + 1}
