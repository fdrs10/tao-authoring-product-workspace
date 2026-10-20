"""Phase D: Customer↔Feature M:N + Customer workspace enhancement.

Revision ID: 0012_phase_d_customers
Revises: 0011_phase_b_workflow
"""

from alembic import op

revision = "0012_phase_d_customers"
down_revision = "0011_phase_b_workflow"

DDL = [
    """CREATE TABLE customer_features (
  customer_id text NOT NULL REFERENCES customers(customer_id),
  feat_id     text NOT NULL REFERENCES features(feat_id),
  importance  text NOT NULL DEFAULT 'REQUIRED'
              CHECK (importance IN ('KEY','REQUIRED','RELEVANT')),
  required_for_migration boolean NOT NULL DEFAULT false,
  required_by_milestone text,
  rationale   text,
  validation_status text NOT NULL DEFAULT 'PRODUCT_HYPOTHESIS',
  customer_feedback text,
  notes       text,
  version     bigint NOT NULL DEFAULT 1,
  created_at  timestamptz NOT NULL DEFAULT now(),
  updated_at  timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (customer_id, feat_id)
)""",
    "ALTER TABLE customers ADD COLUMN IF NOT EXISTS owner text",
]

DDL_DOWN = [
    "ALTER TABLE customers DROP COLUMN IF EXISTS owner",
    "DROP TABLE customer_features",
]


def upgrade() -> None:
    for stmt in DDL:
        op.execute(stmt)


def downgrade() -> None:
    for stmt in DDL_DOWN:
        op.execute(stmt)
