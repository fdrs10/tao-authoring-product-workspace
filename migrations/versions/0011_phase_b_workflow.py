"""Phase B: Ideation lens decisions + Product-created capability support.

Revision ID: 0011_phase_b_workflow
Revises: 0010_decision_rationale
Create Date: 2026-10-16
"""

from alembic import op

revision = "0011_phase_b_workflow"
down_revision = "0010_decision_rationale"
branch_labels = None
depends_on = None

DDL = [
    """CREATE TABLE capability_ideation_decisions (
  decision_id  bigserial PRIMARY KEY,
  cap_id       text NOT NULL REFERENCES capabilities(cap_id),
  lens         text NOT NULL CHECK (lens IN ('V2_POSITION','V1_CARRY_FORWARD','DIRECT_3X_MIGRATION','NEW_NEEDS_GAPS','DISCONTINUED')),
  treatment    text,
  rationale    text,
  notes        text,
  owner        text,
  version      bigint NOT NULL DEFAULT 1,
  created_at   timestamptz NOT NULL DEFAULT now(),
  updated_at   timestamptz NOT NULL DEFAULT now(),
  UNIQUE (cap_id, lens)
)""",
    """ALTER TABLE capabilities ADD COLUMN IF NOT EXISTS created_by_product boolean NOT NULL DEFAULT false""",
]

DDL_DOWN = [
    "ALTER TABLE capabilities DROP COLUMN IF EXISTS created_by_product",
    "DROP TABLE capability_ideation_decisions",
]


def upgrade() -> None:
    for stmt in DDL:
        op.execute(stmt)


def downgrade() -> None:
    for stmt in DDL_DOWN:
        op.execute(stmt)
