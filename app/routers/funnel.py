"""Source-analysis funnel API (CONTROLLED OPERATION — ingestion/funnel).

- GET  /api/funnel                     governed funnel counts (Sources → Evidence → Candidates → Focus)
- GET  /api/evidence                   426-signal evidence universe (filters: source, mexcbt, q, disposition)
- GET  /api/candidates                 candidate population (filters: focus, mexcbt, market, disposition, q)
- PATCH /api/candidates/{id}           ideation disposition + rationale (optimistic version, actor, audit)
- POST /api/candidates/{id}/promote    promote analysed evidence to a new Capability Candidate
                                       (evidence_id + rationale required; lineage preserved; audit)

Promotion/decisions are Product actions: never silent, always audited.
"""

from fastapi import APIRouter, Depends, HTTPException
import psycopg

from ..audit import record_audit
from ..db import db_conn
from ..identity import Actor, get_actor
from ..models import BaseModel, ConfigDict, Field

router = APIRouter(prefix="/api", tags=["funnel"])

DISPOSITIONS = ("ACTIVE FOR IDEATION", "NOT SELECTED FOR IDEATION")


class CandidatePatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: int = Field(ge=1)
    ideation_disposition: str | None = None
    rationale: str = Field(min_length=5)

    def validate(self) -> list[str]:
        errs = []
        if self.ideation_disposition is not None and self.ideation_disposition not in DISPOSITIONS:
            errs.append(f"ideation_disposition must be one of {DISPOSITIONS}")
        return errs


class PromoteBody(BaseModel):
    model_config = ConfigDict(extra="forbid")

    evidence_id: str = Field(min_length=1)
    name: str = Field(min_length=1, max_length=300)
    rationale: str = Field(min_length=5)
    markets: list[str] | None = None


@router.get("/funnel")
def funnel(conn: psycopg.Connection = Depends(db_conn)):
    with conn.cursor() as cur:
        counts = {}
        for key, sql in [
            ("sources", "SELECT count(*) FROM sources"),
            ("evidence_signals", "SELECT count(*) FROM source_evidence"),
            ("capability_candidates",
             "SELECT count(*) FROM capability_candidates WHERE ideation_disposition='ACTIVE FOR IDEATION'"),
            ("focus_capabilities",
             "SELECT count(*) FROM capability_candidates WHERE is_focus"),
            ("historical_baseline",
             "SELECT count(*) FROM capabilities WHERE population='HISTORICAL_BASELINE_V1'"),
        ]:
            cur.execute(sql)
            counts[key] = cur.fetchone()[0]
    return {"funnel": counts,
            "flow": ["Sources", "Evidence Signals", "Capability Candidates", "Focus Capabilities"]}


@router.get("/evidence")
def list_evidence(conn: psycopg.Connection = Depends(db_conn),
                  source: str | None = None, mexcbt: str | None = None,
                  scope: str | None = None, q: str | None = None,
                  limit: int = 500, offset: int = 0):
    where, params = [], []
    if source:
        where.append("source_id=%s"); params.append(source)
    if mexcbt:
        where.append("mexcbt_relevance ILIKE %s"); params.append(f"%{mexcbt}%")
    if scope:
        where.append("authoring_scope ILIKE %s"); params.append(f"%{scope}%")
    if q:
        where.append("(signal_name ILIKE %s OR full_description ILIKE %s)")
        params.extend([f"%{q}%", f"%{q}%"])
    w = ("WHERE " + " AND ".join(where)) if where else ""
    with conn.cursor() as cur:
        cur.execute(f"SELECT count(*) FROM source_evidence {w}", params)
        total = cur.fetchone()[0]
        cur.execute(f"""SELECT * FROM source_evidence {w}
                        ORDER BY evidence_id LIMIT %s OFFSET %s""",
                    (*params, limit, offset))
        cols = [d.name for d in cur.description]
        items = [dict(zip(cols, r)) for r in cur.fetchall()]
    return {"count": total, "items": items}


@router.get("/candidates")
def list_candidates(conn: psycopg.Connection = Depends(db_conn),
                    focus: str | None = None, mexcbt_only: str | None = None,
                    market: str | None = None, disposition: str | None = None,
                    q: str | None = None):
    where, params = [], []
    if focus == "yes":
        where.append("is_focus")
    elif focus == "no":
        where.append("NOT is_focus")
    if disposition:
        where.append("ideation_disposition=%s"); params.append(disposition)
    if market:
        where.append("markets ILIKE %s"); params.append(f"%{market}%")
    if mexcbt_only:
        where.append("mexcbt_signals > 0")
    if q:
        where.append("name ILIKE %s"); params.append(f"%{q}%")
    w = ("WHERE " + " AND ".join(where)) if where else ""
    with conn.cursor() as cur:
        cur.execute(f"SELECT count(*) FROM capability_candidates {w}", params)
        total = cur.fetchone()[0]
        cur.execute(f"""SELECT candidate_id, name, COALESCE(cap_id, 'CAND-' || candidate_id) AS cap_id, markets, signals, owner, review_requested,
               source_ids, evidence_strength, cross_market_leverage, strategy_alignment,
               mexcbt_signals, package_status, is_focus, focus_markets,
               ideation_disposition, disposition_rationale, promotion_rationale,
               cap_id, version
               FROM capability_candidates {w} ORDER BY candidate_id""", params)
        cols = [d.name for d in cur.description]
        items = [dict(zip(cols, r)) for r in cur.fetchall()]
    return {"count": total, "items": items}


@router.get("/candidates/{candidate_id}")
def get_candidate(candidate_id: str, conn: psycopg.Connection = Depends(db_conn)):
    with conn.cursor() as cur:
        cur.execute("""SELECT candidate_id, name, COALESCE(cap_id, 'CAND-' || candidate_id) AS cap_id, markets, signals, owner, review_requested,
               source_ids, evidence_strength, cross_market_leverage, strategy_alignment,
               mexcbt_signals, package_status, is_focus, focus_markets,
               ideation_disposition, disposition_rationale, promotion_rationale,
               cap_id, version, enrichment
               FROM capability_candidates WHERE candidate_id=%s""", (candidate_id,))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404,
                                detail=f"candidate {candidate_id} not found")
        cols = [d.name for d in cur.description]
        row = dict(zip(cols, cur.fetchone()))
        cur.execute("""SELECT j.jira_key, j.summary, j.status, j.target_release, j.jira_url
                       FROM capability_jira cj JOIN jira_tickets j ON j.jira_key = cj.jira_key
                       WHERE cj.cap_id=%s ORDER BY j.jira_key""", (row["cap_id"],))
        row["jira"] = [dict(zip([d.name for d in cur.description], r)) for r in cur.fetchall()]
        cur.execute("""SELECT cap_id, description FROM capabilities WHERE cap_id=%s""",
                    (row["cap_id"],))
        capr = cur.fetchone()
        row["capability_description"] = capr[1] if capr else None
    return row


@router.get("/jira-coverage")
def jira_coverage(conn: psycopg.Connection = Depends(db_conn)):
    with conn.cursor() as cur:
        cur.execute("""SELECT jira_key, summary, issue_type, status, target_release,
                              jira_url, coverage_class, coverage_note
                       FROM jira_tickets ORDER BY jira_key""")
        cols = [d.name for d in cur.description]
        items = [dict(zip(cols, r)) for r in cur.fetchall()]
    counts = {}
    for i in items:
        counts[i["coverage_class"]] = counts.get(i["coverage_class"], 0) + 1
    return {"count": len(items), "coverage_counts": counts, "items": items}


@router.patch("/candidates/{candidate_id}")
def patch_candidate(candidate_id: str, body: CandidatePatch,
                    conn: psycopg.Connection = Depends(db_conn),
                    actor: Actor = Depends(get_actor)):
    errs = body.validate()
    if errs:
        raise HTTPException(status_code=422, detail=errs)
    provided = {}
    if body.ideation_disposition is not None:
        provided["ideation_disposition"] = body.ideation_disposition
        provided["disposition_rationale"] = body.rationale
    else:
        provided["disposition_rationale"] = body.rationale
    with conn.cursor() as cur:
        cur.execute("""SELECT version, ideation_disposition FROM capability_candidates
                       WHERE candidate_id=%s""", (candidate_id,))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404,
                                detail=f"candidate {candidate_id} not found")
        before_version, before_disposition = cur.fetchone()
        if before_version != body.version:
            raise HTTPException(status_code=409, detail={
                "error": "version_conflict", "current_version": before_version,
                "requested_version": body.version})
        sets = ", ".join(f"{k}=%s" for k in provided)
        cur.execute(f"""UPDATE capability_candidates SET {sets},
                        version=version+1, updated_at=now() WHERE candidate_id=%s
                        AND version=%s""",
                    (*provided.values(), candidate_id, body.version))
        if cur.rowcount == 0:
            raise HTTPException(status_code=409, detail={"error": "version_conflict"})
        record_audit(cur, "capability_candidate", candidate_id, "update",
                     actor.user_ref,
                     {"ideation_disposition": before_disposition, "version": before_version},
                     {**provided, "version": before_version + 1},
                     list(provided))
        conn.commit()
    return {"updated": True, "candidate_id": candidate_id,
            "version": before_version + 1}


@router.post("/candidates/{candidate_id}/promote", status_code=201)
def promote_evidence(candidate_id: str, body: PromoteBody,
                     conn: psycopg.Connection = Depends(db_conn),
                     actor: Actor = Depends(get_actor)):
    """Promote analysed evidence to a NEW Capability Candidate (§8).

    The promoted candidate joins the active population with full lineage back
    to the original Source Evidence. Rationale + actor + audit required.
    """
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM capability_candidates WHERE candidate_id=%s",
                    (candidate_id,))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404,
                                detail=f"candidate {candidate_id} not found")
        cur.execute("""SELECT source_id, signal_name, full_description, strategic_category
                       FROM source_evidence WHERE evidence_id=%s""", (body.evidence_id,))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404,
                                detail={"error": "evidence_not_found",
                                        "evidence_id": body.evidence_id})
        src_id, signal_name, full_description, strat_cat = cur.fetchone()
        # new candidate id = max family number + 1 (governed sequence Fxx)
        cur.execute("SELECT candidate_id FROM capability_candidates "
                    "WHERE candidate_id ~ '^F[0-9]+$' ORDER BY length(candidate_id) DESC, candidate_id DESC LIMIT 1")
        last = cur.fetchone()
        next_num = (int(last[0][1:]) + 1) if last else 1
        new_id = f"F{next_num:02d}"
        cap_id = f"CAND-{new_id}"
        cur.execute(
            """INSERT INTO capability_candidates (candidate_id, name, markets, signals,
                 independent_sources, source_ids, evidence_strength,
                 cross_market_leverage, strategy_alignment, mexcbt_signals,
                 package_status, is_focus, ideation_disposition,
                 promotion_rationale, cap_id)
               VALUES (%s,%s,%s,1,1,%s,'PROMOTED','TO_REVIEW','PROMOTED_FROM_EVIDENCE',
                       0,'PROMOTED · PRODUCT CONFIRMATION REQUIRED',false,
                       'ACTIVE FOR IDEATION',%s,%s)""",
            (new_id, body.name,
             ", ".join(body.markets) if body.markets else src_id,
             src_id, body.rationale, cap_id))
        cur.execute(
            """INSERT INTO capabilities (cap_id, working_name, description,
                 strategic_category, roadmap_admission, notes, extraction_origin,
                 population, review_status)
               VALUES (%s,%s,%s,'Awaiting Product data',NULL,NULL,'AI_ABSTRACTED',
                       'SOURCE_ANALYSIS_CANDIDATE',
                       'PROMOTED · PRODUCT CONFIRMATION REQUIRED')
               ON CONFLICT (cap_id) DO NOTHING""",
            (cap_id, body.name,
             f"Promoted from source evidence {body.evidence_id} ({src_id}). "
             f"Product rationale: {body.rationale}. Original signal: {signal_name} — "
             f"{full_description or ''}"))
        if body.markets:
            for name in body.markets:
                cur.execute("SELECT market_id FROM markets WHERE name=%s", (name,))
                row = cur.fetchone()
                if row:
                    cur.execute("""INSERT INTO capability_markets (cap_id, market_id)
                                   VALUES (%s,%s) ON CONFLICT DO NOTHING""", (cap_id, row[0]))
        record_audit(cur, "capability_candidate", new_id, "promote", actor.user_ref,
                     {"evidence_id": body.evidence_id, "source_id": src_id},
                     {"candidate_id": new_id, "cap_id": cap_id,
                      "rationale": body.rationale},
                     ["evidence_promotion"])
        conn.commit()
    return {"promoted": True, "candidate_id": new_id, "cap_id": cap_id,
            "evidence_id": body.evidence_id, "lineage": {
                "source_evidence": body.evidence_id, "source_id": src_id}}


@router.post("/candidates/{candidate_id}/request-review")
def request_review(candidate_id: str, body: dict = None,
                   conn: psycopg.Connection = Depends(db_conn),
                   actor: Actor = Depends(get_actor)):
    """Request Product Review on a Candidate (Phase A closure)."""
    body = body or {}
    with conn.cursor() as cur:
        cur.execute("SELECT version, review_requested FROM capability_candidates WHERE candidate_id=%s",
                    (candidate_id,))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail=f"candidate {candidate_id} not found")
        version, current = cur.fetchone()
        cur.execute(
            """UPDATE capability_candidates SET review_requested=true, version=version+1,
               updated_at=now() WHERE candidate_id=%s AND version=%s""",
            (candidate_id, version))
        if cur.rowcount == 0:
            raise HTTPException(status_code=409, detail={"error": "version_conflict"})
        record_audit(cur, "capability_candidate", candidate_id, "request_review",
                     actor.user_ref, {"review_requested": current},
                     {"review_requested": True}, ["review_requested"])
        conn.commit()
    return {"review_requested": True, "candidate_id": candidate_id, "version": version + 1}


class NewCapabilityBody(BaseModel):
    model_config = ConfigDict(extra="forbid")
    working_name: str = Field(min_length=1, max_length=300)
    description: str | None = None
    strategic_category: str | None = None
    rationale: str = Field(min_length=5)
    markets: list[str] | None = None


@router.post("/capabilities/create-product-created", status_code=201)
def create_product_created_capability(body: NewCapabilityBody,
                                      conn: psycopg.Connection = Depends(db_conn),
                                      actor: Actor = Depends(get_actor)):
    """Create a new Capability with Origin = PRODUCT_CREATED.
    Requires Product rationale. No fake Source evidence."""
    from ..models import STRATEGIC_CATEGORIES
    if body.strategic_category and body.strategic_category not in STRATEGIC_CATEGORIES:
        raise HTTPException(status_code=422, detail="invalid strategic_category")
    # generate CAP-ID
    cur = conn.cursor()
    cur.execute("SELECT count(*) FROM capabilities WHERE cap_id LIKE 'CAND-%'")
    n = cur.fetchone()[0]
    cap_id = f"CAND-NEW-{n + 1:04d}"
    cur.execute(
        """INSERT INTO capabilities (cap_id, working_name, description,
             strategic_category, roadmap_admission, notes,
             extraction_origin, population, review_status,
             product_rationale, created_by_product)
           VALUES (%s,%s,%s,%s,NULL,NULL,'PRODUCT_CREATED',
                   'SOURCE_ANALYSIS_CANDIDATE',
                   'PRODUCT CREATED · AWAITING REVIEW',%s,true)""",
        (cap_id, body.working_name, body.description,
         body.strategic_category or 'Awaiting Product data',
         body.rationale))
    if body.markets:
        for name in body.markets:
            cur.execute("SELECT market_id FROM markets WHERE name=%s", (name,))
            row = cur.fetchone()
            if row:
                cur.execute("INSERT INTO capability_markets (cap_id, market_id) VALUES (%s,%s) ON CONFLICT DO NOTHING",
                            (cap_id, row[0]))
    record_audit(cur, "capability", cap_id, "create_product_created",
                 actor.user_ref, None,
                 {"working_name": body.working_name, "rationale": body.rationale},
                 ["capability"])
    conn.commit()
    return {"created": True, "cap_id": cap_id}


class IdeationDecisionPatch(BaseModel):
    model_config = ConfigDict(extra="forbid")
    version: int = Field(ge=1)
    treatment: str | None = None
    rationale: str | None = None
    notes: str | None = None


@router.get("/ideation-decisions/{cap_id}")
def get_ideation_decisions(cap_id: str, conn: psycopg.Connection = Depends(db_conn)):
    with conn.cursor() as cur:
        cur.execute("""SELECT decision_id, cap_id, lens, treatment, rationale, notes,
                              owner, version, created_at, updated_at
                       FROM capability_ideation_decisions WHERE cap_id=%s
                       ORDER BY lens""", (cap_id,))
        cols = [d.name for d in cur.description]
        items = [dict(zip(cols, r)) for r in cur.fetchall()]
    return {"count": len(items), "items": items}


@router.patch("/ideation-decisions/{cap_id}/{lens}")
def patch_ideation_decision(cap_id: str, lens: str, body: IdeationDecisionPatch,
                            conn: psycopg.Connection = Depends(db_conn),
                            actor: Actor = Depends(get_actor)):
    LENSES = ("V2_POSITION", "V1_CARRY_FORWARD", "DIRECT_3X_MIGRATION", "NEW_NEEDS_GAPS", "DISCONTINUED")
    if lens not in LENSES:
        raise HTTPException(status_code=404, detail=f"unknown lens {lens}")
    provided = body.model_dump(exclude_unset=True)
    version = provided.pop("version")
    if not provided:
        raise HTTPException(status_code=400, detail="no fields to update")
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM capability_ideation_decisions WHERE cap_id=%s AND lens=%s",
                    (cap_id, lens))
        exists = cur.fetchone()[0] > 0
        if not exists:
            cur.execute(
                """INSERT INTO capability_ideation_decisions (cap_id, lens, treatment, rationale, notes, owner, version)
                   VALUES (%s,%s,%s,%s,%s,%s,1)""",
                (cap_id, lens, provided.get("treatment"), provided.get("rationale"),
                 provided.get("notes"), actor.user_ref))
        else:
            cur.execute("""SELECT version FROM capability_ideation_decisions
                           WHERE cap_id=%s AND lens=%s""", (cap_id, lens))
            db_version = cur.fetchone()[0]
            if db_version != version:
                raise HTTPException(status_code=409, detail={"error": "version_conflict", "current_version": db_version})
            sets = ", ".join(f"{k}=%s" for k in provided)
            cur.execute(f"""UPDATE capability_ideation_decisions SET {sets}, version=version+1, updated_at=now()
                           WHERE cap_id=%s AND lens=%s AND version=%s""",
                        (*provided.values(), cap_id, lens, version))
        record_audit(cur, "ideation_decision", f"{cap_id}:{lens}", "update",
                     actor.user_ref,
                     {k: before.get(k) for k in provided},
                     dict(provided), list(provided))
        conn.commit()
    return {"updated": True, "cap_id": cap_id, "lens": lens, "version": version + 1}


@router.get("/evidence/{evidence_id}")
def get_evidence_detail(evidence_id: str, conn: psycopg.Connection = Depends(db_conn)):
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM source_evidence WHERE evidence_id=%s", (evidence_id,))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="evidence not found")
        cols = [d.name for d in cur.description]
        row = dict(zip(cols, cur.fetchone()))
        cur.execute("SELECT title FROM sources WHERE source_id=%s", (row.get("source_id"),))
        src = cur.fetchone()
        row["source_title"] = src[0] if src else None
    return row


@router.get("/journey/{entity_type}/{entity_id}")
def view_journey(entity_type: str, entity_id: str,
                 conn: psycopg.Connection = Depends(db_conn)):
    """End-to-end traceability: lineage + decisions for any entity (§34)."""
    journey = {"entity_type": entity_type, "entity_id": entity_id, "lineage": [], "decisions": []}
    with conn.cursor() as cur:
        if entity_type == "capability":
            cur.execute("SELECT cap_id, working_name, population, extraction_origin, product_review_status, owner, decision_rationale FROM capabilities WHERE cap_id=%s", (entity_id,))
            cap = cur.fetchone()
            if not cap:
                raise HTTPException(status_code=404, detail="capability not found")
            cols = [d.name for d in cur.description]
            c = dict(zip(cols, cap))
            journey["name"] = c["working_name"]
            journey["lineage"] = [
                {"step": "Origin", "detail": c.get("extraction_origin") or "unknown"},
                {"step": "Population", "detail": c.get("population") or "unassigned"},
            ]
            cur.execute("""SELECT sc.source_id, s.title FROM source_capabilities sc
                           JOIN sources s ON s.source_id = sc.source_id WHERE sc.canonical_cap_id=%s""", (entity_id,))
            for r in cur.fetchall():
                journey["lineage"].append({"step": "Source", "detail": f"{r[0]} · {r[1]}"})
            cur.execute("""SELECT sc.evidence_id, sc.source_id, sc.signal_name
                           FROM source_evidence sc WHERE sc.current_canonical_cap_id=%s""", (entity_id,))
            for r in cur.fetchall():
                journey["lineage"].append({"step": "Evidence", "detail": f"{r[0]} · {r[2]}"})
            cur.execute("""SELECT f.feat_id, f.name FROM feature_capabilities fc
                           JOIN features f ON f.feat_id = fc.feat_id WHERE fc.cap_id=%s""", (entity_id,))
            for r in cur.fetchall():
                journey["lineage"].append({"step": "Feature", "detail": f"{r[0]} · {r[1]}"})
            cur.execute("""SELECT cc.customer_id, cu.name FROM customer_capabilities cc
                           JOIN customers cu ON cu.customer_id = cc.customer_id WHERE cc.cap_id=%s""", (entity_id,))
            for r in cur.fetchall():
                journey["lineage"].append({"step": "Customer", "detail": f"{r[0]} · {r[1]}"})
            journey["decisions"] = [
                {"decision": "Extraction provenance", "value": c.get("extraction_origin") or "unknown"},
                {"decision": "Product Review", "value": c.get("product_review_status") or "not reviewed"},
                {"decision": "Decision rationale", "value": c.get("decision_rationale") or "not recorded"},
                {"decision": "Owner", "value": c.get("owner") or "not assigned"},
            ]
        elif entity_type == "evidence":
            cur.execute("SELECT signal_name, source_id, current_treatment, reconciled_family_id, provenance FROM source_evidence WHERE evidence_id=%s", (entity_id,))
            ev = cur.fetchone()
            if not ev:
                raise HTTPException(status_code=404, detail="evidence not found")
            cols = [d.name for d in cur.description]
            e = dict(zip(cols, ev))
            journey["name"] = e["signal_name"]
            journey["lineage"] = [
                {"step": "Source", "detail": e["source_id"]},
                {"step": "Treatment", "detail": e["current_treatment"] or "UNRECONCILED"},
            ]
            if e["reconciled_family_id"]:
                journey["lineage"].append({"step": "Candidate", "detail": e["reconciled_family_id"]})
            journey["decisions"] = [{"decision": "Provenance", "value": e.get("provenance") or "unknown"}]
        elif entity_type == "feature":
            cur.execute("SELECT feat_id, name, owner, status FROM features WHERE feat_id=%s", (entity_id,))
            f = cur.fetchone()
            if not f:
                raise HTTPException(status_code=404, detail="feature not found")
            cols = [d.name for d in cur.description]
            feat = dict(zip(cols, f))
            journey["name"] = feat["name"]
            journey["lineage"] = [{"step": "Feature", "detail": feat["feat_id"]}]
            cur.execute("""SELECT fc.cap_id, c.working_name FROM feature_capabilities fc
                           JOIN capabilities c ON c.cap_id = fc.cap_id WHERE fc.feat_id=%s""", (entity_id,))
            for r in cur.fetchall():
                journey["lineage"].append({"step": "Capability", "detail": f"{r[0]} · {r[1]}"})
            journey["decisions"] = [{"decision": "Owner", "value": feat.get("owner") or "not assigned"},
                                    {"decision": "Status", "value": feat.get("status") or "not set"}]
        elif entity_type == "customer":
            cur.execute("SELECT customer_id, name, validation_status FROM customers WHERE customer_id=%s", (entity_id,))
            cu = cur.fetchone()
            if not cu:
                raise HTTPException(status_code=404, detail="customer not found")
            cols = [d.name for d in cur.description]
            customer = dict(zip(cols, cu))
            journey["name"] = customer["name"]
            journey["lineage"] = [{"step": "Customer", "detail": customer["customer_id"]}]
            cur.execute("""SELECT cc.cap_id, c.working_name FROM customer_capabilities cc
                           JOIN capabilities c ON c.cap_id = cc.cap_id WHERE cc.customer_id=%s""", (entity_id,))
            for r in cur.fetchall():
                journey["lineage"].append({"step": "Required Capability", "detail": f"{r[0]} · {r[1]}"})
            journey["decisions"] = [{"decision": "Validation status", "value": customer.get("validation_status") or "not assessed"}]
        else:
            raise HTTPException(status_code=404, detail=f"unknown entity type {entity_type}")
    return journey
