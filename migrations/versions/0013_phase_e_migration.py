"""Phase E: Customer migration per-interval analysis + conflict detection.

Revision ID: 0013_phase_e_migration
Revises: 0012_phase_d_customers
"""

from alembic import op

revision = "0013_phase_e_migration"
down_revision = "0012_phase_d_customers"

DDL = [
    """CREATE TABLE IF NOT EXISTS customer_migration_intervals (
  customer_id text NOT NULL REFERENCES customers(customer_id),
  from_milestone text NOT NULL,
  to_milestone text NOT NULL,
  treatment text,
  rationale text,
  notes text,
  version bigint NOT NULL DEFAULT 1,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (customer_id, from_milestone)
)""",
]


def upgrade() -> None:
    for stmt in DDL:
        op.execute(stmt)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS customer_migration_intervals")
