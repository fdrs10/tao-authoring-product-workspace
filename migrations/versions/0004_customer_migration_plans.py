"""Customer Migration Plan fields (FINAL UAT EVOLUTION, contract §9).

Revision ID: 0004_customer_migration_plans
Revises: 0003_uat_structural
Create Date: 2026-10-16

A Customer Migration Plan applies the ONE common Migration Path (M1–M6) to
ONE customer. The new columns carry only customer-side context — never
duplicated Product timing (§10: customer plans consume Product Roadmap truth).

Derived readiness (§14) is computed from underlying data at read time —
no speculative score column.
"""

from alembic import op

revision = "0004_customer_migration_plans"
down_revision = "0003_uat_structural"
branch_labels = None
depends_on = None

DDL = [
    """
ALTER TABLE customers
  ADD COLUMN current_environment text,
  ADD COLUMN relevant_markets    text,
  ADD COLUMN proposed_migration_window text,
  ADD COLUMN customer_dependencies text,
  ADD COLUMN assumptions         text,
  ADD COLUMN exceptions          text,
  ADD COLUMN customer_feedback   text
""",
]

DDL_DOWN = [
    """ALTER TABLE customers
  DROP COLUMN customer_feedback,
  DROP COLUMN exceptions,
  DROP COLUMN assumptions,
  DROP COLUMN customer_dependencies,
  DROP COLUMN proposed_migration_window,
  DROP COLUMN relevant_markets,
  DROP COLUMN current_environment""",
]


def upgrade() -> None:
    for stmt in DDL:
        op.execute(stmt)


def downgrade() -> None:
    for stmt in DDL_DOWN:
        op.execute(stmt)
