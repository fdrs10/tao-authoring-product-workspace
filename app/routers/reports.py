"""Reports / Deliverables API (FINAL STRUCTURAL STEP).

Model: Application Product Truth → Report Contract → Generated Report.
Generating a report NEVER mutates Product Truth — it only records a snapshot
generation (report_generations).

- GET  /api/reports                          contracts + data readiness/section states
- GET  /api/reports/{rid}/preview            print-friendly generated HTML (not persisted)
- GET  /api/reports/{rid}/preview?customer_id=…  D5 per-customer preview
- POST /api/reports/{rid}/generate           record a generation (snapshot) — optional
                                             customer_id / customer_ids params
- GET  /api/reports/{rid}/generations        generation history (version metadata)
"""

import psycopg
import psycopg.types.json
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse

from .. import reports as R
from ..audit import record_audit
from ..config import settings
from ..db import db_conn
from ..identity import Actor, get_actor

router = APIRouter(prefix="/api/reports", tags=["reports"])


def _utcnow():
    import datetime as _dt
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def _section_states(report_id: str, sections: dict):
    """Deterministic ordering per contract + completeness counters."""
    order = R.SECTIONS[report_id]
    return [(title, *sections[title]) for title in order if title in sections]


def _build(cur, report_id: str, customer=None, customer_ids=None):
    data = R.Data(cur)
    caps = data.capabilities()
    timing = data.timing()
    milestones = data.milestones()
    params = {}
    if report_id == "D1":
        sections = R.d1_sections(data, caps)
    elif report_id == "D2":
        sections = R.d2_sections(data, caps)
    elif report_id == "D3":
        sections = R.d3_sections(data, caps, timing)
    elif report_id == "D4":
        sections = R.d4_sections(data, caps, timing, milestones)
    elif report_id == "D5":
        if not customer:
            raise HTTPException(status_code=400, detail={
                "error": "customer_required",
                "message": "D5 generates one report per governed customer; pass customer_id."})
        cust = data.q("SELECT * FROM customers WHERE customer_id=%s", (customer,))
        if not cust:
            raise HTTPException(status_code=404, detail={
                "error": "customer_not_found", "customer_id": customer,
                "message": "governed customer records only — customers are never invented"})
        customer = cust[0]
        sections = R.d5_sections(data, caps, timing, milestones, customer)
        params = {"customer_id": customer["customer_id"]}
    else:
        raise HTTPException(status_code=404, detail=f"unknown report {report_id}")
    pairs = _section_states(report_id, sections)
    available = sum(1 for _, st, _ in pairs if st == "AVAILABLE")
    return pairs, available, params


@router.get("")
def list_reports(conn: psycopg.Connection = Depends(db_conn)):
    out = []
    for rid in ("D1", "D2", "D3", "D4", "D5"):
        if rid == "D5":
            # one report per governed customer — summary without a customer
            with conn.cursor() as cur:
                cur.execute("SELECT count(*) FROM customers")
                customers = cur.fetchone()[0]
            out.append({"report_id": "D5", "name": R.REPORT_NAMES["D5"],
                        "target_delivery": R.TARGET_DATES["D5"],
                        "consumes": R.CONSUMES["D5"],
                        "sections_total": len(R.SECTIONS["D5"]),
                        "sections_available": 0,
                        "status": "INCOMPLETE",
                        "note": "select a governed customer to generate",
                        "governed_customers": customers,
                        "last_generated": None, "last_version": 0, "last_actor": None})
            continue
        with conn.cursor() as cur:
            pairs, available, _ = _build(cur, rid)
        total = len(R.SECTIONS[rid])
        last = conn.cursor()
        last.execute(
            """SELECT version, generated_at, actor FROM report_generations
               WHERE report_id=%s ORDER BY version DESC LIMIT 1""", (rid,))
        gen = last.fetchone()
        out.append({
            "report_id": rid,
            "name": R.REPORT_NAMES[rid],
            "target_delivery": R.TARGET_DATES[rid],
            "consumes": R.CONSUMES[rid],
            "sections_total": total,
            "sections_available": available,
            "status": "AVAILABLE" if available == total else "INCOMPLETE",
            "last_generated": gen[1].isoformat() if gen else None,
            "last_version": gen[0] if gen else 0,
            "last_actor": gen[2] if gen else None,
        })
    return {"count": len(out), "pilot_intended_customers": R.PILOT_INTENDED_CUSTOMERS,
            "items": out}


@router.get("/{rid}/preview", response_class=HTMLResponse)
def preview_report(rid: str, customer_id: str | None = None,
                   conn: psycopg.Connection = Depends(db_conn),
                   actor: Actor = Depends(get_actor)):
    with conn.cursor() as cur:
        pairs, available, params = _build(cur, rid, customer=customer_id)
    if customer_id:
        params["customer_id"] = customer_id
    html = R.render_document(rid, pairs, version=0,
                             generated_at=_utcnow() + " (preview — not a recorded generation)",
                             actor=actor.user_ref, params=params)
    return HTMLResponse(html)


def _snapshot_counts(cur):
    cur.execute("""SELECT (SELECT count(*) FROM capabilities),
                          (SELECT count(*) FROM source_capabilities),
                          (SELECT count(*) FROM milestones),
                          (SELECT count(*) FROM customers),
                          (SELECT coalesce(max(version),0) FROM capabilities)""")
    return dict(zip(["capabilities", "source_capabilities", "milestones",
                     "customers", "capability_max_version"], cur.fetchone()))


@router.post("/{rid}/generate")
def generate_report(rid: str, body: dict | None = None,
                    conn: psycopg.Connection = Depends(db_conn),
                    actor: Actor = Depends(get_actor)):
    body = body or {}
    customer_id = body.get("customer_id")
    customer_ids = body.get("customer_ids")
    pilot = rid == "PILOT" or body.get("pilot") is True

    counts = _snapshot_counts(conn.cursor())

    if pilot or rid == "PILOT":
        selected = customer_ids or []
        with conn.cursor() as cur:
            cur.execute("SELECT customer_id FROM customers")
            governed = {r[0] for r in cur.fetchall()}
        unknown = [c for c in selected if c not in governed]
        if unknown:
            raise HTTPException(status_code=422, detail={
                "error": "unknown_customers", "customers": unknown,
                "message": "Pilot Set uses selected governed customers only — none are invented."})
        if not selected:
            raise HTTPException(status_code=400, detail={"error": "no_customers_selected"})
        docs = []
        with conn.cursor() as cur:
            data = R.Data(cur)
            caps = data.capabilities()
            timing = data.timing()
            milestones = data.milestones()
            for cid in selected:
                cur.execute("SELECT * FROM customers WHERE customer_id=%s", (cid,))
                cols = [d.name for d in cur.description]
                cust = dict(zip(cols, cur.fetchone()))
                sections = R.d5_sections(data, caps, timing, milestones, cust)
                pairs = _section_states("D5", sections)
                docs.append((cid, R.render_document("D5", pairs, 0, _utcnow(),
                                                    actor.user_ref, {"customer_id": cid})))
        cur = conn.cursor()
        cur.execute("SELECT COALESCE(MAX(version), 0) + 1 FROM report_generations WHERE report_id='PILOT'")
        version = cur.fetchone()[0]
        cur.execute(
            """INSERT INTO report_generations (report_id, report_type, version, actor, params, source_snapshot, html)
               VALUES ('PILOT', 'pilot-set', %s, %s, %s, %s, %s)""",
            (version, actor.user_ref,
             psycopg.types.json.Json({"customer_ids": selected}),
             psycopg.types.json.Json(counts),
             psycopg.types.json.Json(docs)))
        record_audit(cur, "report_generation", "PILOT", "create", actor.user_ref,
                     None, {"customer_ids": selected}, ["report_generation"])
        conn.commit()
        return {"generated": True, "report_id": "PILOT", "report_type": "pilot-set",
                "version": version,
                "documents": [{"customer_id": cid, "html": html} for cid, html in docs]}

    if rid not in R.SECTIONS:
        raise HTTPException(status_code=404, detail=f"unknown report {rid}")
    with conn.cursor() as cur:
        pairs, available, params = _build(cur, rid, customer=customer_id)
    if customer_id:
        params["customer_id"] = customer_id
    html = R.render_document(rid, pairs, 0, _utcnow(), actor.user_ref, params)
    with conn.cursor() as cur:
        cur.execute("SELECT COALESCE(MAX(version), 0) + 1 FROM report_generations WHERE report_id=%s", (rid,))
        version = cur.fetchone()[0]
        cur.execute(
            """INSERT INTO report_generations (report_id, report_type, version, actor, params, source_snapshot, html)
               VALUES (%s, 'contract', %s, %s, %s, %s, %s)""",
            (rid, version, actor.user_ref,
             psycopg.types.json.Json(params),
             psycopg.types.json.Json(counts),
             html))
        record_audit(cur, "report_generation", rid, "create", actor.user_ref,
                     None, {"version": version}, ["report_generation"])
        conn.commit()
    return {"generated": True, "report_id": rid, "version": version, "html": html,
            "sections_available": available, "sections_total": len(R.SECTIONS[rid])}


@router.get("/{rid}/generations")
def generation_history(rid: str, conn: psycopg.Connection = Depends(db_conn)):
    with conn.cursor() as cur:
        cur.execute("""SELECT version, report_type, actor, generated_at, params, source_snapshot
                       FROM report_generations WHERE report_id=%s ORDER BY version DESC""", (rid,))
        cols = [d.name for d in cur.description]
        rows = [dict(zip(cols, r)) for r in cur.fetchall()]
    for row in rows:
        row["generated_at"] = row["generated_at"].isoformat()
    return {"count": len(rows), "items": rows}
