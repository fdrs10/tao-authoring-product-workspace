"""roadmap outcomes — Product narrative per horizon (Phase 5, contract §6)

Revision ID: 0002_roadmap_outcomes
Revises: 0001_initial_schema
Create Date: 2026-10-15

Recovers the v38.6 "Roadmap | Outcome" switch: three Product narrative
blocks (0–6m / 7–24m / Tail). v38.6 stored them in localStorage; the
governed model persists them server-side with version + actor + audit
(§18: shared Product state never lives in LocalStorage).

Rows are created on demand (GET upserts missing horizon rows with a NULL
narrative) — no invented content, ever.
"""

from alembic import op

revision = "0002_roadmap_outcomes"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None

DDL = [
    """
CREATE TABLE roadmap_outcomes (
  horizon     text PRIMARY KEY CHECK (horizon IN ('0-6m','7-24m','tail')),
  narrative   text,
  version     bigint NOT NULL DEFAULT 1,
  updated_at  timestamptz NOT NULL DEFAULT now(),
  updated_by  text
)
""",
]

DDL_DOWN = ["DROP TABLE roadmap_outcomes"]


def upgrade() -> None:
    for stmt in DDL:
        op.execute(stmt)


def downgrade() -> None:
    for stmt in DDL_DOWN:
        op.execute(stmt)
