"""Governed Product Truth export (Phase 6, contract §7).

- GET /api/export   full canonical export as JSON — one authoritative,
                    structured read for backup/portability/UAT. Product Truth
                    lives in PostgreSQL; this endpoint never scrapes the UI
                    and never writes anything.

Covers (§7 minimum): capabilities (incl. MoSCoW, Admission, budgets, decision,
visibility), markets + capability_markets, sources, source_capabilities
(lineage), capability_sources, jira_tickets + capability_jira (relationships),
roadmap_timing, roadmap_outcomes, milestones, customers, customer_capabilities.
"""

import datetime

from fastapi import APIRouter, Depends
import psycopg

from ..config import settings
from ..db import db_conn

router = APIRouter(prefix="/api", tags=["export"])

# table -> ordering key (deterministic export; stable diffs for portability)
ENTITIES = [
    ("capabilities", "cap_id"),
    ("capability_markets", "cap_id, market_id"),
    ("markets", "market_id"),
    ("sources", "source_id"),
    ("source_capabilities", "source_capability_id"),
    ("capability_sources", "cap_id, source_id"),
    ("jira_tickets", "jira_key"),
    ("capability_jira", "cap_id, jira_key"),
    ("roadmap_timing", "cap_id"),
    ("roadmap_outcomes", "horizon"),
    ("milestones", "milestone_id"),
    ("customers", "customer_id"),
    ("customer_capabilities", "customer_id, cap_id"),
]


def _rows(cur: psycopg.Cursor, table: str, order: str) -> list[dict]:
    cur.execute(f"SELECT * FROM {table} ORDER BY {order}")
    cols = [d.name for d in cur.description]
    out = []
    for r in cur.fetchall():
        row = {}
        for k, v in zip(cols, r):
            row[k] = v.isoformat() if hasattr(v, "isoformat") else v
        out.append(row)
    return out


@router.get("/export")
def export_product_truth(conn: psycopg.Connection = Depends(db_conn)):
    entities = {}
    with conn.cursor() as cur:
        for table, order in ENTITIES:
            entities[table] = _rows(cur, table, order)
    return {
        "export": "tao-authoring-product-truth",
        "app_version": settings.version,
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "counts": {k: len(v) for k, v in entities.items()},
        "entities": entities,
    }
