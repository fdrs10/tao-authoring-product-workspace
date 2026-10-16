"""UAT structural update (contract: UAT STRUCTURAL UPDATE 2026-10-16).

Revision ID: 0003_uat_structural
Revises: 0002_roadmap_outcomes
Create Date: 2026-10-16

Separates extraction provenance from Product review, prepares source
capabilities for source-by-source reconstruction, and introduces Feature as a
first-class Product composition entity.

Data derivations (deterministic, from existing governed values — nothing
invented):
- capabilities.extraction_origin = 'AI_EXTRACTED' where the existing review
  status records AI extraction ('AI PROPOSED …'); other rows stay NULL until
  source-by-source reconciliation records provenance.
- product_review_status starts NULL everywhere: Product has not reviewed yet
  (NULL = unreviewed; never silently CONFIRMED).
"""

from alembic import op

revision = "0003_uat_structural"
down_revision = "0002_roadmap_outcomes"
branch_labels = None
depends_on = None

DDL = [
    """
ALTER TABLE capabilities
  ADD COLUMN extraction_origin text
    CHECK (extraction_origin IN ('SOURCE_DEFINED','AI_EXTRACTED','AI_ABSTRACTED',
                                 'PRODUCT_CREATED','MANUAL_EXTRACTION')),
  ADD COLUMN product_review_status text
    CHECK (product_review_status IN ('REVIEW_REQUIRED','CONFIRMED',
                                     'CONFIRMED_WITH_CHANGES','REJECTED')),
  ADD COLUMN product_rationale text
""",
    """UPDATE capabilities SET extraction_origin = 'AI_EXTRACTED'
       WHERE review_status LIKE 'AI PROPOSED%'""",
    """
ALTER TABLE source_capabilities
  ADD COLUMN authoring_scope_assessment text,
  ADD COLUMN strategic_category_interpretation text
""",
    """
CREATE TABLE features (
  feat_id    text PRIMARY KEY,
  name       text NOT NULL,
  description text,
  owner      text,
  status     text,
  notes      text,
  version    bigint NOT NULL DEFAULT 1,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
)
""",
    """
CREATE TABLE feature_capabilities (
  feat_id  text NOT NULL REFERENCES features(feat_id) ON DELETE CASCADE,
  cap_id   text NOT NULL REFERENCES capabilities(cap_id),
  added_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (feat_id, cap_id)
)
""",
]

DDL_DOWN = [
    "DROP TABLE feature_capabilities",
    "DROP TABLE features",
    "ALTER TABLE source_capabilities DROP COLUMN strategic_category_interpretation,"
    " DROP COLUMN authoring_scope_assessment",
    "ALTER TABLE capabilities DROP COLUMN product_rationale,"
    " DROP COLUMN product_review_status, DROP COLUMN extraction_origin",
]


def upgrade() -> None:
    for stmt in DDL:
        op.execute(stmt)


def downgrade() -> None:
    for stmt in DDL_DOWN:
        op.execute(stmt)
