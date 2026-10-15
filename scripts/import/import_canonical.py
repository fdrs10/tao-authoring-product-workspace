#!/usr/bin/env python3
"""Idempotent canonical data loader — Authoring Product Workspace.

Contract (§16):
- idempotent, deterministic, preserves canonical IDs / source IDs /
  source-capability IDs, preserves NULL semantics, does not silently
  normalize Product values, reports inconsistencies, validates
  referential integrity.

Conflict policy: INSERT ... ON CONFLICT DO NOTHING everywhere.
This guarantees idempotency and — critically — never clobbers
in-database Product edits with a re-import. Re-imports that would
change a row are reported as SKIPPED for human review.

Governance encoded here (implementation contract, Phase 1 decisions):
- §3  five capabilities get review_status='PRODUCT_SCOPE_REVIEW_REQUIRED'
- §5  SRC-JIRA-001 registered (Operational / Delivery Evidence)
- §8  CAP-0134/CAP-0136 -> ideation_sheet='UNSET', review_status='REVIEW_REQUIRED'
- §9  roadmap_admission stays NULL (UNSET); never defaulted to Backlog
- §12 budgets never populated on import (NULL = not estimated)
- §13 decision labels imported verbatim (no normalization)
"""

import csv
import json
import os
import sys
from pathlib import Path

import psycopg

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA = REPO_ROOT / "data"

SCOPE_REVIEW_CAP_IDS = ["CAP-0071", "CAP-0126", "CAP-0128", "CAP-0131", "CAP-0133"]
UNSET_IDEATION_CAP_IDS = {"CAP-0134", "CAP-0136"}

SRC_JIRA_001 = {
    "source_id": "SRC-JIRA-001",
    "title": "Current Authoring Jira Backlog",
    "source_type": "Operational / Delivery Evidence",
    "owner": None,
    "source_date": None,
    "version_label": None,
    "document_uri": "data/raw/JIRA_current_backlog.csv",
    "summary": (
        "Current Authoring Jira backlog import. Operational/delivery "
        "evidence only - NOT product capability truth. Jira tickets map to "
        "0..N capabilities and capabilities map to 0..N tickets. Future "
        "implementations may replace CSV ingestion with a direct Jira API "
        "connection; this Source identity and lineage must survive that "
        "transition."
    ),
    "input_form": "Jira CSV export (governed); future: direct Jira API",
    "upstream_reference": "oat-sa.atlassian.net (current backlog)",
    "status": "REGISTERED",
}


def db_url() -> str:
    url = os.environ.get("DATABASE_URL") or os.environ.get("DB_URL")
    if not url:
        print("ERROR: DATABASE_URL required "
              "(e.g. postgresql+psycopg://user:pass@host:5432/db)")
        sys.exit(2)
    if url.startswith("postgresql+psycopg://"):
        url = "postgresql://" + url.split("://", 1)[1]
    if url.startswith("postgresql+psycopg2://"):
        url = "postgresql://" + url.split("://", 1)[1]
    return url


def rd_csv(rel: str):
    with open(DATA / rel, newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def insert_many(cur, sql, rows):
    executed = 0
    for row in rows:
        cur.execute(sql, row)
        executed += cur.rowcount  # 1 inserted, 0 conflict-skipped
    return executed


def main() -> int:
    caps = json.load(open(DATA / "canonical" / "capabilities.json"))
    jira = json.load(open(DATA / "canonical" / "jira_tickets.json"))
    sources = json.load(open(DATA / "canonical" / "sources.json"))
    s2c = rd_csv("source_extracts/SOURCE_TO_CANONICAL.csv")

    cap_ids = {c["id"] for c in caps}
    src_ids = {s["Source ID"] for s in sources}
    stats = {"inserted": {}, "skipped_conflicts": {}, "warnings": []}

    with psycopg.connect(db_url()) as conn:
        with conn.cursor() as cur:
            # --- sources (7 governed + SRC-JIRA-001 per §5)
            source_rows = [
                (
                    s["Source ID"], s["Document / Source"], s.get("Type"),
                    s.get("Owner"), None, None, None, None,
                    s.get("Input form"), s.get("Reference / upstream materials"),
                    s.get("Status"),
                )
                for s in sources
            ]
            source_rows.append(tuple(SRC_JIRA_001[k] for k in (
                "source_id", "title", "source_type", "owner", "source_date",
                "version_label", "document_uri", "summary", "input_form",
                "upstream_reference", "status")))
            src_ids.add("SRC-JIRA-001")
            n = insert_many(cur, """
                INSERT INTO sources (source_id, title, source_type, owner,
                  source_date, version_label, document_uri, summary,
                  input_form, upstream_reference, status)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (source_id) DO NOTHING""", source_rows)
            stats["inserted"]["sources"] = n
            stats["skipped_conflicts"]["sources"] = len(source_rows) - n

            # --- capabilities (§3/§8 governance marks; §9/§12 NULL semantics)
            cap_rows = []
            for c in sorted(caps, key=lambda x: x["id"]):
                review = c.get("reviewStatus")
                if c["id"] in SCOPE_REVIEW_CAP_IDS:
                    review = "PRODUCT_SCOPE_REVIEW_REQUIRED"
                if c["id"] in UNSET_IDEATION_CAP_IDS:
                    review = "REVIEW_REQUIRED"
                ideation = c.get("ideationSheet")
                if c["id"] in UNSET_IDEATION_CAP_IDS:
                    ideation = "UNSET"
                cap_rows.append((
                    c["id"], c["name"], c.get("description") or "",
                    c.get("category"), c.get("moscow"), c.get("visibility"),
                    c.get("scope"), c.get("origin"), c.get("owner"),
                    c.get("decision"), c.get("v2"), ideation,
                    c.get("admission"),  # NULL when unset (§9)
                    None, None,          # budgets: never populated (§12)
                    c.get("notes"), review,
                ))
            n = insert_many(cur, """
                INSERT INTO capabilities (cap_id, working_name, description,
                  strategic_category, moscow, visibility, scope, origin, owner,
                  decision, v2_mapping, ideation_sheet, roadmap_admission,
                  analysis_budget_hours, execution_budget_hours, notes,
                  review_status)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (cap_id) DO NOTHING""", cap_rows)
            stats["inserted"]["capabilities"] = n
            stats["skipped_conflicts"]["capabilities"] = len(cap_rows) - n

            # --- capability_markets (market names -> market_ids)
            cur.execute("SELECT market_id, name FROM markets")
            market_by_name = {r[1]: r[0] for r in cur.fetchall()}
            mk_rows = []
            for c in sorted(caps, key=lambda x: x["id"]):
                for m in c.get("markets") or []:
                    mid = market_by_name.get(m)
                    if not mid:
                        stats["warnings"].append(
                            f"unknown market '{m}' on {c['id']}")
                        continue
                    mk_rows.append((c["id"], mid))
            n = insert_many(cur, """
                INSERT INTO capability_markets (cap_id, market_id)
                VALUES (%s,%s) ON CONFLICT DO NOTHING""", mk_rows)
            stats["inserted"]["capability_markets"] = n
            stats["skipped_conflicts"]["capability_markets"] = len(mk_rows) - n

            # --- source_capabilities (Source Truth preserved verbatim, §18)
            sc_rows = []
            for r in s2c:
                cap_ref = r["Global CAP-ID"].strip() or None
                if cap_ref and cap_ref not in cap_ids:
                    stats["warnings"].append(
                        f"source cap {r['Source Capability ID']} maps to "
                        f"unknown CAP {cap_ref}")
                    cap_ref = None
                sc_rows.append((
                    r["Source Capability ID"], r["Source ID"],
                    r["Original / Extracted Capability Name"],
                    r["Full Description"], r.get("Source Category") or None,
                    r.get("Evidence / Reference") or None,
                    r.get("Source Confidence") or None,
                    r.get("Extraction Type") or None,
                    r.get("Review Status") or None,
                    cap_ref, r.get("Relationship to Canonical") or None,
                    r.get("Notes") or None,
                ))
            n = insert_many(cur, """
                INSERT INTO source_capabilities
                  (source_capability_id, source_id, original_name,
                   original_description, source_category, evidence_reference,
                   source_confidence, extraction_type, review_status,
                   canonical_cap_id, reconciliation_relationship, notes)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (source_capability_id) DO NOTHING""", sc_rows)
            stats["inserted"]["source_capabilities"] = n
            stats["skipped_conflicts"]["source_capabilities"] = \
                len(sc_rows) - n

            # --- capability_sources: lineage pairs from CSV plus registered
            # sources from canonical json (covers CAP-0134/0136 -> SRC-JIRA-001)
            pairs = {}
            for r in s2c:
                if r["Global CAP-ID"].strip() and r["Source ID"].strip():
                    pairs[(r["Global CAP-ID"].strip(), r["Source ID"].strip())] = (
                        r.get("Relationship to Canonical") or None)
            for c in caps:
                for sid in c.get("sourceIds") or []:
                    if sid not in src_ids:
                        stats["warnings"].append(
                            f"cap {c['id']} references unregistered {sid}")
                    pairs.setdefault((c["id"], sid), "CANONICAL_SOURCE")
            cs_rows = [(k[0], k[1], v) for k, v in sorted(pairs.items())
                       if k[0] in cap_ids]
            n = insert_many(cur, """
                INSERT INTO capability_sources (cap_id, source_id, relationship)
                VALUES (%s,%s,%s) ON CONFLICT DO NOTHING""", cs_rows)
            stats["inserted"]["capability_sources"] = n
            stats["skipped_conflicts"]["capability_sources"] = \
                len(cs_rows) - n

            # --- jira (§6: delivery evidence, treatment preserved)
            jt_rows = [(
                t["key"], t.get("issueType"), t.get("summary"),
                t.get("description"), t.get("status"), t.get("lifecycle"),
                t.get("targetRelease") or None, t.get("dueDate") or None,
                t.get("assignee") or None, t.get("url"),
                t.get("jiraEstimateHours"), t.get("capabilityTreatment"),
                t.get("reconciliationRationale"), json.dumps(t),
            ) for t in jira]
            n = insert_many(cur, """
                INSERT INTO jira_tickets
                  (jira_key, issue_type, summary, description, status,
                   lifecycle, target_release, due_date, assignee, jira_url,
                   jira_estimate_hours, capability_treatment,
                   reconciliation_rationale, raw_json)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb)
                ON CONFLICT (jira_key) DO NOTHING""", jt_rows)
            stats["inserted"]["jira_tickets"] = n
            stats["skipped_conflicts"]["jira_tickets"] = len(jt_rows) - n

            cj_rows = [
                (ci, t["key"], "DELIVERY_EVIDENCE", None)
                for t in jira for ci in (t.get("capIds") or [])
            ]
            n = insert_many(cur, """
                INSERT INTO capability_jira (cap_id, jira_key, relationship, note)
                VALUES (%s,%s,%s,%s) ON CONFLICT DO NOTHING""", cj_rows)
            stats["inserted"]["capability_jira"] = n
            stats["skipped_conflicts"]["capability_jira"] = len(cj_rows) - n

            # --- roadmap_timing (135 records from governed json)
            rt_rows = [(c["id"], c.get("start"), c.get("dur"))
                       for c in sorted(caps, key=lambda x: x["id"])]
            n = insert_many(cur, """
                INSERT INTO roadmap_timing (cap_id, start_month, duration_months)
                VALUES (%s,%s,%s) ON CONFLICT (cap_id) DO NOTHING""", rt_rows)
            stats["inserted"]["roadmap_timing"] = n
            stats["skipped_conflicts"]["roadmap_timing"] = len(rt_rows) - n

        conn.commit()

    print(json.dumps(stats, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
