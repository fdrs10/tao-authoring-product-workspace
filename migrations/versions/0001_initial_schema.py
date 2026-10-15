"""initial schema — Authoring Product Workspace

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-10-15

Implements db/schema.sql evolved per the Phase 1/Phase 2 implementation contract:
- §9  roadmap_admission NULLABLE (NULL = UNSET; never swallowed by a default)
- §12 analysis/execution budget hours NULLABLE (NULL = not estimated; 0 = explicit zero)
- §19 source_capabilities.reconciliation_relationship
      (SAME / OVERLAP / PARTIAL / SUPPORTS / EVOLVES / DISTINCT)
- §26 markets seeded as governed reference data (approved colour identity
      recovered from legacy v38.6)
- §39 customers/customer_capabilities model present but never seeded
      (real customer dataset supplied later; do not invent customers)
- §51 users table: foundation for multiuser identity/audit (no auth UX yet)
"""

from alembic import op
import sqlalchemy as sa

revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None

DDL = [
    """
CREATE TABLE users (
  user_pk     bigserial PRIMARY KEY,
  user_ref    text UNIQUE NOT NULL,
  display_name text,
  created_at  timestamptz NOT NULL DEFAULT now()
)
""",
    """
CREATE TABLE capabilities (
  cap_id                text PRIMARY KEY,
  working_name          text NOT NULL,
  description           text NOT NULL DEFAULT '',
  strategic_category    text NOT NULL,
  moscow                text,
  visibility            text,
  scope                 text,
  origin                text,
  owner                 text,
  decision              text,
  v2_mapping            text,
  ideation_sheet        text,
  roadmap_admission     text,           -- §9 nullable; NULL = UNSET (Product undecided)
  analysis_budget_hours  numeric,       -- §12 nullable; NULL = not estimated
  execution_budget_hours numeric,
  notes                 text,
  review_status         text,
  version               bigint NOT NULL DEFAULT 1,
  created_at            timestamptz NOT NULL DEFAULT now(),
  updated_at            timestamptz NOT NULL DEFAULT now()
)
""",
    """
CREATE TABLE markets (
  market_id text PRIMARY KEY,
  name      text UNIQUE NOT NULL,
  color     text
)
""",
    """
CREATE TABLE capability_markets (
  cap_id    text NOT NULL REFERENCES capabilities(cap_id),
  market_id text NOT NULL REFERENCES markets(market_id),
  PRIMARY KEY (cap_id, market_id)
)
""",
    """
CREATE TABLE sources (
  source_id           text PRIMARY KEY,
  title               text NOT NULL,
  source_type         text,
  owner               text,
  source_date         text,
  version_label       text,
  document_uri        text,
  summary             text,
  input_form          text,
  upstream_reference  text,
  status              text,
  version             bigint NOT NULL DEFAULT 1
)
""",
    """
CREATE TABLE source_capabilities (
  source_capability_id      text PRIMARY KEY,
  source_id                 text NOT NULL REFERENCES sources(source_id),
  original_name             text,
  original_description      text,
  source_category           text,
  evidence_reference        text,
  source_confidence         text,
  extraction_type           text,
  review_status             text,
  canonical_cap_id          text REFERENCES capabilities(cap_id),
  reconciliation_relationship text,    -- §19 SAME/OVERLAP/PARTIAL/SUPPORTS/EVOLVES/DISTINCT
  notes                     text
)
""",
    """
CREATE TABLE capability_sources (
  cap_id    text NOT NULL REFERENCES capabilities(cap_id),
  source_id text NOT NULL REFERENCES sources(source_id),
  relationship text,
  PRIMARY KEY (cap_id, source_id)
)
""",
    """
CREATE TABLE jira_tickets (
  jira_key          text PRIMARY KEY,
  issue_type        text,
  summary           text,
  description       text,
  status            text,
  lifecycle         text,
  target_release    text,
  due_date          text,
  assignee          text,
  jira_url          text,
  jira_estimate_hours numeric,
  capability_treatment text,   -- EVIDENCE_ONLY / NEEDS_DECOMPOSITION / NON_CAPABILITY / NULL
  reconciliation_rationale text,
  raw_json          jsonb
)
""",
    """
CREATE TABLE capability_jira (
  cap_id   text NOT NULL REFERENCES capabilities(cap_id),
  jira_key text NOT NULL REFERENCES jira_tickets(jira_key),
  relationship text,
  note     text,
  PRIMARY KEY (cap_id, jira_key)
)
""",
    """
CREATE TABLE milestones (
  milestone_id   text PRIMARY KEY,
  name           text NOT NULL,
  milestone_date date,
  scope_type     text,
  scope_ref      text,
  description    text,
  position_month integer,
  version        bigint NOT NULL DEFAULT 1
)
""",
    """
CREATE TABLE roadmap_timing (
  cap_id          text PRIMARY KEY REFERENCES capabilities(cap_id),
  start_month     integer,
  duration_months integer,
  version         bigint NOT NULL DEFAULT 1
)
""",
    """
CREATE TABLE customers (
  customer_id                  text PRIMARY KEY,
  name                         text NOT NULL,
  current_use                  text,
  min_functionality_today      text,
  min_functionality_studio     text,
  desired_outcome              text,
  value_opportunity            text,
  blockers                     text,
  earliest_milestone_interval  text,   -- §40 milestone interval e.g. M3->M4; no TS codes
  validation_status            text,
  notes                        text,
  version                      bigint NOT NULL DEFAULT 1
)
""",
    """
CREATE TABLE customer_capabilities (
  customer_id text NOT NULL REFERENCES customers(customer_id),
  cap_id      text NOT NULL REFERENCES capabilities(cap_id),
  PRIMARY KEY (customer_id, cap_id)
)
""",
    """
CREATE TABLE audit_events (
  audit_id    bigserial PRIMARY KEY,
  entity_type text NOT NULL,
  entity_id   text NOT NULL,
  action      text NOT NULL,
  actor       text,
  before_json jsonb,
  after_json  jsonb,
  created_at  timestamptz NOT NULL DEFAULT now()
)
""",
    "CREATE INDEX ix_source_caps_source ON source_capabilities(source_id)",
    "CREATE INDEX ix_source_caps_cap ON source_capabilities(canonical_cap_id)",
    "CREATE INDEX ix_cap_jira_jira ON capability_jira(jira_key)",
    "CREATE INDEX ix_cap_sources_source ON capability_sources(source_id)",
    "CREATE INDEX ix_cap_markets_market ON capability_markets(market_id)",
    "CREATE INDEX ix_audit_entity ON audit_events(entity_type, entity_id)",
]

# §26 governed market reference data — colour identity recovered from
# legacy v38.6 (approved palette), never invented.
MARKET_SEED = [
    ("MKT-K12",  "Traditional / K-12",            "#4388bd"),
    ("MKT-PRO",  "Professional / Credentialing",  "#8061b5"),
    ("MKT-HED",  "Higher Education",              "#2f99aa"),
    ("MKT-FOR",  "Governed Formative",            "#669b3c"),
    ("MKT-ALE",  "Assessment-led Learning",       "#d77619"),
    ("MKT-MEX",  "MEXCBT / Uchida",               "#c95c5c"),
]


def upgrade() -> None:
    for stmt in DDL:
        op.execute(stmt)
    for market_id, name, color in MARKET_SEED:
        op.get_bind().execute(
            sa.text("INSERT INTO markets (market_id, name, color) "
                    "VALUES (:mid, :name, :color)"),
            {"mid": market_id, "name": name, "color": color},
        )


def downgrade() -> None:
    for table in [
        "audit_events", "customer_capabilities", "customers",
        "roadmap_timing", "milestones", "capability_jira", "jira_tickets",
        "capability_sources", "source_capabilities", "sources",
        "capability_markets", "markets", "capabilities", "users",
    ]:
        op.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
