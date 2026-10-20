"""Collaboration + Home API (Phase A).

- GET  /api/comments?entity_type=&entity_id=   discussion threads
- POST /api/comments                           add a comment
- PATCH /api/comments/{id}                     resolve/unresolve
- GET  /api/recent-changes                     recent audit events (all entity types)
- GET  /api/home                               PM attention items + counts
"""

from fastapi import APIRouter, Depends, HTTPException
import psycopg

from ..audit import record_audit
from ..config import settings
from ..db import db_conn
from ..identity import Actor, get_actor

router = APIRouter(prefix="/api", tags=["collaboration"])


@router.get("/comments")
def list_comments(entity_type: str | None = None, entity_id: str | None = None,
                  conn: psycopg.Connection = Depends(db_conn)):
    where, params = [], []
    if entity_type:
        where.append("entity_type=%s"); params.append(entity_type)
    if entity_id:
        where.append("entity_id=%s"); params.append(entity_id)
    w = ("WHERE " + " AND ".join(where)) if where else ""
    with conn.cursor() as cur:
        cur.execute(f"""SELECT comment_id, entity_type, entity_id, parent_id,
                              author, comment, resolved, created_at
                       FROM comments {w} ORDER BY created_at DESC LIMIT 200""")
        cols = [d.name for d in cur.description]
        items = []
        for r in cur.fetchall():
            row = dict(zip(cols, r))
            row["created_at"] = row["created_at"].isoformat()
            items.append(row)
    return {"count": len(items), "items": items}


@router.post("/comments/create", status_code=201)
def create_comment_post(body: dict,
                        conn: psycopg.Connection = Depends(db_conn),
                        actor: Actor = Depends(get_actor)):
    """Add a comment to any entity."""
    entity_type = body.get("entity_type", "")
    entity_id = body.get("entity_id", "")
    comment_text = body.get("comment", "").strip()
    parent_id = body.get("parent_id")
    if not entity_type or not entity_id or not comment_text:
        raise HTTPException(status_code=422, detail="entity_type, entity_id and comment are required")
    with conn.cursor() as cur:
        cur.execute(
            """INSERT INTO comments (entity_type, entity_id, parent_id, author, comment)
               VALUES (%s,%s,%s,%s,%s) RETURNING comment_id, created_at""",
            (entity_type, entity_id, parent_id, actor.user_ref, comment_text))
        cid, created = cur.fetchone()
        conn.commit()
    return {"created": True, "comment_id": cid, "created_at": created.isoformat(),
            "author": actor.user_ref}


@router.patch("/comments/{comment_id}/resolve")
def resolve_comment(comment_id: int, resolved: bool = True,
                    conn: psycopg.Connection = Depends(db_conn),
                    actor: Actor = Depends(get_actor)):
    with conn.cursor() as cur:
        cur.execute("UPDATE comments SET resolved=%s WHERE comment_id=%s",
                    (resolved, comment_id))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="comment not found")
        conn.commit()
    return {"resolved": resolved, "comment_id": comment_id}


@router.get("/recent-changes")
def recent_changes(limit: int = 20, offset: int = 0,
                   conn: psycopg.Connection = Depends(db_conn)):
    with conn.cursor() as cur:
        cur.execute(
            """SELECT audit_id, entity_type, entity_id, action, actor,
                      created_at, after_json->>'working_name' AS name
               FROM audit_events
               ORDER BY audit_id DESC LIMIT %s OFFSET %s""",
            (limit, offset))
        cols = [d.name for d in cur.description]
        items = []
        for r in cur.fetchall():
            row = dict(zip(cols, r))
            if row.get("created_at"):
                row["created_at"] = row["created_at"].isoformat()
            items.append(row)
    return {"count": len(items), "items": items}


@router.get("/home")
def home_data(conn: psycopg.Connection = Depends(db_conn),
              actor: Actor = Depends(get_actor)):
    """PM-oriented Home data: attention items + counts + recent changes."""
    with conn.cursor() as cur:
        # counts
        cur.execute("SELECT count(*) FROM capability_candidates WHERE ideation_disposition='ACTIVE FOR IDEATION'")
        active_candidates = cur.fetchone()[0]
        cur.execute("SELECT count(*) FROM capability_candidates WHERE is_focus")
        focus = cur.fetchone()[0]
        cur.execute("SELECT count(*) FROM source_evidence")
        evidence = cur.fetchone()[0]
        cur.execute("SELECT count(*) FROM sources")
        sources = cur.fetchone()[0]
        cur.execute("SELECT count(*) FROM milestones")
        milestones = cur.fetchone()[0]
        cur.execute("SELECT count(*) FROM customers")
        customers = cur.fetchone()[0]
        cur.execute("SELECT count(*) FROM features")
        features = cur.fetchone()[0]

        # attention items
        cur.execute("""SELECT count(*) FROM capability_candidates
                       WHERE ideation_disposition='ACTIVE FOR IDEATION'""")
        needs_review = cur.fetchone()[0]

        cur.execute("SELECT count(*) FROM comments WHERE resolved=false")
        open_comments = cur.fetchone()[0]

        # recent changes from audit
        cur.execute(
            """SELECT audit_id, entity_type, entity_id, action, actor, created_at
               FROM audit_events ORDER BY audit_id DESC LIMIT 10""")
        cols = [d.name for d in cur.description]
        recent = []
        for r in cur.fetchall():
            row = dict(zip(cols, r))
            if row.get("created_at"):
                row["created_at"] = row["created_at"].isoformat()
            recent.append(row)

    return {
        "counts": {
            "sources": sources,
            "evidence_signals": evidence,
            "active_candidates": active_candidates,
            "focus_capabilities": focus,
            "historical_baseline": 135,
            "milestones": milestones,
            "customers": customers,
            "features": features,
        },
        "attention": {
            "candidates_needing_review": needs_review,
            "open_comments": open_comments,
        },
        "recent_changes": recent,
        "app_version": settings.version,
        "app_env": settings.app_env,
    }
