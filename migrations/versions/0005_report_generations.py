"""report_generations — generated report snapshots (FINAL STRUCTURAL STEP).

A generated report is a snapshot of Product Truth at generation time.
Generating one NEVER mutates Product Truth; this table records only
generation metadata + the rendered HTML for retrieval.
"""

from alembic import op

revision = "0005_report_generations"
down_revision = "0004_customer_migration_plans"
branch_labels = None
depends_on = None

DDL = [
    """
CREATE TABLE report_generations (
  generation_id   bigserial PRIMARY KEY,
  report_id       text NOT NULL,
  report_type     text NOT NULL,
  version         integer NOT NULL,
  actor           text NOT NULL,
  generated_at    timestamptz NOT NULL DEFAULT now(),
  params          jsonb,
  source_snapshot jsonb,
  html            text
)
""",
    "CREATE INDEX idx_report_generations_report ON report_generations (report_id, version)",
]

DDL_DOWN = ["DROP TABLE report_generations"]


def upgrade() -> None:
    for stmt in DDL:
        op.execute(stmt)


def downgrade() -> None:
    for stmt in DDL_DOWN:
        op.execute(stmt)
