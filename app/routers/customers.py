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
  earliest_milestone_interval, validation_status, notes, version,
  current_environment, relevant_markets, proposed_migration_window,
  customer_dependencies, assumptions, exceptions, customer_feedback
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
        for row in rows:
            row["migration_plan"] = _migration_plan(cur, row)
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
        cust["migration_plan"] = _migration_plan(cur, cust)
    return cust


# ---- Customer Migration Plan derivation (FINAL UAT EVOLUTION §10/§14) ------
# The plan CONSUMES Product Roadmap truth — it never stores a second timing.
# Readiness states are explainable from the underlying data (§14), no scores.

def _migration_plan(cur, cust: dict) -> dict:
    """Derive the Customer Migration Plan view from canonical truth:
    required capabilities + their Roadmap timing + availability by the
    proposed interval's start milestone + shared milestones."""
    cur.execute("SELECT milestone_id, name, position_month FROM milestones "
                "ORDER BY position_month NULLS LAST, milestone_id")
    milestones = [dict(zip([d.name for d in cur.description], r))
                  for r in cur.fetchall()]
    by_id = {m["milestone_id"]: m for m in milestones}

    interval = (cust.get("earliest_milestone_interval") or "").upper()
    start_mid = interval.split("->")[0].strip() if "->" in interval else None
    start_pos = by_id[start_mid]["position_month"] if start_mid in by_id else None

    cur.execute(
        """SELECT c.cap_id, c.working_name, c.roadmap_admission,
                  r.start_month, r.duration_months
           FROM customer_capabilities cc
           JOIN capabilities c ON c.cap_id = cc.cap_id
           LEFT JOIN roadmap_timing r ON r.cap_id = c.cap_id
           WHERE cc.customer_id=%s ORDER BY c.cap_id""", (cust["customer_id"],))
    cols = [d.name for d in cur.description]
    required = []
    for r in cur.fetchall():
        row = dict(zip(cols, r))
        end = (row["start_month"] + (row["duration_months"] or 0)
               if row["start_month"] is not None else None)
        row["roadmap_end_month"] = end
        row["available_by_interval_start"] = (
            True if start_pos is None else (end is not None and end <= start_pos))
        row["dependency"] = (
            "available" if row["available_by_interval_start"]
            else ("untimed — dependent on Roadmap planning" if end is None
                  else f"Roadmap timing completes month {end}, after the "
                       f"proposed interval start (month {start_pos})"))
        # features composed around this capability (composition only)
        cur.execute(
            """SELECT f.feat_id, f.name FROM feature_capabilities fc
               JOIN features f ON f.feat_id = fc.feat_id
               WHERE fc.cap_id=%s ORDER BY f.feat_id""", (row["cap_id"],))
        row["features"] = [dict(zip([d.name for d in cur.description], fr))
                           for fr in cur.fetchall()]
        required.append(row)

    blocked = [c for c in required if not c["available_by_interval_start"]]
    validated = (cust.get("validation_status") or "") in (
        "Customer validated", "Migration committed")
    if not cust.get("earliest_milestone_interval"):
        readiness = "PRODUCT DECISION REQUIRED"
        reason = "no proposed milestone interval yet — Product must propose one"
    elif blocked:
        readiness = "BLOCKED BY ROADMAP CAPABILITY"
        reason = (f"{len(blocked)} of {len(required)} required capabilities are "
                  f"not available by the proposed interval start")
    elif not validated:
        readiness = "CUSTOMER VALIDATION REQUIRED"
        reason = "all required capabilities available; customer validation status is not yet committed"
    else:
        readiness = "READY FOR PROPOSED INTERVAL"
        reason = "all required capabilities available by the proposed interval start and customer validated"
    if (cust.get("validation_status") or "").lower().startswith("migration exception"):
        readiness, reason = "MIGRATION EXCEPTION", "recorded as a migration exception by Product"

    return {
        "milestones": milestones,
        "proposed_interval": cust.get("earliest_milestone_interval"),
        "interval_start_milestone": start_mid,
        "required_capabilities": required,
        "available_by_interval_start": len(required) - len(blocked),
        "blocked_count": len(blocked),
        "blocked_capability_ids": [c["cap_id"] for c in blocked],
        "readiness_status": readiness,
        "readiness_reason": reason,
    }


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


@router.get("/{customer_id}/migration-intervals")
def get_migration_intervals(customer_id: str,
                            conn: psycopg.Connection = Depends(db_conn)):
    """Per-interval Customer Migration Plan over shared M1–M6."""
    with conn.cursor() as cur:
        cur.execute("""SELECT milestone_id, name, milestone_date, position_month
                       FROM milestones ORDER BY position_month NULLS LAST""")
        milestones = [dict(zip([d.name for d in cur.description], r))
                      for r in cur.fetchall()]
        cur.execute("""SELECT cc.cap_id, c.working_name, c.roadmap_admission,
                              r.start_month, r.duration_months
                       FROM customer_capabilities cc
                       JOIN capabilities c ON c.cap_id = cc.cap_id
                       LEFT JOIN roadmap_timing r ON r.cap_id = cc.cap_id
                       WHERE cc.customer_id=%s ORDER BY c.cap_id""", (customer_id,))
        req_caps = [dict(zip([d.name for d in cur.description], r))
                    for r in cur.fetchall()]
        cur.execute("SELECT * FROM customers WHERE customer_id=%s", (customer_id,))
        cust_cols = [d.name for d in cur.description]
        cust_row = cur.fetchone()
        cust = dict(zip(cust_cols, cust_row)) if cust_row else {}
        interval_str = cust.get("earliest_milestone_interval") or ""
        start_mid = interval_str.split("->")[0].strip() if "->" in interval_str else None

    intervals = []
    sorted_ms = [m for m in milestones if m["position_month"] is not None]
    sorted_ms.sort(key=lambda m: m["position_month"])
    prev = None
    for m in sorted_ms:
        if prev is not None:
            intervals.append({"from": prev["milestone_id"], "to": m["milestone_id"],
                              "from_pos": prev["position_month"], "to_pos": m["position_month"],
                              "from_name": prev["name"], "to_name": m["name"]})
        elif m["position_month"] > 0:
            intervals.append({"from": "START", "to": m["milestone_id"],
                              "from_pos": 0, "to_pos": m["position_month"],
                              "from_name": "Start", "to_name": m["name"]})
        prev = m
    if sorted_ms:
        last = sorted_ms[-1]
        intervals.append({"from": last["milestone_id"], "to": "POST_EOL",
                          "from_pos": last["position_month"], "to_pos": 27,
                          "from_name": last["name"], "to_name": "Post-EOL"})

    result = []
    for iv in intervals:
        start = iv["to_pos"]  # capabilities must be available by END of interval
        available = [c for c in req_caps
                     if c["start_month"] is not None
                     and c["start_month"] + (c["duration_months"] or 0) <= start]
        blocked = [c for c in req_caps if c not in available]
        # conflict: required but roadmap delivers later than this interval
        roadmap_blockers = [c for c in blocked if c["start_month"] is not None]
        customer_blockers = [c for c in blocked if c["start_month"] is None]
        result.append({
            "from_milestone": iv["from"], "to_milestone": iv["to"],
            "from_pos": iv["from_pos"], "to_pos": iv["to_pos"],
            "available_count": len(available),
            "blocked_count": len(blocked),
            "available": [{"cap_id": c["cap_id"], "name": c["working_name"]} for c in available],
            "blocked": [{"cap_id": c["cap_id"], "name": c["working_name"],
                         "roadmap_end": c["start_month"] + (c["duration_months"] or 0) if c["start_month"] is not None else None,
                         "type": "PRODUCT_ROADMAP_BLOCKER" if c["start_month"] is not None else "CUSTOMER_BLOCKER",
                         "detail": ("Roadmap timing completes month " + str(c["start_month"] + (c["duration_months"] or 0)) +
                                    ", after this interval ends (month " + str(start) + ")")
                                    if c["start_month"] is not None else "untimed"} for c in blocked],
        })
    return {"customer_id": customer_id, "intervals": result}
