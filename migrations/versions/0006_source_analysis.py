"""Source-analysis ingestion schema (CONTROLLED OPERATION, contract §20).

Revision ID: 0006_source_analysis
Revises: 0005_report_generations
Create Date: 2026-10-16

- `capabilities.population`: separates HISTORICAL_BASELINE_V1 (the previous
  135-cap baseline — preserved, never active) from
  SOURCE_ANALYSIS_CANDIDATE (the active working population).
- `sources` + evidence_class/authority/extraction_rule (governed Source
  Registry metadata from SOURCE_SET_METADATA).
- `source_evidence`: the 426-signal evidence universe (Source Truth layer).
- `capability_candidates`: the 34 reconciled candidates with focus/disposition
  governance.
"""

from alembic import op

revision = "0006_source_analysis"
down_revision = "0005_report_generations"
branch_labels = None
depends_on = None

DDL = [
    "ALTER TABLE capabilities ADD COLUMN population text",
    """ALTER TABLE sources
       ADD COLUMN evidence_class text,
       ADD COLUMN authority text,
       ADD COLUMN extraction_rule text""",
    """CREATE TABLE source_evidence (
  evidence_id      text PRIMARY KEY,
  source_id        text NOT NULL REFERENCES sources(source_id),
  signal_name      text NOT NULL,
  full_description text,
  evidence_type    text,
  extraction_type  text,
  source_confidence text,
  source_category  text,
  strategic_category text,
  authoring_scope  text,
  market_k12       text,
  market_prof      text,
  market_hed       text,
  market_formative text,
  market_ale       text,
  mexcbt_relevance text,
  market_mapping_basis text,
  evidence_reference text,
  current_canonical_cap_id text,
  current_treatment text,
  feature_composition_status text,
  feature_ids      text,
  notes            text,
  owner_proposer   text,
  provenance       text,
  product_review_status text,
  import_batch     text
)""",
    "CREATE INDEX idx_source_evidence_source ON source_evidence (source_id)",
    """CREATE TABLE capability_candidates (
  candidate_id    text PRIMARY KEY,
  name            text NOT NULL,
  markets         text,
  signals         integer NOT NULL DEFAULT 0,
  independent_sources integer NOT NULL DEFAULT 0,
  source_ids      text,
  evidence_strength text,
  cross_market_leverage text,
  strategy_alignment text,
  mexcbt_signals  integer NOT NULL DEFAULT 0,
  package_status  text,
  is_focus        boolean NOT NULL DEFAULT false,
  focus_markets   text,
  ideation_disposition text NOT NULL DEFAULT 'ACTIVE FOR IDEATION',
  disposition_rationale text,
  promotion_rationale text,
  cap_id          text,
  version         bigint NOT NULL DEFAULT 1,
  created_at      timestamptz NOT NULL DEFAULT now(),
  updated_at      timestamptz NOT NULL DEFAULT now()
)""",
]


def upgrade() -> None:
    for stmt in DDL:
        op.execute(stmt)


def downgrade() -> None:
    for stmt in [
        "DROP TABLE capability_candidates",
        "DROP TABLE source_evidence",
        "ALTER TABLE sources DROP COLUMN extraction_rule, DROP COLUMN authority, DROP COLUMN evidence_class",
        "ALTER TABLE capabilities DROP COLUMN population",
    ]:
        op.execute(stmt)
