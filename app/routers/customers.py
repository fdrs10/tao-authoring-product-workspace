"""Customers API (Phase 3).

Model + CRUD complete (D3: schema/API ready), dataset intentionally EMPTY
until Product supplies the governed customer list. Never invent customers.
earliest_milestone_interval is a milestone interval like "M3 -> M4"; no
TS1/TS2/TS3 codes (§40) — format lightly validated here, stricter
validation once real milestones exist (D2).
"""

from fastapi import APIRouter, Body, Depends, HTTPException
import psycopg

from ..audit import record_audit
from ..db import db_conn
from ..identity import Actor, get_actor
from ..models import CustomerCreate, CustomerPatch

router = APIRouter(prefix="/api/customers", tags=["customers"])

CUST_COLS = """
  customer_id, name, current_use, min_functionality_today,
  min_functionality_studio, desired_outcome, value_opportunity, blockers,
  earliest_milestone_interval, validation_status, notes, version
"""


def _check_interval(v: str | None) -> None:
    if v is None:
        return
    up = " ".join(v.upper().split())
    if up.startswith("TS") and any(up.startswith(f"TS{i}") for i in range(1, 10)):
        raise HTTPException(
            status_code=422,
            detail="earliest_milestone_interval must be a milestone interval "
                   "(e.g. 'M3 -> M4'), not TS transition codes (§40)")


@router.get("")
def list_customers(conn: psycopg.Connection = Depends(db_conn)):
    sql = f"""
      SELECT {CUST_COLS},
        (SELECT count(*) FROM customer_capabilities cc
          WHERE cc.customer_id=c.customer_id) AS required_capability_count
      FROM customers c ORDER BY c.customer_id
    """
    with conn.cursor() as cur:
        cur.execute(sql)
        cols = [d.name for d in cur.description]
        rows = [dict(zip(cols, r)) for r in cur.fetchall()]
    return {"count": len(rows), "items": rows}


@router.get("/{customer_id}")
def get_customer(customer_id: str,
                 conn: psycopg.Connection = Depends(db_conn)):
    with conn.cursor() as cur:
        cur.execute(f"SELECT {CUST_COLS} FROM customers WHERE customer_id=%s",
                    (customer_id,))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404,
                                detail=f"customer {customer_id} not found")
        cols = [d.name for d in cur.description]
        cust = dict(zip(cols, cur.fetchone()))
        cur.execute(
            """SELECT cc.cap_id, c.working_name FROM customer_capabilities cc
               JOIN capabilities c ON c.cap_id=cc.cap_id
               WHERE cc.customer_id=%s ORDER BY cc.cap_id""", (customer_id,))
        cust["required_capabilities"] = [
            dict(zip([d.name for d in cur.description], r))
            for r in cur.fetchall()]
    return cust


@router.post("", status_code=201)
def create_customer(body: CustomerCreate,
                    conn: psycopg.Connection = Depends(db_conn),
                    actor: Actor = Depends(get_actor)):
    _check_interval(body.earliest_milestone_interval)
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM customers WHERE customer_id=%s",
                    (body.customer_id,))
        if cur.rowcount:
            raise HTTPException(status_code=409,
                                detail=f"customer {body.customer_id} exists")
        data = body.model_dump()
        cols = list(data)
        cur.execute(
            f"INSERT INTO customers ({', '.join(cols)}) "
            f"VALUES ({', '.join(['%s'] * len(cols))})",
            tuple(data.values()))
        record_audit(cur, "customer", body.customer_id, "create",
                     actor.user_ref, None, body.model_dump(mode="json"),
                     ["customer"])
        conn.commit()
    return {"created": True, "customer_id": body.customer_id}


@router.patch("/{customer_id}")
def patch_customer(customer_id: str, body: CustomerPatch,
                   conn: psycopg.Connection = Depends(db_conn),
                   actor: Actor = Depends(get_actor)):
    provided = body.model_dump(exclude_unset=True)
    version = provided.pop("version")
    if not provided:
        raise HTTPException(status_code=400, detail="no fields to update")
    _check_interval(provided.get("earliest_milestone_interval"))
    with conn.cursor() as cur:
        cur.execute(f"SELECT {CUST_COLS} FROM customers WHERE customer_id=%s",
                    (customer_id,))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404,
                                detail=f"customer {customer_id} not found")
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
                f"UPDATE customers SET {sets}, version=version+1 "
                "WHERE customer_id=%s AND version=%s",
                (*provided.values(), customer_id, version))
            record_audit(cur, "customer", customer_id, "update",
                         actor.user_ref,
                         {k: before[k] for k in provided},
                         dict(provided), list(provided))
    except HTTPException:
        conn.rollback()
        raise
    else:
        conn.commit()
    return {"updated": True, "customer_id": customer_id,
            "version": version + 1}


@router.post("/{customer_id}/capabilities", status_code=201)
def link_customer_capability(customer_id: str,
                             cap_id: str = Body(embed=True, min_length=1),
                             conn: psycopg.Connection = Depends(db_conn),
                             actor: Actor = Depends(get_actor)):
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM customers WHERE customer_id=%s",
                    (customer_id,))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404,
                                detail=f"customer {customer_id} not found")
        cur.execute("SELECT 1 FROM capabilities WHERE cap_id=%s", (cap_id,))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404,
                                detail=f"capability {cap_id} not found")
        cur.execute(
            """INSERT INTO customer_capabilities (customer_id, cap_id)
               VALUES (%s,%s) ON CONFLICT DO NOTHING RETURNING customer_id""",
            (customer_id, cap_id))
        if cur.rowcount == 0:
            conn.rollback()
            raise HTTPException(status_code=409,
                                detail=f"link {customer_id}:{cap_id} exists")
        record_audit(cur, "customer_capabilities", f"{customer_id}:{cap_id}",
                     "create", actor.user_ref, None,
                     {"customer_id": customer_id, "cap_id": cap_id},
                     ["customer_capability_link"])
        conn.commit()
    return {"customer_id": customer_id, "cap_id": cap_id, "created": True}


@router.delete("/{customer_id}/capabilities/{cap_id}")
def unlink_customer_capability(customer_id: str, cap_id: str,
                               conn: psycopg.Connection = Depends(db_conn),
                               actor: Actor = Depends(get_actor)):
    with conn.cursor() as cur:
        cur.execute(
            "DELETE FROM customer_capabilities "
            "WHERE customer_id=%s AND cap_id=%s", (customer_id, cap_id))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404,
                                detail=f"link {customer_id}:{cap_id} not found")
        record_audit(cur, "customer_capabilities", f"{customer_id}:{cap_id}",
                     "delete", actor.user_ref,
                     {"customer_id": customer_id, "cap_id": cap_id}, None,
                     ["customer_capability_link"])
        conn.commit()
    return {"deleted": True}
