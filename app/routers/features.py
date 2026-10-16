"""Features API (UAT structural update, contract §12–§15).

A Feature is a Product-managed composition of one or more Canonical
Capabilities. Capability remains Product Truth; Feature is a planning/
composition construct. Feature is NOT a Jira Epic and NOT a Source
Capability. Composition is a Product decision — nothing auto-groups
capabilities into features.

- GET    /api/features                     list (each with its capabilities)
- POST   /api/features                     create (FEAT-xxxx identity)
- GET    /api/features/{feat_id}           detail
- PATCH  /api/features/{feat_id}           optimistic version + audit
- POST   /api/features/{feat_id}/capabilities/{cap_id}    link (M:N)
- DELETE /api/features/{feat_id}/capabilities/{cap_id}    unlink
                                          (removes only the relationship —
                                           Feature and Capability survive)
"""

from fastapi import APIRouter, Depends, HTTPException
import psycopg

from ..audit import record_audit
from ..db import db_conn
from ..identity import Actor, get_actor
from ..models import FeatureCreate, FeaturePatch

router = APIRouter(prefix="/api/features", tags=["features"])

FEAT_COLS = ("feat_id, name, description, owner, status, notes, "
             "version, created_at, updated_at")


def _caps_for(cur, feat_id: str) -> list[dict]:
    cur.execute(
        """SELECT c.cap_id, c.working_name, c.strategic_category, c.moscow,
                  c.roadmap_admission, fc.added_at
           FROM feature_capabilities fc
           JOIN capabilities c ON c.cap_id = fc.cap_id
           WHERE fc.feat_id=%s ORDER BY c.cap_id""", (feat_id,))
    cols = [d.name for d in cur.description]
    return [dict(zip(cols, r)) for r in cur.fetchall()]


def _feature_dict(cur, row, cols) -> dict:
    feat = dict(zip(cols, row))
    feat["capabilities"] = _caps_for(cur, feat["feat_id"])
    # §19: Feature coverage is DERIVED from constituent capabilities — never a
    # second planning truth. Simple derived window: min/max of cap timing.
    cur.execute(
        """SELECT min(r.start_month), max(r.start_month + r.duration_months)
           FROM feature_capabilities fc
           JOIN roadmap_timing r ON r.cap_id = fc.cap_id
           WHERE fc.feat_id=%s""", (feat["feat_id"],))
    lo, hi = cur.fetchone()
    feat["derived_timing_window"] = (
        {"start_month": lo, "end_month_exclusive": hi}
        if lo is not None and hi is not None else None)
    return feat


@router.get("")
def list_features(conn: psycopg.Connection = Depends(db_conn)):
    with conn.cursor() as cur:
        cur.execute(f"SELECT {FEAT_COLS} FROM features ORDER BY feat_id")
        cols = [d.name for d in cur.description]
        rows = [_feature_dict(cur, r, cols) for r in cur.fetchall()]
    return {"count": len(rows), "items": rows}


@router.get("/{feat_id}")
def get_feature(feat_id: str, conn: psycopg.Connection = Depends(db_conn)):
    with conn.cursor() as cur:
        cur.execute(f"SELECT {FEAT_COLS} FROM features WHERE feat_id=%s",
                    (feat_id,))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404,
                                detail=f"feature {feat_id} not found")
        cols = [d.name for d in cur.description]
        return _feature_dict(cur, cur.fetchone(), cols)


@router.post("", status_code=201)
def create_feature(body: FeatureCreate,
                   conn: psycopg.Connection = Depends(db_conn),
                   actor: Actor = Depends(get_actor)):
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM features WHERE feat_id=%s", (body.feat_id,))
        if cur.rowcount:
            raise HTTPException(status_code=409,
                                detail=f"feature {body.feat_id} exists")
        data = body.model_dump()
        cols = list(data)
        cur.execute(
            f"INSERT INTO features ({', '.join(cols)}) "
            f"VALUES ({', '.join(['%s'] * len(cols))})", tuple(data.values()))
        record_audit(cur, "feature", body.feat_id, "create", actor.user_ref,
                     None, body.model_dump(mode="json"), ["feature"])
        conn.commit()
    return {"created": True, "feat_id": body.feat_id}


@router.patch("/{feat_id}")
def patch_feature(feat_id: str, body: FeaturePatch,
                  conn: psycopg.Connection = Depends(db_conn),
                  actor: Actor = Depends(get_actor)):
    provided = body.model_dump(exclude_unset=True)
    version = provided.pop("version")
    if not provided:
        raise HTTPException(status_code=400, detail="no fields to update")
    with conn.cursor() as cur:
        cur.execute(f"SELECT {FEAT_COLS} FROM features WHERE feat_id=%s",
                    (feat_id,))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404,
                                detail=f"feature {feat_id} not found")
        cols = [d.name for d in cur.description]
        before = dict(zip(cols, cur.fetchone()))
        if before["version"] != version:
            raise HTTPException(
                status_code=409,
                detail={"error": "version_conflict",
                        "current_version": before["version"],
                        "requested_version": version})
        sets = ", ".join(f"{k}=%s" for k in provided)
        cur.execute(
            f"UPDATE features SET {sets}, version=version+1, updated_at=now() "
            "WHERE feat_id=%s AND version=%s",
            (*provided.values(), feat_id, version))
        record_audit(cur, "feature", feat_id, "update", actor.user_ref,
                     {k: before[k] for k in provided},
                     dict(provided), list(provided))
        conn.commit()
    return {"updated": True, "feat_id": feat_id, "version": version + 1}


@router.delete("/{feat_id}")
def delete_feature(feat_id: str,
                  conn: psycopg.Connection = Depends(db_conn),
                  actor: Actor = Depends(get_actor)):
    """Delete a Feature. Constituent Capabilities are untouched (Feature is a
    composition view; the join rows go with it via ON DELETE CASCADE)."""
    with conn.cursor() as cur:
        cur.execute("SELECT name FROM features WHERE feat_id=%s", (feat_id,))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404,
                                detail=f"feature {feat_id} not found")
        name = cur.fetchone()[0]
        cur.execute("DELETE FROM features WHERE feat_id=%s", (feat_id,))
        record_audit(cur, "feature", feat_id, "delete", actor.user_ref,
                     {"name": name}, None, ["feature"])
        conn.commit()
    return {"deleted": True, "feat_id": feat_id,
            "note": "capabilities are untouched"}


@router.post("/{feat_id}/capabilities/{cap_id}", status_code=201)
def link_capability(feat_id: str, cap_id: str,
                    conn: psycopg.Connection = Depends(db_conn),
                    actor: Actor = Depends(get_actor)):
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM features WHERE feat_id=%s", (feat_id,))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404,
                                detail=f"feature {feat_id} not found")
        cur.execute("SELECT 1 FROM capabilities WHERE cap_id=%s", (cap_id,))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404,
                                detail=f"capability {cap_id} not found")
        cur.execute(
            """INSERT INTO feature_capabilities (feat_id, cap_id)
               VALUES (%s,%s) ON CONFLICT DO NOTHING RETURNING feat_id""",
            (feat_id, cap_id))
        if cur.rowcount == 0:
            conn.rollback()
            raise HTTPException(
                status_code=409, detail=f"link {feat_id}:{cap_id} exists")
        record_audit(cur, "feature_capabilities",
                     f"{feat_id}:{cap_id}", "create", actor.user_ref, None,
                     {"feat_id": feat_id, "cap_id": cap_id},
                     ["feature_capability_link"])
        conn.commit()
    return {"feat_id": feat_id, "cap_id": cap_id, "created": True}


@router.delete("/{feat_id}/capabilities/{cap_id}")
def unlink_capability(feat_id: str, cap_id: str,
                      conn: psycopg.Connection = Depends(db_conn),
                      actor: Actor = Depends(get_actor)):
    with conn.cursor() as cur:
        cur.execute(
            "DELETE FROM feature_capabilities "
            "WHERE feat_id=%s AND cap_id=%s", (feat_id, cap_id))
        if cur.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail=f"link {feat_id}:{cap_id} not found")
        record_audit(cur, "feature_capabilities", f"{feat_id}:{cap_id}",
                     "delete", actor.user_ref,
                     {"feat_id": feat_id, "cap_id": cap_id}, None,
                     ["feature_capability_link"])
        conn.commit()
    return {"deleted": True,
            "note": "only the relationship was removed — Feature and "
                    "Capability both survive"}
