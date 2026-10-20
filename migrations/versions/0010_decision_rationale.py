"""Phase A closure: decision_rationale on capabilities.

Revision ID: 0010_decision_rationale
Revises: 0009_phase_a_closure
"""

from alembic import op

revision = "0010_decision_rationale"
down_revision = "0009_phase_a_closure"

DDL = ["ALTER TABLE capabilities ADD COLUMN IF NOT EXISTS decision_rationale text"]
DDL_DOWN = ["ALTER TABLE capabilities DROP COLUMN IF EXISTS decision_rationale"]


def upgrade() -> None:
    for stmt in DDL:
        op.execute(stmt)


def downgrade() -> None:
    for stmt in DDL_DOWN:
        op.execute(stmt)
