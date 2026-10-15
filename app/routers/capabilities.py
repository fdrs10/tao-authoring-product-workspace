"""Capabilities API (Phase 3).

- GET    /api/capabilities            list + filters
- GET    /api/capabilities/{cap_id}   full canonical detail
- PATCH  /api/capabilities/{cap_id}   optimistic-concurrency update
                                      (version required; 409 on stale)
- POST   /api/capabilities/{cap_id}/jira            add Jira link (0..N)
- DELETE /api/capabilities/{cap_id}/jira/{jira_key} remove Jira link

Semantics: CAP-ID immutable; roadmap_admission NULL = UNSET (≠ BACKLOG);
budget NULL ≠ 0; every mutation audited with actor/before/after/changed.
Roadmap Admission edited here is THE one field shared by Cross-analysis,
Product Backlog and the Capability editor (§11).
"""

from fastapi import APIRouter, Depends, HTTPException, Request
import psycopg

from ..audit import record_audit
from ..db import db_conn
from ..identity import Actor, get_actor
from ..models import CapabilityPatch, JiraLinkCreate

router = APIRouter(prefix="/api", tags=["capabilities"])

CAP_COLS = """
  cap_id, working_name, description, strategic_category, moscow,
  visibility, scope, origin, owner, decision, v2_mapping, ideation_sheet,
  roadmap_admission, analysis_budget_hours, execution_budget_hours,
  notes, review_status, version, created_at, updated_at
"""

LIST_FILTER = {
    "category": "strategic_category",
    "moscow": "moscow",
    "visibility": "visibility",
    "ideation_sheet": "ideation_sheet",
    "decision": "decision",
    "origin": "origin",
}


def _cap_not_found(cap_id: str) -> HTTPException:
    return HTTPException(status_code=404, detail=f"capability {cap_id} not found")


@router.get("/capabilities")
def list_capabilities(
    conn: psycopg.Connection = Depends(db_conn),
    category: str | None = None,
    market: str | None = None,
    moscow: str | None = None,
    admission: str | None = None,  # explicit value or literal "UNSET" for NULL
    visibility: str | None = None,
    source: str | None = None,
    ideation_sheet: str | None = None,
    decision: str | None = None,
    origin: str | None = None,
):
    where, params = [], []
    for qv, col in (
        (category, "c.strategic_category"), (moscow, "c.moscow"),
        (visibility, "c.visibility"), (ideation_sheet, "c.ideation_sheet"),
        (decision, "c.decision"), (origin, "c.origin"),
    ):
        if qv is not None:
            where.append(f"{col} = %s")
            params.append(qv)
    if admission is not None:
        if admission == "UNSET":
            where.append("c.roadmap_admission IS NULL")
        else:
            where.append("c.roadmap_admission = %s")
            params.append(admission)
    if market is not None:
        where.append(
            "EXISTS (SELECT 1 FROM capability_markets cm JOIN markets m "
            "ON m.market_id = cm.market_id WHERE cm.cap_id = c.cap_id "
            "AND m.name = %s)"
        )
        params.append(market)
    if source is not None:
        where.append(
            "EXISTS (SELECT 1 FROM capability_sources cs "
            "WHERE cs.cap_id = c.cap_id AND cs.source_id = %s)"
        )
        params.append(source)

    sql = f"""
      SELECT {CAP_COLS},
        COALESCE((SELECT json_agg(m.name ORDER BY m.name)
                  FROM capability_markets cm JOIN markets m
                  ON m.market_id = cm.market_id
                  WHERE cm.cap_id = c.cap_id), '[]'::json) AS markets,
        COALESCE((SELECT json_agg(m.color ORDER BY m.name)
                  FROM capability_markets cm JOIN markets m
                  ON m.market_id = cm.market_id
                  WHERE cm.cap_id = c.cap_id), '[]'::json) AS market_colors,
        (SELECT count(*) FROM capability_jira cj
          WHERE cj.cap_id = c.cap_id) AS jira_link_count,
        COALESCE((SELECT json_agg(json_build_object(
                    'jira_key', cj.jira_key, 'status', j.status,
                    'target_release', j.target_release, 'url', j.jira_url)
                  ORDER BY cj.jira_key)
                  FROM capability_jira cj JOIN jira_tickets j
                  ON j.jira_key = cj.jira_key
                  WHERE cj.cap_id = c.cap_id), '[]'::json) AS jira,
        (SELECT count(*) FROM capability_sources cs
          WHERE cs.cap_id = c.cap_id) AS source_link_count
      FROM capabilities c
      {("WHERE " + " AND ".join(where)) if where else ""}
      ORDER BY c.cap_id
    """
    with conn.cursor() as cur:
        cur.execute(sql, params)
        cols = [d.name for d in cur.description]
        rows = [dict(zip(cols, r)) for r in cur.fetchall()]
    return {"count": len(rows), "items": rows}


@router.get("/capabilities/{cap_id}")
def get_capability(cap_id: str, conn: psycopg.Connection = Depends(db_conn)):
    with conn.cursor() as cur:
        cur.execute(f"SELECT {CAP_COLS} FROM capabilities WHERE cap_id=%s",
                    (cap_id,))
        if cur.rowcount == 0:
            raise _cap_not_found(cap_id)
        cols = [d.name for d in cur.description]
        cap = dict(zip(cols, cur.fetchone()))

        cur.execute(
            """SELECT m.name, m.color FROM capability_markets cm
               JOIN markets m ON m.market_id = cm.market_id
               WHERE cm.cap_id=%s ORDER BY m.name""", (cap_id,))
        cap["markets"] = [{"name": n, "color": c} for n, c in cur.fetchall()]

        cur.execute(
            """SELECT cs.source_id, s.title, cs.relationship
               FROM capability_sources cs JOIN sources s
                 ON s.source_id = cs.source_id
               WHERE cs.cap_id=%s ORDER BY cs.source_id""", (cap_id,))
        cap["sources"] = [dict(zip([d.name for d in cur.description], r))
                          for r in cur.fetchall()]

        cur.execute(
            """SELECT sc.source_capability_id, sc.source_id, sc.original_name,
                      sc.reconciliation_relationship
               FROM source_capabilities sc
               WHERE sc.canonical_cap_id=%s ORDER BY sc.source_capability_id""",
            (cap_id,))
        cap["source_capabilities"] = [
            dict(zip([d.name for d in cur.description], r))
            for r in cur.fetchall()]

        cur.execute(
            """SELECT cj.jira_key, cj.relationship, cj.note,
                      j.summary, j.status, j.lifecycle, j.target_release,
                      j.due_date, j.assignee, j.jira_url, j.capability_treatment
               FROM capability_jira cj JOIN jira_tickets j
                 ON j.jira_key = cj.jira_key
               WHERE cj.cap_id=%s ORDER BY cj.jira_key""", (cap_id,))
        cap["jira"] = [dict(zip([d.name for d in cur.description], r))
                       for r in cur.fetchall()]

        cur.execute(
            "SELECT start_month, duration_months, version FROM roadmap_timing "
            "WHERE cap_id=%s", (cap_id,))
        rt = cur.fetchone()
        cap["roadmap_timing"] = (
            {"start_month": rt[0], "duration_months": rt[1], "version": rt[2]}
            if rt else None)

    a, e = cap.get("analysis_budget_hours"), cap.get("execution_budget_hours")
    cap["total_budget_hours"] = (
        None if (a is None and e is None) else (a or 0) + (e or 0))
    cap["capability_version"] = cap["version"]
    return cap


@router.patch("/capabilities/{cap_id}")
def patch_capability(cap_id: str, body: CapabilityPatch,
                     conn: psycopg.Connection = Depends(db_conn),
                     actor: Actor = Depends(get_actor)):
    errors = body.validate_enums()
    if errors:
        raise HTTPException(status_code=422, detail=errors)

    provided = body.model_dump(exclude_unset=True)
    markets_requested = provided.pop("markets", None)
    version = provided.pop("version")
    if not provided and markets_requested is None:
        raise HTTPException(status_code=400,
                            detail="no fields to update were provided")

    with conn.cursor() as cur:
        cur.execute(f"SELECT {CAP_COLS} FROM capabilities WHERE cap_id=%s",
                    (cap_id,))
        if cur.rowcount == 0:
            raise _cap_not_found(cap_id)
        cols = [d.name for d in cur.description]
        before = dict(zip(cols, cur.fetchone()))

    if before["version"] != version:
        raise HTTPException(
            status_code=409,
            detail={"error": "version_conflict",
                    "current_version": before["version"],
                    "requested_version": version,
                    "message": "stale edit refused; refetch and reapply"})

    # resolve requested market names to ids
    new_market_pairs = None
    if markets_requested is not None:
        if not isinstance(markets_requested, list):
            raise HTTPException(status_code=422, detail="markets must be a list")
        with conn.cursor() as cur:
            cur.execute("SELECT name, market_id FROM markets")
            by_name = {n: i for n, i in cur.fetchall()}
        unknown = [m for m in markets_requested if m not in by_name]
        if unknown:
            raise HTTPException(status_code=422,
                                detail={"unknown_markets": unknown})
        new_market_pairs = sorted(by_name[m] for m in set(markets_requested))

    changed_cols = {k: v for k, v in provided.items()
                    if before[k] != v}
    market_change = None
    if new_market_pairs is not None:
        with conn.cursor() as cur:
            cur.execute("SELECT market_id FROM capability_markets "
                        "WHERE cap_id=%s", (cap_id,))
            current_pairs = sorted(r[0] for r in cur.fetchall())
        if current_pairs != new_market_pairs:
            market_change = {"before": current_pairs, "after": new_market_pairs}

    if not changed_cols and market_change is None:
        return {"updated": False, "cap_id": cap_id,
                "message": "no changes", "version": version}

    with conn.cursor() as cur:
        try:
            if changed_cols:
                sets = ", ".join(f"{k}=%s" for k in changed_cols)
                cur.execute(
                    f"""UPDATE capabilities SET {sets},
                          version = version + 1, updated_at = now()
                        WHERE cap_id=%s AND version=%s""",
                    (*changed_cols.values(), cap_id, version))
            else:
                cur.execute(
                    "UPDATE capabilities SET version = version + 1, "
                    "updated_at = now() WHERE cap_id=%s AND version=%s",
                    (cap_id, version))
            if cur.rowcount == 0:
                raise HTTPException(status_code=409,
                                    detail={"error": "version_conflict"})
            if market_change is not None:
                cur.execute("DELETE FROM capability_markets WHERE cap_id=%s",
                            (cap_id,))
                for mid in new_market_pairs:
                    cur.execute(
                        "INSERT INTO capability_markets (cap_id, market_id) "
                        "VALUES (%s,%s)", (cap_id, mid))

            before_diff = {k: before[k] for k in changed_cols}
            after_diff = dict(changed_cols)
            changed_names = list(changed_cols)
            if market_change is not None:
                before_diff["markets"] = market_change["before"]
                after_diff["markets"] = market_change["after"]
                changed_names.append("markets")
            record_audit(cur, "capability", cap_id, "update",
                         actor.user_ref, before_diff, after_diff, changed_names)
            cur.execute(
                "INSERT INTO users (user_ref) VALUES (%s) "
                "ON CONFLICT (user_ref) DO NOTHING", (actor.user_ref,))
        except HTTPException:
            conn.rollback()
            raise
        except Exception:
            conn.rollback()
            raise HTTPException(status_code=500, detail="update failed")
        conn.commit()
    return {"updated": True, "cap_id": cap_id, "version": version + 1,
            "changed": list(changed_cols) + (["markets"] if market_change else [])}


@router.post("/capabilities/{cap_id}/jira", status_code=201)
def add_jira_link(cap_id: str, body: JiraLinkCreate,
                  conn: psycopg.Connection = Depends(db_conn),
                  actor: Actor = Depends(get_actor)):
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM capabilities WHERE cap_id=%s", (cap_id,))
        if cur.rowcount == 0:
            raise _cap_not_found(cap_id)
        cur.execute("SELECT 1 FROM jira_tickets WHERE jira_key=%s",
                    (body.jira_key,))
        if cur.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail=f"jira ticket {body.jira_key} not in governed Jira data")
        cur.execute(
            "SELECT relationship, note FROM capability_jira "
            "WHERE cap_id=%s AND jira_key=%s", (cap_id, body.jira_key))
        existing = cur.fetchone()
        created = existing is None
        if created:
            cur.execute(
                "INSERT INTO capability_jira (cap_id, jira_key, relationship, note) "
                "VALUES (%s,%s,%s,%s)",
                (cap_id, body.jira_key, body.relationship, body.note))
            before_snap = None
        else:
            cur.execute(
                "UPDATE capability_jira SET relationship=%s, note=%s "
                "WHERE cap_id=%s AND jira_key=%s",
                (body.relationship, body.note, cap_id, body.jira_key))
            before_snap = {"relationship": existing[0], "note": existing[1]}
        record_audit(cur, "capability_jira", f"{cap_id}:{body.jira_key}",
                     "create" if created else "update", actor.user_ref,
                     before_snap,
                     {"cap_id": cap_id, "jira_key": body.jira_key,
                      "relationship": body.relationship, "note": body.note},
                     ["capability_jira_link"])
        conn.commit()
    return {"cap_id": cap_id, "jira_key": body.jira_key, "created": bool(created)}


@router.delete("/capabilities/{cap_id}/jira/{jira_key}")
def remove_jira_link(cap_id: str, jira_key: str,
                     conn: psycopg.Connection = Depends(db_conn),
                     actor: Actor = Depends(get_actor)):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT relationship, note FROM capability_jira "
            "WHERE cap_id=%s AND jira_key=%s", (cap_id, jira_key))
        row = cur.fetchone()
        if not row:
            raise HTTPException(
                status_code=404,
                detail=f"jira link {cap_id}:{jira_key} not found")
        cur.execute(
            "DELETE FROM capability_jira WHERE cap_id=%s AND jira_key=%s",
            (cap_id, jira_key))
        record_audit(cur, "capability_jira", f"{cap_id}:{jira_key}", "delete",
                     actor.user_ref,
                     {"relationship": row[0], "note": row[1]}, None,
                     ["capability_jira_link"])
        conn.commit()
    return {"deleted": True, "cap_id": cap_id, "jira_key": jira_key}
