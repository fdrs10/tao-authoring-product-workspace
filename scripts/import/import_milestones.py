#!/usr/bin/env python3
"""Deterministic, idempotent import of the governed milestone baseline.

Contract (UAT STRUCTURAL UPDATE §22/§23):
- Materialises M1–M6 from data/milestones/milestones_baseline.json (Product
  confirmed as the editable UAT baseline; recovered from
  TAO_Authoring_v35_6_MIGRATION_DIAGRAM).
- ON CONFLICT (milestone_id) DO NOTHING — never overwrites in-database
  Product edits. Rows that would differ are reported as SKIPPED for review.
- Roadmap and Migration consume the same records (no separate datasets).
- Does NOT invent milestones beyond M1–M6 and does NOT use ad-hoc SQL.
"""

import json
import os
import sys
from pathlib import Path

import psycopg

REPO_ROOT = Path(__file__).resolve().parents[2]
BASELINE = REPO_ROOT / "data" / "milestones" / "milestones_baseline.json"


def db_url() -> str:
    """psycopg connects with plain postgresql:// — normalise SQLAlchemy-style
    schemes the same way import_canonical.py does."""
    url = os.environ.get("DATABASE_URL") or os.environ.get("DB_URL")
    if not url:
        print("ERROR: DATABASE_URL required "
              "(e.g. postgresql+psycopg://user:pass@host:5432/db)", file=sys.stderr)
        sys.exit(2)
    if url.startswith("postgresql+psycopg://") or url.startswith("postgresql+psycopg2://"):
        url = "postgresql://" + url.split("://", 1)[1]
    return url


def main() -> int:
    data = json.loads(BASELINE.read_text())
    rows = [
        (m["milestone_id"], m["name"], m["milestone_date"], m["scope_type"],
         m["scope_ref"], m["description"], m["position_month"])
        for m in data["milestones"]
    ]
    with psycopg.connect(db_url()) as conn, \
            conn.cursor() as cur:
        inserted, skipped = 0, []
        for r in rows:
            cur.execute(
                """INSERT INTO milestones (milestone_id, name, milestone_date,
                       scope_type, scope_ref, description, position_month)
                   VALUES (%s,%s,%s,%s,%s,%s,%s)
                   ON CONFLICT (milestone_id) DO NOTHING""", r)
            if cur.rowcount:
                inserted += 1
            else:
                cur.execute(
                    "SELECT name, milestone_date, position_month "
                    "FROM milestones WHERE milestone_id=%s", (r[0],))
                existing = cur.fetchone()
                same = (existing[0] == r[1] and str(existing[1]) == r[2]
                        and existing[2] == r[6])
                skipped.append({"milestone_id": r[0],
                                "action": "SKIPPED (already present"
                                          + (", identical" if same else
                                             ", DIFFERS from baseline — review)")})
        conn.commit()
    print(json.dumps({"dataset": data["dataset"], "inserted": inserted,
                      "total_baseline": len(rows), "skipped": skipped}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
