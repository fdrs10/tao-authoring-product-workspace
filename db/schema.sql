-- Initial target schema. Kinchi may evolve through migrations, preserving semantics.
CREATE TABLE capabilities (
  cap_id text PRIMARY KEY, working_name text NOT NULL, description text NOT NULL DEFAULT '',
  strategic_category text NOT NULL, moscow text, visibility text, scope text, origin text, owner text,
  decision text, v2_mapping text, roadmap_admission text NOT NULL DEFAULT 'Backlog',
  analysis_budget_hours numeric NOT NULL DEFAULT 0, execution_budget_hours numeric NOT NULL DEFAULT 0,
  notes text, version bigint NOT NULL DEFAULT 1, created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE markets (market_id text PRIMARY KEY, name text UNIQUE NOT NULL);
CREATE TABLE capability_markets (cap_id text REFERENCES capabilities(cap_id), market_id text REFERENCES markets(market_id), PRIMARY KEY(cap_id,market_id));
CREATE TABLE sources (source_id text PRIMARY KEY, title text NOT NULL, source_type text, owner text, source_date text, version_label text, document_uri text, summary text, version bigint NOT NULL DEFAULT 1);
CREATE TABLE source_capabilities (source_capability_id text PRIMARY KEY, source_id text NOT NULL REFERENCES sources(source_id), original_name text, original_description text, evidence_reference text, extraction_type text, canonical_cap_id text REFERENCES capabilities(cap_id));
CREATE TABLE capability_sources (cap_id text REFERENCES capabilities(cap_id), source_id text REFERENCES sources(source_id), relationship text, PRIMARY KEY(cap_id,source_id));
CREATE TABLE jira_tickets (jira_key text PRIMARY KEY, summary text, description text, status text, lifecycle text, target_release text, due_date text, assignee text, jira_url text, raw_json jsonb);
CREATE TABLE capability_jira (cap_id text REFERENCES capabilities(cap_id), jira_key text REFERENCES jira_tickets(jira_key), relationship text, note text, PRIMARY KEY(cap_id,jira_key));
CREATE TABLE milestones (milestone_id text PRIMARY KEY, name text NOT NULL, milestone_date date, scope_type text, scope_ref text, description text, position_month integer, version bigint NOT NULL DEFAULT 1);
CREATE TABLE roadmap_timing (cap_id text PRIMARY KEY REFERENCES capabilities(cap_id), start_month integer, duration_months integer, version bigint NOT NULL DEFAULT 1);
CREATE TABLE customers (customer_id text PRIMARY KEY, name text NOT NULL, current_use text, min_functionality_today text, min_functionality_studio text, desired_outcome text, value_opportunity text, blockers text, earliest_milestone_interval text, validation_status text, notes text, version bigint NOT NULL DEFAULT 1);
CREATE TABLE customer_capabilities (customer_id text REFERENCES customers(customer_id), cap_id text REFERENCES capabilities(cap_id), PRIMARY KEY(customer_id,cap_id));
CREATE TABLE audit_events (audit_id bigserial PRIMARY KEY, entity_type text NOT NULL, entity_id text NOT NULL, action text NOT NULL, actor text, before_json jsonb, after_json jsonb, created_at timestamptz NOT NULL DEFAULT now());
