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
        cur.execute(f"""SELECT candidate_id, name, COALESCE(cap_id, 'CAND-' || candidate_id) AS cap_id, markets, signals,
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
        cur.execute("""SELECT candidate_id, name, COALESCE(cap_id, 'CAND-' || candidate_id) AS cap_id, markets, signals,
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
