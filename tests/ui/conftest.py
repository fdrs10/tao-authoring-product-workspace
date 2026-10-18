"""Phase 4 UI E2E fixtures: migrated throwaway DB + deterministic seed +
real uvicorn server + headless Chromium. Blank-screen guard: any page
JavaScript error fails the test (§55)."""

import os
import subprocess
import sys
import time
from pathlib import Path

import httpx
import psycopg
import pytest
from playwright.sync_api import sync_playwright

REPO = Path(__file__).resolve().parents[2]
TEST_URL = "postgresql://tao:tao_dev_password@localhost:54323/tao_authoring_e2e"
ADMIN_URL = "postgresql://tao:tao_dev_password@localhost:54323/postgres"
PORT = 8099
BASE = f"http://127.0.0.1:{PORT}"

# NOTE: no module-level os.environ write here. app.main binds DATABASE_URL at
# import time; mutating the process env would retarget the in-process API
# TestClient (tests/api) to the e2e database when both suites run together.
# The uvicorn subprocess below receives its DATABASE_URL explicitly.

SEED = """
INSERT INTO capabilities (cap_id, working_name, description, strategic_category,
  moscow, visibility, scope, origin, owner, decision, v2_mapping, ideation_sheet,
  roadmap_admission, analysis_budget_hours, execution_budget_hours, review_status,
  population)
VALUES
 ('CAP-9001','Alpha item authoring','Full alpha description','Create & Design','Must',
  'Shared / common core','V2 candidate','v1','Owner A','Keep as-is','CAP-9001',
  'V1 Carry-forward',NULL,NULL,NULL,'AI PROPOSED · PRODUCT REVIEW REQUIRED',
  'SOURCE_ANALYSIS_CANDIDATE'),
 ('CAP-9002','Beta QTI export','Full beta description','Standards & Portability','Should',
  'Market-specific','V2 candidate','new','Owner B','DEVELOP / VALIDATE','CAP-9002',
  'New Needs & Gaps / Developments','Candidate',NULL,NULL,'PRODUCT_SCOPE_REVIEW_REQUIRED',
  'SOURCE_ANALYSIS_CANDIDATE'),
 ('CAP-9003','Gamma zero budgets','Full gamma description','Create & Design','Must',
  'Shared / common core','V2 candidate','v1','Owner C','Keep as-is','CAP-9003',
  'V1 Carry-forward',NULL,0,0,NULL,'SOURCE_ANALYSIS_CANDIDATE'),
 ('CAP-9004','Delta null budgets','Full delta description','Manage & Govern','Should',
  'Shared / market-configured','V2 candidate','3x','Owner D','Migrate / recreate','CAP-9004',
  '3.x Direct Migration to V2',NULL,NULL,NULL,NULL,
  'SOURCE_ANALYSIS_CANDIDATE');
INSERT INTO capability_markets (cap_id, market_id) VALUES
 ('CAP-9001','MKT-K12'), ('CAP-9002','MKT-K12'), ('CAP-9002','MKT-PRO'),
 ('CAP-9003','MKT-K12'), ('CAP-9003','MKT-ALE'), ('CAP-9004','MKT-FOR')
ON CONFLICT DO NOTHING;
INSERT INTO sources (source_id, title, source_type, owner, status, document_uri,
                     evidence_class, authority, extraction_rule)
VALUES
 ('SRC-TEST-001','Test Source Doc','TestType','Owner S','REGISTERED','data/raw/test.pdf',NULL,NULL,NULL),
 ('SRC-JIRA-001','Current Authoring Jira Backlog','Operational / Delivery Evidence',NULL,'REGISTERED','local://SRC-JIRA-001/JIRA_current_backlog.csv','Delivery Evidence','HIGH','CSV export; tickets verbatim'),
 ('SRC-3X-001','TAO Authoring - feature list','Product Capability Baseline','Dragos Ivan','REGISTERED',NULL,'Existing Product Baseline','HIGH','Literal feature list; names/descriptions preserved'),
 ('SRC-V1-001','TAO Studio - feature list','Product Capability Baseline','Dragos Ivan','REGISTERED',NULL,'Existing Product Baseline','HIGH','Literal feature list; names/descriptions preserved'),
 ('SRC-NEW-001','TAO Authoring Strategic Initiative','Strategic Initiative','Product','REGISTERED',NULL,'Strategic Direction','MEDIUM','User-provided text; abstraction recorded'),
 ('SRC-COMP-001','TAO AI Competitor Intelligence Report','Competitor Intelligence','Product','REGISTERED',NULL,'Competitor Intelligence','MEDIUM','User-provided report text; abstraction recorded'),
 ('SRC-OECD-001','OECD Digital Education Outlook 2026: Exploring Effective Uses of Generative AI in Education','External Report','OECD','REGISTERED','local://SRC-OECD-001/OECD_Digital_Education_Outlook_2026.pdf','External Report','HIGH','Uploaded PDF; abstraction recorded'),
 ('SRC-HTML-001','Existing TAO Authoring HTML capability seed','Product Capability Baseline',NULL,'REGISTERED',NULL,'Existing Product Baseline','LOW','Requires evidence reconciliation before promotion'),
 ('SRC-GAP-001','TAO Authoring - TAO Studio gap analysis','Gap Analysis','Product','REGISTERED','local://SRC-GAP-001/SRC_GAP_TAO_3X_VS_STUDIO_V1.txt','Gap Analysis','HIGH','Confluence copy/paste; preserved verbatim'),
 ('SRC-NYSED-001','3.x features and enhancements (NYSED)','Customer Requirements','NYSED','REGISTERED',NULL,'Customer Requirements','HIGH','Original docx; literal extraction'),
 ('SRC-STRATEGY-001','OAT 18 + 18 Months Strategy - Product and Markets','Strategy','Product','REGISTERED',NULL,'Strategic Direction','HIGH','Original docx; strategy analysis read-only view');
INSERT INTO source_capabilities (source_capability_id, source_id, original_name,
  original_description, canonical_cap_id, reconciliation_relationship, evidence_reference)
VALUES ('SC-TEST-0001','SRC-TEST-001','Original alpha','orig alpha desc','CAP-9001','EVOLVES','§3.2');
INSERT INTO capability_sources (cap_id, source_id, relationship) VALUES
 ('CAP-9001','SRC-TEST-001','CANONICAL_SOURCE'), ('CAP-9002','SRC-JIRA-001','CANONICAL_SOURCE');
INSERT INTO jira_tickets (jira_key, issue_type, summary, status, lifecycle,
  target_release, jira_url, capability_treatment)
VALUES ('PCR-TEST-1','Epic','Test epic summary','In Progress','DoR','R1b',
        'https://oat-sa.atlassian.net/browse/PCR-TEST-1',NULL);
INSERT INTO capability_jira (cap_id, jira_key, relationship, note)
VALUES ('CAP-9002','PCR-TEST-1','DELIVERY_EVIDENCE',NULL);
INSERT INTO roadmap_timing (cap_id, start_month, duration_months, version) VALUES
 ('CAP-9001',0,3,1);
"""

TRUNCATE = [
    "audit_events", "customer_capabilities", "customers",
    "capability_jira", "jira_tickets", "capability_sources",
    "source_capabilities", "sources", "capability_markets",
    "roadmap_timing", "milestones", "capabilities", "users",
    "feature_capabilities", "features", "report_generations",
    "capability_candidates", "source_evidence",
]


def wait_postgres():
    for i in range(30):
        try:
            psycopg.connect(ADMIN_URL, connect_timeout=2).close()
            return
        except Exception:
            time.sleep(1)
    raise RuntimeError("postgres unreachable")


@pytest.fixture(scope="session", autouse=True)
def server():
    wait_postgres()
    with psycopg.connect(ADMIN_URL, autocommit=True) as conn:
        conn.execute(
            "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
            "WHERE datname='tao_authoring_e2e' AND pid<>pg_backend_pid()")
        conn.execute("DROP DATABASE IF EXISTS tao_authoring_e2e")
        conn.execute("CREATE DATABASE tao_authoring_e2e")
    subprocess.run([sys.executable, "-m", "alembic", "upgrade", "head"],
                   cwd=REPO, env={**os.environ, "DATABASE_URL":
                                  TEST_URL.replace("postgresql://", "postgresql+psycopg://")},
                   check=True, capture_output=True, text=True)
    # governed baselines that ship with the product (idempotent imports):
    # M1–M6 milestone dataset + source-document materialization/coverage
    for script in ("scripts/import/import_milestones.py",
                   "scripts/import/materialize_source_documents.py"):
        subprocess.run([sys.executable, script], cwd=REPO,
                       env={**os.environ, "DATABASE_URL":
                            TEST_URL.replace("postgresql://", "postgresql+psycopg://")},
                       check=True, capture_output=True, text=True)

    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--port", str(PORT)],
        cwd=REPO, env={**os.environ, "DATABASE_URL":
                       TEST_URL.replace("postgresql://", "postgresql+psycopg://"),
                       "APP_ENV": "test", "LOG_FORMAT": "text"},
        # DEVNULL: an unread PIPE fills (~64KB) and BLOCKS the server mid-run
        # (late-session Page.goto timeouts). Diagnostics use /health polling.
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for i in range(60):
        try:
            if httpx.get(f"{BASE}/health/db", timeout=2).status_code == 200:
                break
        except Exception:
            time.sleep(0.5)
    else:
        proc.kill()
        raise RuntimeError("uvicorn did not come up")
    yield BASE
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()


@pytest.fixture()
def page(server):
    with psycopg.connect(TEST_URL, autocommit=True) as conn:
        conn.execute("TRUNCATE " + ", ".join(TRUNCATE) + " RESTART IDENTITY CASCADE")
        conn.execute(SEED)
    # governed baselines are re-applied after truncation (all imports are
    # deterministic + idempotent): M1–M6 milestones, source artifacts/URI, and
    # the FINAL Source-analysis package. NOTE: TRUNCATE sources CASCADE wipes
    # source_evidence — the ingestion must re-run after every truncation.
    for script in ("scripts/import/import_milestones.py",
                   "scripts/import/materialize_source_documents.py"):
        subprocess.run([sys.executable, script], cwd=REPO,
                       env={**os.environ, "DATABASE_URL":
                            TEST_URL.replace("postgresql://", "postgresql+psycopg://")},
                       check=True, capture_output=True, text=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(base_url=server)
        page_errors = []
        page.on("pageerror", lambda exc: page_errors.append(str(exc)))
        yield page
        assert not page_errors, f"page JS errors (blank-screen guard §55): {page_errors}"
        browser.close()
