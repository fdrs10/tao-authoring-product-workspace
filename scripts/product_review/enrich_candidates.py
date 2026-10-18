#!/usr/bin/env python3
"""Evidence-grounded enrichment of the 34 Capability Candidates + Jira coverage
audit (CONTROLLED PRODUCT OPERATION — no Roadmap prioritisation, no Admission
changes, no automatic promotion).

Sources of truth used (governed only):
- capability_candidates + capabilities (active candidate population)
- source_evidence + the package's embedded reconciliation register
  (per-row Reconciled Family ID / Reconciliation Result — the analysis
  decisions that took 426 signals to 34 candidates)
- governed Jira dataset + existing Jira↔Capability relationships

Distinctions preserved: SOURCE FACT vs PRODUCT INTERPRETATION vs PRODUCT
DECISION vs DELIVERY EVIDENCE. Where evidence cannot establish something the
record says so explicitly ("Evidence insufficient to determine" /
"Product definition required"). Product Review and Roadmap Admission are NOT
changed by this operation.

Outputs:
- DB: capability_candidates.enrichment (jsonb), capabilities.description
  (functional definition for the active population), source_evidence family
  linkage, jira_tickets.coverage_class/coverage_note
- data/product-review/candidate_enrichment.json  (one record per candidate)
- data/product-review/jira_candidate_coverage.json (one record per Jira item)
"""

import json
import os
import sys
from pathlib import Path

import psycopg

REPO = Path(__file__).resolve().parents[2]
REGISTER = REPO / "data" / "source-analysis" / "v1_4" / "reconciliation_register_enriched.json"
OUT_DIR = REPO / "data" / "product-review"

JIRA_CONTAINERS = {"epic", "container", "placeholder"}


def norm(v):
    return (v or "").strip()


def main() -> int:
    url = os.environ.get("DATABASE_URL", "")
    if url.startswith("postgresql+psycopg"):
        url = "postgresql://" + url.split("://", 1)[1]
    if not url:
        print("DATABASE_URL required", file=sys.stderr)
        return 2
    reg = {r["Source Capability ID"]: r for r in json.loads(REGISTER.read_text())}

    with psycopg.connect(url, autocommit=True) as conn, conn.cursor() as cur:
        # ---- 0. backfill per-evidence family linkage from the package register
        linked = 0
        for eid, r in reg.items():
            cur.execute(
                """UPDATE source_evidence
                   SET reconciled_family_id=%s, reconciliation_result=%s
                   WHERE evidence_id=%s AND reconciled_family_id IS NULL""",
                (r.get("Reconciled Family ID"), r.get("Reconciliation Result"), eid))
            linked += cur.rowcount
        cur.execute("SELECT count(*) FROM source_evidence WHERE reconciled_family_id IS NOT NULL")
        linked_total = cur.fetchone()[0]

        # ---- 1. candidates + their consolidated evidence
        cur.execute("""SELECT candidate_id, name, markets, signals, independent_sources,
                              source_ids, evidence_strength, cross_market_leverage,
                              strategy_alignment, mexcbt_signals, package_status,
                              is_focus, focus_markets, ideation_disposition,
                              disposition_rationale, cap_id, version
                       FROM capability_candidates ORDER BY candidate_id""")
        cols = [d.name for d in cur.description]
        candidates = [dict(zip(cols, r)) for r in cur.fetchall()]

        enrichments = {}
        for cand in candidates:
            fam = cand["candidate_id"]
            cur.execute(
                """SELECT evidence_id, source_id, signal_name, full_description,
                          evidence_type, extraction_type, source_confidence,
                          authoring_scope, evidence_reference, current_treatment,
                          authoring_scope AS scope_col
                   FROM source_evidence WHERE reconciled_family_id=%s
                   ORDER BY evidence_id""", (fam,))
            cols_e = [d.name for d in cur.description]
            ev = [dict(zip(cols_e, r)) for r in cur.fetchall()]
            cur.execute(
                """SELECT DISTINCT authoring_scope FROM source_evidence
                   WHERE reconciled_family_id=%s AND authoring_scope IS NOT NULL
                     AND authoring_scope <> ''""", (fam,))
            scopes = [r[0] for r in cur.fetchall()]

            signal_names = [e["signal_name"] for e in ev]
            sources = sorted({e["source_id"] for e in ev})
            refs = sorted({e["evidence_reference"] for e in ev if e["evidence_reference"]})

            # PRODUCT INTERPRETATION — synthesised strictly from the consolidated
            # signal names/descriptions of THIS family, with evidence citations.
            definition = (
                f"Ability to {cand['name'].lower()} — consolidated from "
                f"{len(ev)} source evidence signals across {len(sources)} independent "
                f"sources ({', '.join(signal_names[:6])}"
                f"{'…' if len(signal_names) > 6 else ''}).")
            enables = (
                " ; ".join(f"{e['signal_name']} ({e['evidence_id']})"
                           for e in ev[:5]) or "Evidence insufficient to determine")
            problem = (
                "Evidence insufficient to determine — the Source package records the "
                "signals but no explicit user/product problem statement for this family.")
            scope_txt = (
                f"Functional scope per consolidated evidence: {', '.join(signal_names)}."
                + (f" Authoring-scope assessments recorded: {', '.join(scopes)}." if scopes else ""))
            out_of_scope = (
                "Evidence insufficient to determine — explicit out-of-scope boundaries "
                "require a Product decision.")
            why = (
                f"Survived the 426 → 34 analysis as family {fam}: {cand['signals']} signals "
                f"consolidated from {cand['independent_sources']} independent sources; evidence "
                f"strength {cand['evidence_strength']}; cross-market leverage "
                f"{cand['cross_market_leverage']}; strategy alignment {cand['strategy_alignment']}; "
                f"package status: {cand['package_status']}.")
            uncertainty = (
                "Functional description is a consolidation of source signal names/descriptions "
                "(PRODUCT INTERPRETATION) — a Product-written definition is required."
                if len(ev) < 3 else
                "Consolidation is evidence-backed; a Product-written definition is still required.")

            # delivery evidence (Jira) — via capability_jira on the candidate's cap row
            cur.execute(
                """SELECT j.jira_key, j.summary, j.status, j.target_release, j.jira_url
                   FROM capability_jira cj JOIN jira_tickets j ON j.jira_key = cj.jira_key
                   WHERE cj.cap_id=%s ORDER BY j.jira_key""", (cand["cap_id"],))
            jira = [dict(zip([d.name for d in cur.description], r)) for r in cur.fetchall()]

            enrichment = {
                "candidate_id": fam,
                "cap_id": cand["cap_id"],
                "working_name": cand["name"],
                "identity": {
                    "cap_id": cand["cap_id"], "working_name": cand["name"],
                    "strategic_category": "Awaiting Product data"},
                "product_definition": {
                    "functional_definition": definition,
                    "what_it_enables": enables,
                    "user_problem_addressed": problem,
                    "functional_scope": scope_txt,
                    "out_of_scope": out_of_scope,
                    "interpretation_marker": "PRODUCT INTERPRETATION — consolidated from source evidence; not a Source-verbatim definition"},
                "analysis_rationale": {
                    "why_this_candidate": why,
                    "consolidation_rationale": (
                        f"The analysis grouped {len(ev)} evidence signals into this family; "
                        f"per-signal decisions recorded as Reconciliation Result."),
                    "evidence_counts": {"signals": len(ev), "sources": len(sources),
                                        "package_declared": cand["signals"]}},
                "product_context": {
                    "markets": cand["markets"],
                    "mexcbt_signals": cand["mexcbt_signals"],
                    "strategy_alignment": cand["strategy_alignment"],
                    "cross_market_leverage": cand["cross_market_leverage"],
                    "evidence_strength": cand["evidence_strength"],
                    "is_focus": cand["is_focus"],
                    "focus_markets": cand["focus_markets"]},
                "evidence": {
                    "signal_ids": [e["evidence_id"] for e in ev],
                    "signal_names": signal_names,
                    "sources": sources,
                    "count": len(ev),
                    "key_references": refs[:10],
                    "provenance": "Source Truth layer (source_evidence) + package reconciliation register"},
                "relationships": {
                    "related_candidates": [],
                    "dependencies": "Evidence insufficient to determine",
                    "potential_overlaps": "Consistency review pending (see CANDIDATE_CONSISTENCY_REVIEW)"},
                "delivery_evidence": {
                    "jira": jira,
                    "note": "Jira is delivery/work evidence — its existence implies no Product decision."},
                "product_review": {
                    "product_review_status": "not reviewed (enrichment is preparation for review)",
                    "ideation_disposition": cand["ideation_disposition"],
                    "open_questions": [
                        "Product-written functional definition required",
                        "Strategic Category assignment required"],
                    "uncertainty": uncertainty},
            }
            enrichments[fam] = enrichment

            # mirror the functional definition onto the active capability row so
            # Backlog/Roadmap/Reports consume the enriched definition
            cur.execute("UPDATE capabilities SET description=%s WHERE cap_id=%s",
                        (definition, cand["cap_id"]))

        for fam, e in enrichments.items():
            cur.execute("UPDATE capability_candidates SET enrichment=%s WHERE candidate_id=%s",
                        (psycopg.types.json.Json(e), fam))

        # ---- 2. Jira coverage audit (§9/§10/§11) — deterministic classification
        cur.execute("""SELECT j.jira_key, j.summary, j.issue_type, j.status,
                              j.target_release, j.jira_url
                       FROM jira_tickets j ORDER BY j.jira_key""")
        jcols = [d.name for d in cur.description]
        jiras = [dict(zip(jcols, r)) for r in cur.fetchall()]
        cur.execute("""SELECT cj.jira_key, cj.cap_id, c.population, c.working_name
                       FROM capability_jira cj
                       JOIN capabilities c ON c.cap_id = cj.cap_id""")
        links = cur.fetchall()

        coverage = []
        for j in jiras:
            key = j["jira_key"]
            linked_caps = [(cap, pop, name) for (jk, cap, pop, name) in links if jk == key]
            itype = norm(j["issue_type"]).lower()
            if any(k in itype for k in JIRA_CONTAINERS) or "placeholder" in norm(j["summary"]).lower():
                cls, note = "D_NON_CAPABILITY_DELIVERY_CONTAINER", (
                    "Epic/container/placeholder work-management record — not a Product Capability.")
            elif any(pop == "SOURCE_ANALYSIS_CANDIDATE" for _, pop, _ in linked_caps):
                cls, note = "A_COVERED_BY_ACTIVE_CANDIDATE", (
                    "Linked to active candidate capability: " + ", ".join(
                        f"{cap} ({name})" for cap, pop, name in linked_caps
                        if pop == "SOURCE_ANALYSIS_CANDIDATE"))
            elif linked_caps:
                cls, note = "E_PRODUCT_REVIEW_REQUIRED", (
                    "Linked only to the historical baseline (" + ", ".join(
                        cap for cap, pop, _ in linked_caps) + ") — the relationship to the "
                    "34 active candidates cannot safely be determined from current evidence.")
            else:
                cls, note = "C_NOT_REPRESENTED_BY_ACTIVE_CANDIDATES", (
                    "No governed Jira↔Capability relationship exists for this record.")
            cur.execute("UPDATE jira_tickets SET coverage_class=%s, coverage_note=%s "
                        "WHERE jira_key=%s", (cls, note, key))
            coverage.append({
                "jira_key": key, "summary": j["summary"], "issue_type": j["issue_type"],
                "status": j["status"], "target_release": j["target_release"],
                "jira_url": j["jira_url"],
                "existing_product_relationship": (
                    [{"cap_id": cap, "population": pop, "name": name}
                     for cap, pop, name in linked_caps] or None),
                "coverage_class": cls, "coverage_note": note,
                "suggested_review_question": (
                    "Should this work relate to an active Candidate, stay delivery-only, "
                    "or be treated as no longer relevant?" if cls.startswith("C_") or
                    cls.startswith("E_") else None)})

        OUT_DIR.mkdir(parents=True, exist_ok=True)
        (OUT_DIR / "candidate_enrichment.json").write_text(
            json.dumps({"generated_by": "scripts/product_review/enrich_candidates.py",
                        "active_candidates": len(enrichments),
                        "items": list(enrichments.values())}, indent=1))
        (OUT_DIR / "jira_candidate_coverage.json").write_text(
            json.dumps({"generated_by": "scripts/product_review/enrich_candidates.py",
                        "jira_records": len(coverage),
                        "coverage_counts": dict(sorted(
                            (cls, sum(1 for c in coverage if c["coverage_class"] == cls))
                            for cls in {c["coverage_class"] for c in coverage})),
                        "items": coverage}, indent=1))
        print(json.dumps({"evidence_family_link_backfilled": linked,
                          "evidence_family_linked_total": linked_total,
                          "candidates_enriched": len(enrichments),
                          "jira_records_audited": len(coverage),
                          "coverage_counts": dict(sorted(
                              (cls, sum(1 for c in coverage if c["coverage_class"] == cls))
                              for cls in {c["coverage_class"] for c in coverage}))}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
