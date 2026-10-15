#!/usr/bin/env python3
"""Post-import validation — §53 deliverables 5/6/7.

Checks record counts, referential integrity and NULL/UNSET semantics
against the Phase 1 reconciled truth, writing a machine-readable report
to data/reports/phase2_import_validation.json. Exit code 0 = all checks
pass; non-zero = at least one FAIL.
"""

import json
import os
import sys
from pathlib import Path

import psycopg

REPO_ROOT = Path(__file__).resolve().parents[2]
OUT = REPO_ROOT / "data" / "reports" / "phase2_import_validation.json"


def db_url() -> str:
    url = os.environ.get("DATABASE_URL") or os.environ.get("DB_URL")
    if not url:
        print("ERROR: DATABASE_URL required")
        sys.exit(2)
    for p in ("postgresql+psycopg://", "postgresql+psycopg2://"):
        if url.startswith(p):
            url = "postgresql://" + url.split("://", 1)[1]
    return url


def q(cur, sql, args=None):
    cur.execute(sql, args or [])
    return cur.fetchall()


def main() -> int:
    checks = []
    add = checks.append

    with psycopg.connect(db_url()) as conn, conn.cursor() as cur:
        counts = {
            t: q(cur, f"SELECT count(*) FROM {t}")[0][0]
            for t in ["capabilities", "sources", "source_capabilities",
                      "capability_sources", "capability_markets", "markets",
                      "jira_tickets", "capability_jira", "roadmap_timing",
                      "customers", "milestones"]
        }
        expect = {
            "capabilities": 135, "sources": 8,        # 7 + SRC-JIRA-001 (§5)
            "source_capabilities": 224, "jira_tickets": 28,
            "capability_jira": 32, "markets": 6, "roadmap_timing": 135,
            "customers": 0, "milestones": 0,          # §39/§36: no invented rows
        }
        for k, v in expect.items():
            add({"check": f"count:{k}", "expected": v, "actual": counts[k],
                 "status": "PASS" if counts[k] == v else "FAIL"})

        # referential integrity
        ri = {
            "source_caps_with_unknown_cap":
                "SELECT count(*) FROM source_capabilities sc LEFT JOIN capabilities c ON sc.canonical_cap_id=c.cap_id WHERE sc.canonical_cap_id IS NOT NULL AND c.cap_id IS NULL",
            "cap_sources_unknown_ref":
                "SELECT count(*) FROM capability_sources x LEFT JOIN capabilities c ON x.cap_id=c.cap_id LEFT JOIN sources s ON x.source_id=s.source_id WHERE c.cap_id IS NULL OR s.source_id IS NULL",
            "cap_jira_unknown_ref":
                "SELECT count(*) FROM capability_jira x LEFT JOIN capabilities c ON x.cap_id=c.cap_id LEFT JOIN jira_tickets j ON x.jira_key=j.jira_key WHERE c.cap_id IS NULL OR j.jira_key IS NULL",
            "cap_markets_unknown_ref":
                "SELECT count(*) FROM capability_markets x LEFT JOIN capabilities c ON x.cap_id=c.cap_id LEFT JOIN markets m ON x.market_id=m.market_id WHERE c.cap_id IS NULL OR m.market_id IS NULL",
            "timing_unknown_cap":
                "SELECT count(*) FROM roadmap_timing r LEFT JOIN capabilities c ON r.cap_id=c.cap_id WHERE c.cap_id IS NULL",
        }
        for name, sql in ri.items():
            v = q(cur, sql)[0][0]
            add({"check": f"referential:{name}", "expected": 0,
                 "actual": v, "status": "PASS" if v == 0 else "FAIL"})

        # uniqueness of canonical IDs (PK enforces; belt and braces)
        v = q(cur, "SELECT count(*) - count(DISTINCT cap_id) FROM capabilities")[0][0]
        add({"check": "no_duplicate_cap_ids", "expected": 0, "actual": v,
             "status": "PASS" if v == 0 else "FAIL"})
        v = q(cur, "SELECT count(*) FROM capabilities WHERE cap_id='CAP-0135'")[0][0]
        add({"check": "retired_CAP-0135_absent", "expected": 0, "actual": v,
             "status": "PASS" if v == 0 else "FAIL"})

        # §9 / §12 NULL semantics
        v = q(cur, "SELECT count(*) FROM capabilities WHERE roadmap_admission IS NULL")[0][0]
        add({"check": "admission_NULL_meaning_UNSET", "expected": 133,
             "actual": v, "status": "PASS" if v == 133 else "FAIL"})
        v = q(cur, "SELECT count(*) FROM capabilities WHERE roadmap_admission='Candidate'")[0][0]
        add({"check": "admission_Candidate", "expected": 2, "actual": v,
             "status": "PASS" if v == 2 else "FAIL"})
        v = q(cur, "SELECT count(*) FROM capabilities WHERE analysis_budget_hours IS NULL")[0][0]
        u = q(cur, "SELECT count(*) FROM capabilities WHERE execution_budget_hours IS NULL")[0][0]
        add({"check": "budgets_NULL_not_zero", "expected": "135/135",
             "actual": f"{v}/{u}",
             "status": "PASS" if (v, u) == (135, 135) else "FAIL"})

        # §3/§8 governance marks
        rows = [r[0] for r in q(cur, "SELECT cap_id FROM capabilities WHERE review_status='PRODUCT_SCOPE_REVIEW_REQUIRED' ORDER BY cap_id")]
        exp_rows = ["CAP-0071", "CAP-0126", "CAP-0128", "CAP-0131", "CAP-0133"]
        add({"check": "scope_review_marks_s3", "expected": exp_rows,
             "actual": rows, "status": "PASS" if rows == exp_rows else "FAIL"})
        v = q(cur, "SELECT count(*) FROM capabilities WHERE cap_id IN ('CAP-0134','CAP-0136') AND ideation_sheet='UNSET' AND review_status='REVIEW_REQUIRED'")[0][0]
        add({"check": "cap_0134_0136_governance_s8", "expected": 2,
             "actual": v, "status": "PASS" if v == 2 else "FAIL"})

        # §5 SRC-JIRA-001 registered
        v = q(cur, "SELECT count(*) FROM sources WHERE source_id='SRC-JIRA-001' AND source_type='Operational / Delivery Evidence'")[0][0]
        add({"check": "src_jira_001_registered_s5", "expected": 1,
             "actual": v, "status": "PASS" if v == 1 else "FAIL"})

        # markets exact set (§26)
        rows = [r[0] for r in q(cur, "SELECT name FROM markets ORDER BY name")]
        exp = sorted(["Traditional / K-12", "Professional / Credentialing",
                      "Higher Education", "Governed Formative",
                      "Assessment-led Learning", "MEXCBT / Uchida"])
        add({"check": "markets_exact_six_s26", "expected": exp, "actual": rows,
             "status": "PASS" if rows == exp else "FAIL"})

        # PCR treatments preserved (§6)
        rows = dict(q(cur, "SELECT jira_key, capability_treatment FROM jira_tickets WHERE jira_key IN ('PCR-117','PCR-139','PCR-201','PCR-215')"))
        exp = {"PCR-117": "EVIDENCE_ONLY", "PCR-139": "NEEDS_DECOMPOSITION",
               "PCR-201": "NON_CAPABILITY", "PCR-215": "NEEDS_DECOMPOSITION"}
        add({"check": "pcr_treatments_s6", "expected": exp, "actual": rows,
             "status": "PASS" if rows == exp else "FAIL"})

        # derived KPIs for the report
        v = q(cur, "SELECT count(DISTINCT jira_key) FROM capability_jira")[0][0]
        add({"check": "linked_jira_tickets", "expected": 24, "actual": v,
             "status": "PASS" if v == 24 else "FAIL"})
        v = q(cur, "SELECT count(DISTINCT cap_id) FROM capability_jira")[0][0]
        add({"check": "caps_with_jira_links", "expected": 17, "actual": v,
             "status": "PASS" if v == 17 else "FAIL"})

        # derived KPIs for the report
        kpi = {
            "caps_with_jira_links": v,
            "capability_market_links": q(cur, "SELECT count(*) FROM capability_markets")[0][0],
            "capability_source_links": q(cur, "SELECT count(*) FROM capability_sources")[0][0],
        }

    report = {
        "phase": 2, "checks": checks, "counts": counts, "kpi": kpi,
        "summary": {"pass": sum(1 for c in checks if c["status"] == "PASS"),
                    "fail": sum(1 for c in checks if c["status"] == "FAIL")},
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True))
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["summary"]["fail"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
