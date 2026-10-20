"""Phase A: PM Shell + Collaboration Foundation.

Revision ID: 0008_phase_a_collaboration
Revises: 0007_candidate_enrichment
Create Date: 2026-10-16

- comments table (polymorphic discussion threads)
- owner on capability_candidates (PM accountability)
- review_requested boolean on capability_candidates
"""

from alembic import op

revision = "0008_phase_a_collaboration"
down_revision = "0007_candidate_enrichment"
branch_labels = None
depends_on = None

DDL = [
    """CREATE TABLE comments (
  comment_id  bigserial PRIMARY KEY,
  entity_type text NOT NULL,
  entity_id   text NOT NULL,
  parent_id   bigint REFERENCES comments(comment_id),
  author      text NOT NULL,
  comment     text NOT NULL,
  resolved    boolean NOT NULL DEFAULT false,
  created_at  timestamptz NOT NULL DEFAULT now()
)""",
    "CREATE INDEX idx_comments_entity ON comments (entity_type, entity_id)",
    """ALTER TABLE capability_candidates
       ADD COLUMN owner text,
       ADD COLUMN review_requested boolean NOT NULL DEFAULT false""",
]

DDL_DOWN = [
    "ALTER TABLE capability_candidates DROP COLUMN review_requested, DROP COLUMN owner",
    "DROP TABLE comments",
]


def upgrade() -> None:
    for stmt in DDL:
        op.execute(stmt)


def downgrade() -> None:
    for stmt in DDL_DOWN:
        op.execute(stmt)
