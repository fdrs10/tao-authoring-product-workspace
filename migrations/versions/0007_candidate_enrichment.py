"""Candidate enrichment + Jira coverage (CONTROLLED PRODUCT OPERATION).

Revision ID: 0007_candidate_enrichment
Revises: 0006_source_analysis
Create Date: 2026-10-16

- capability_candidates.enrichment jsonb — the evidence-grounded Product
  definition per candidate (identity/definition/context/evidence/relationships/
  review). Generating enrichment never changes Product Review or Admission.
- source_evidence.reconciled_family_id / reconciliation_result — the per-row
  analysis linkage from the final package (426 rows).
- jira_tickets.coverage_class / coverage_note — Jira-vs-34 coverage audit
  classification (A–E, §9); Product-editable later.
"""

from alembic import op

revision = "0007_candidate_enrichment"
down_revision = "0006_source_analysis"
branch_labels = None
depends_on = None

DDL = [
    "ALTER TABLE capability_candidates ADD COLUMN enrichment jsonb",
    "ALTER TABLE source_evidence ADD COLUMN reconciled_family_id text,"
    " ADD COLUMN reconciliation_result text",
    "CREATE INDEX idx_source_evidence_family ON source_evidence (reconciled_family_id)",
    "ALTER TABLE jira_tickets ADD COLUMN coverage_class text,"
    " ADD COLUMN coverage_note text",
]


def upgrade() -> None:
    for stmt in DDL:
        op.execute(stmt)


def downgrade() -> None:
    for stmt in [
        "ALTER TABLE jira_tickets DROP COLUMN coverage_note, DROP COLUMN coverage_class",
        "DROP INDEX idx_source_evidence_family",
        "ALTER TABLE source_evidence DROP COLUMN reconciliation_result,"
        " DROP COLUMN reconciled_family_id",
        "ALTER TABLE capability_candidates DROP COLUMN enrichment",
    ]:
        op.execute(stmt)
