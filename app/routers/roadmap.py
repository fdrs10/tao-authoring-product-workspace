"""Roadmap API (Phase 3).

- GET   /api/roadmap              planning view consuming canonical CAPs
                                  (default admission=COMMITTED, §34;
                                  Product timing only — Jira Target Release
                                  is exposed separately, never overwriting)
- PATCH /api/roadmap/{cap_id}     upsert roadmap timing (optimistic version)
- GET   /api/milestones           shared Roadmap/Migration milestone records
- POST  /api/milestones           create (we hold 0 rows until governed data)
- PATCH /api/milestones/{id}      version-guarded update
"""

from fastapi import APIRouter, Body, Depends, HTTPException
import psycopg

from ..audit import record_audit
from ..db import db_conn
from ..identity import Actor, get_actor
from ..models import MilestoneCreate, MilestonePatch, RoadmapTimingPatch

router = APIRouter(prefix="/api", tags=["roadmap"])


@router.get("/roadmap")
def get_roadmap(conn: psycopg.Connection = Depends(db_conn),
                admission: str | None = "COMMITTED",
                category: str | None = None,
                market: str | None = None,
                population: str | None = None):
    where, params = [], []
    # Population rule (CONTROLLED OPERATION §12/§19): default = ACTIVE — the
    # historical baseline never drives the Product Roadmap.
    if population is None or population == "active":
        where.append("""((SELECT count(*) FROM capabilities c2
                          WHERE c2.population = 'SOURCE_ANALYSIS_CANDIDATE') = 0
                         AND c.population IS DISTINCT FROM 'HISTORICAL_BASELINE_V1'
                         OR c.population = 'SOURCE_ANALYSIS_CANDIDATE')""")
    elif population == "historical":
        where.append("c.population = 'HISTORICAL_BASELINE_V1'")
    elif population == "all":
        pass
    if admission == "UNSET":
        where.append("c.roadmap_admission IS NULL")
    elif admission:
        where.append("c.roadmap_admission = %s")
        params.append(admission)
    # admission=None explicitly disables the admission filter (all states)
    if category is not None:
        where.append("c.strategic_category = %s")
        params.append(category)
    if market is not None:
        where.append(
            "EXISTS (SELECT 1 FROM capability_markets cm JOIN markets m "
            "ON m.market_id=cm.market_id WHERE cm.cap_id=c.cap_id "
            "AND m.name=%s)")
        params.append(market)

    sql = f"""
      SELECT c.cap_id, c.working_name, c.strategic_category, c.moscow,
             c.visibility, c.decision, c.roadmap_admission,
             r.start_month, r.duration_months, r.version AS timing_version,
             c.version AS cap_version,
        COALESCE((SELECT json_agg(m.name ORDER BY m.name)
                  FROM capability_markets cm JOIN markets m
                  ON m.market_id=cm.market_id
                  WHERE cm.cap_id=c.cap_id), '[]'::json) AS markets,
        COALESCE((SELECT json_agg(json_build_object('jira_key', cj.jira_key,
                    'status', j.status, 'target_release', j.target_release))
                  FROM capability_jira cj JOIN jira_tickets j
                  ON j.jira_key=cj.jira_key
                  WHERE cj.cap_id=c.cap_id), '[]'::json) AS jira
      FROM capabilities c
      LEFT JOIN roadmap_timing r ON r.cap_id = c.cap_id
      {("WHERE " + " AND ".join(where)) if where else ""}
      ORDER BY c.strategic_category, r.start_month NULLS LAST, c.cap_id
    """
    with conn.cursor() as cur:
        cur.execute(sql, params)
        cols = [d.name for d in cur.description]
        rows = [dict(zip(cols, r)) for r in cur.fetchall()]
    return {"count": len(rows), "admission_filter": admission, "items": rows}


@router.patch("/roadmap/{cap_id}")
def patch_roadmap_timing(cap_id: str, body: RoadmapTimingPatch,
                         conn: psycopg.Connection = Depends(db_conn),
                         actor: Actor = Depends(get_actor)):
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM capabilities WHERE cap_id=%s", (cap_id,))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404,
                                detail=f"capability {cap_id} not found")
        cur.execute("SELECT start_month, duration_months, version "
                    "FROM roadmap_timing WHERE cap_id=%s", (cap_id,))
        row = cur.fetchone()
        try:
            if row is None:
                cur.execute(
                    """INSERT INTO roadmap_timing
                         (cap_id, start_month, duration_months, version)
                       VALUES (%s,%s,%s,2)""",
                    (cap_id, body.start_month, body.duration_months))
                record_audit(cur, "roadmap_timing", cap_id, "create",
                             actor.user_ref, None,
                             {"start_month": body.start_month,
                              "duration_months": body.duration_months},
                             ["start_month", "duration_months"])
            else:
                before = {"start_month": row[0], "duration_months": row[1],
                          "version": row[2]}
                if row[2] != body.version:
                    raise HTTPException(
                        status_code=409,
                        detail={"error": "version_conflict",
                                "current_version": row[2],
                                "requested_version": body.version,
                                "message": "stale edit refused; refetch and reapply"})
                cur.execute(
                    """UPDATE roadmap_timing SET start_month=%s,
                         duration_months=%s, version=version+1
                       WHERE cap_id=%s""",
                    (body.start_month, body.duration_months, cap_id))
                record_audit(cur, "roadmap_timing", cap_id, "update",
                             actor.user_ref,
                             {k: before[k] for k in ("start_month", "duration_months")},
                             {"start_month": body.start_month,
                              "duration_months": body.duration_months},
                             ["start_month", "duration_months"])
                new_version = row[2] + 1
        except HTTPException:
            conn.rollback()
            raise
        conn.commit()
    return {"updated": True, "cap_id": cap_id,
            "version": new_version if row is not None else 2}


@router.get("/milestones")
def list_milestones(conn: psycopg.Connection = Depends(db_conn)):
    with conn.cursor() as cur:
        cur.execute(
            """SELECT milestone_id, name, milestone_date, scope_type,
                      scope_ref, description, position_month, version
               FROM milestones ORDER BY position_month NULLS LAST, milestone_id""")
        cols = [d.name for d in cur.description]
        rows = [dict(zip(cols, r)) for r in cur.fetchall()]
    return {"count": len(rows), "items": rows}


@router.post("/milestones", status_code=201)
def create_milestone(body: MilestoneCreate,
                     conn: psycopg.Connection = Depends(db_conn),
                     actor: Actor = Depends(get_actor)):
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM milestones WHERE milestone_id=%s",
                    (body.milestone_id,))
        if cur.rowcount:
            raise HTTPException(status_code=409,
                                detail=f"milestone {body.milestone_id} exists")
        cur.execute(
            """INSERT INTO milestones (milestone_id, name, milestone_date,
                 scope_type, scope_ref, description, position_month)
               VALUES (%s,%s,%s,%s,%s,%s,%s)""",
            (body.milestone_id, body.name, body.milestone_date,
             body.scope_type, body.scope_ref, body.description,
             body.position_month))
        record_audit(cur, "milestone", body.milestone_id, "create",
                     actor.user_ref, None,
                     body.model_dump(mode="json"), ["milestone"])
        conn.commit()
    return {"created": True, "milestone_id": body.milestone_id}


@router.patch("/milestones/{milestone_id}")
def patch_milestone(milestone_id: str, body: MilestonePatch,
                    conn: psycopg.Connection = Depends(db_conn),
                    actor: Actor = Depends(get_actor)):
    provided = body.model_dump(exclude_unset=True)
    version = provided.pop("version")
    if not provided:
        raise HTTPException(status_code=400, detail="no fields to update")
    with conn.cursor() as cur:
        cur.execute(
            """SELECT milestone_id, name, milestone_date, scope_type,
                      scope_ref, description, position_month, version
               FROM milestones WHERE milestone_id=%s""", (milestone_id,))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404,
                                detail=f"milestone {milestone_id} not found")
        cols = [d.name for d in cur.description]
        before = dict(zip(cols, cur.fetchone()))
    if before["version"] != version:
        raise HTTPException(status_code=409,
                            detail={"error": "version_conflict",
                                    "current_version": before["version"],
                                    "requested_version": version})
    try:
        with conn.cursor() as cur:
            sets = ", ".join(f"{k}=%s" for k in provided)
            cur.execute(
                f"UPDATE milestones SET {sets}, version=version+1 "
                "WHERE milestone_id=%s AND version=%s",
                (*provided.values(), milestone_id, version))
            record_audit(cur, "milestone", milestone_id, "update",
                         actor.user_ref,
                         {k: (before[k].isoformat() if hasattr(before[k], "isoformat") else before[k]) for k in provided},
                         {k: (v.isoformat() if hasattr(v, "isoformat") else v) for k, v in provided.items()},
                         list(provided))
            conn.commit()
    except HTTPException:
        conn.rollback()
        raise
    return {"updated": True, "milestone_id": milestone_id,
            "version": version + 1}
