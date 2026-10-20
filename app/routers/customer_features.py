"""Customer↔Feature M:N relationship API (Phase D).

Importance: KEY / REQUIRED / RELEVANT.
Validation: PRODUCT_HYPOTHESIS ≠ CUSTOMER_VALIDATED (§26).
"""

from fastapi import APIRouter, Depends, HTTPException
import psycopg

from ..audit import record_audit
from ..db import db_conn
from ..identity import Actor, get_actor

router = APIRouter(prefix="/api/customer-features", tags=["customer-features"])

IMPORTANCE = ("KEY", "REQUIRED", "RELEVANT")


@router.get("")
def list_customer_features(customer_id: str | None = None,
                           conn: psycopg.Connection = Depends(db_conn)):
    where, params = [], []
    if customer_id:
        where.append("cf.customer_id=%s"); params.append(customer_id)
    w = ("WHERE " + " AND ".join(where)) if where else ""
    with conn.cursor() as cur:
        cur.execute(f"""SELECT cf.customer_id, cf.feat_id, cf.importance,
                              cf.required_for_migration, cf.required_by_milestone,
                              cf.rationale, cf.validation_status, cf.customer_feedback,
                              cf.notes, cf.version, cf.created_at, cf.updated_at,
                              f.name AS feature_name, f.status AS feature_status
                       FROM customer_features cf
                       JOIN features f ON f.feat_id = cf.feat_id
                       {w} ORDER BY cf.customer_id, cf.feat_id""", params)
        cols = [d.name for d in cur.description]
        items = []
        for r in cur.fetchall():
            row = dict(zip(cols, r))
            for k in ("created_at", "updated_at"):
                if row.get(k): row[k] = row[k].isoformat()
            items.append(row)
    return {"count": len(items), "items": items}


@router.post("/{customer_id}/{feat_id}", status_code=201)
def link_customer_feature(customer_id: str, feat_id: str, body: dict = None,
                          conn: psycopg.Connection = Depends(db_conn),
                          actor: Actor = Depends(get_actor)):
    body = body or {}
    importance = body.get("importance", "REQUIRED")
    if importance not in IMPORTANCE:
        raise HTTPException(status_code=422, detail=f"importance must be one of {IMPORTANCE}")
    validation = body.get("validation_status", "PRODUCT_HYPOTHESIS")
    if validation not in ("PRODUCT_HYPOTHESIS", "CUSTOMER_VALIDATED"):
        raise HTTPException(status_code=422, detail="validation_status must be PRODUCT_HYPOTHESIS or CUSTOMER_VALIDATED")
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM customers WHERE customer_id=%s", (customer_id,))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail=f"customer {customer_id} not found")
        cur.execute("SELECT 1 FROM features WHERE feat_id=%s", (feat_id,))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail=f"feature {feat_id} not found")
        cur.execute(
            """INSERT INTO customer_features (customer_id, feat_id, importance,
                   required_for_migration, rationale, validation_status, notes)
               VALUES (%s,%s,%s,%s,%s,%s,%s)
               ON CONFLICT (customer_id, feat_id) DO NOTHING RETURNING customer_id""",
            (customer_id, feat_id, importance,
             body.get("required_for_migration", False),
             body.get("rationale"), validation, body.get("notes")))
        if cur.rowcount == 0:
            conn.rollback()
            raise HTTPException(status_code=409, detail=f"link {customer_id}:{feat_id} exists")
        record_audit(cur, "customer_feature", f"{customer_id}:{feat_id}", "create",
                     actor.user_ref, None,
                     {"customer_id": customer_id, "feat_id": feat_id, "importance": importance},
                     ["customer_feature_link"])
        conn.commit()
    return {"customer_id": customer_id, "feat_id": feat_id, "created": True}


@router.patch("/{customer_id}/{feat_id}")
def patch_customer_feature(customer_id: str, feat_id: str, body: dict,
                           conn: psycopg.Connection = Depends(db_conn),
                           actor: Actor = Depends(get_actor)):
    provided = {k: v for k, v in body.items() if k != "version"}
    version = body.get("version")
    if not version:
        raise HTTPException(status_code=400, detail="version required")
    if provided.get("importance") and provided["importance"] not in IMPORTANCE:
        raise HTTPException(status_code=422, detail=f"importance must be one of {IMPORTANCE}")
    with conn.cursor() as cur:
        cur.execute("""SELECT version FROM customer_features
                       WHERE customer_id=%s AND feat_id=%s""", (customer_id, feat_id))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="relationship not found")
        db_version = cur.fetchone()[0]
        if db_version != version:
            raise HTTPException(status_code=409, detail={
                "error": "version_conflict", "current_version": db_version, "requested_version": version})
        sets = ", ".join(f"{k}=%s" for k in provided)
        cur.execute(f"""UPDATE customer_features SET {sets}, version=version+1, updated_at=now()
                       WHERE customer_id=%s AND feat_id=%s AND version=%s""",
                    (*provided.values(), customer_id, feat_id, version))
        record_audit(cur, "customer_feature", f"{customer_id}:{feat_id}", "update",
                     actor.user_ref, {}, dict(provided), list(provided))
        conn.commit()
    return {"updated": True, "customer_id": customer_id, "feat_id": feat_id, "version": version + 1}


@router.delete("/{customer_id}/{feat_id}")
def unlink_customer_feature(customer_id: str, feat_id: str,
                            conn: psycopg.Connection = Depends(db_conn),
                            actor: Actor = Depends(get_actor)):
    with conn.cursor() as cur:
        cur.execute("DELETE FROM customer_features WHERE customer_id=%s AND feat_id=%s",
                    (customer_id, feat_id))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="relationship not found")
        record_audit(cur, "customer_feature", f"{customer_id}:{feat_id}", "delete",
                     actor.user_ref, {"customer_id": customer_id, "feat_id": feat_id}, None,
                     ["customer_feature_link"])
        conn.commit()
    return {"deleted": True, "customer_id": customer_id, "feat_id": feat_id}
