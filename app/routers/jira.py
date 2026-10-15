"""Jira API (Phase 3). Jira is delivery evidence, never capability truth (§6).

- GET /api/jira            ticket list (with linked CAP count)
- GET /api/jira/{key}      ticket detail incl 0..N canonical CAP relations
"""

from fastapi import APIRouter, Depends, HTTPException
import psycopg

from ..db import db_conn

router = APIRouter(prefix="/api/jira", tags=["jira"])

JT_COLS = """
  jira_key, issue_type, summary, description, status, lifecycle,
  target_release, due_date, assignee, jira_url, jira_estimate_hours,
  capability_treatment, reconciliation_rationale
"""


@router.get("")
def list_jira(conn: psycopg.Connection = Depends(db_conn),
              status: str | None = None,
              treatment: str | None = None):
    where, params = [], []
    if status is not None:
        where.append("status = %s")
        params.append(status)
    if treatment is not None:
        where.append("capability_treatment = %s")
        params.append(treatment)
    sql = f"""
      SELECT {JT_COLS},
        (SELECT count(*) FROM capability_jira cj
          WHERE cj.jira_key = j.jira_key) AS linked_capability_count
      FROM jira_tickets j
      {("WHERE " + " AND ".join(where)) if where else ""}
      ORDER BY j.jira_key
    """
    with conn.cursor() as cur:
        cur.execute(sql, params)
        cols = [d.name for d in cur.description]
        rows = [dict(zip(cols, r)) for r in cur.fetchall()]
    return {"count": len(rows), "items": rows}


@router.get("/{key}")
def get_jira(key: str, conn: psycopg.Connection = Depends(db_conn)):
    with conn.cursor() as cur:
        cur.execute(f"SELECT {JT_COLS} FROM jira_tickets WHERE jira_key=%s",
                    (key,))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404,
                                detail=f"jira ticket {key} not found")
        cols = [d.name for d in cur.description]
        ticket = dict(zip(cols, cur.fetchone()))
        cur.execute(
            """SELECT cj.cap_id, cj.relationship, cj.note, c.working_name
               FROM capability_jira cj JOIN capabilities c
                 ON c.cap_id = cj.cap_id
               WHERE cj.jira_key=%s ORDER BY cj.cap_id""", (key,))
        ticket["capabilities"] = [
            dict(zip([d.name for d in cur.description], r))
            for r in cur.fetchall()]
    return ticket
