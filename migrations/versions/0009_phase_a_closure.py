"""Phase A closure: owner + review_requested on capability_candidates.

Revision ID: 0009_phase_a_closure
Revises: 0008_phase_a_collaboration
"""

from alembic import op

revision = "0009_phase_a_closure"
down_revision = "0008_phase_a_collaboration"
branch_labels = None
depends_on = None

DDL = [
    "ALTER TABLE capability_candidates ADD COLUMN IF NOT EXISTS owner text",
    "ALTER TABLE capability_candidates ADD COLUMN IF NOT EXISTS review_requested boolean NOT NULL DEFAULT false",
]

DDL_DOWN = [
    "ALTER TABLE capability_candidates DROP COLUMN IF EXISTS review_requested, DROP COLUMN IF EXISTS owner",
]


def upgrade() -> None:
    for stmt in DDL:
        op.execute(stmt)


def downgrade() -> None:
    for stmt in DDL_DOWN:
        op.execute(stmt)
