"""Phase 3 API tests — pytest fixtures.

A dedicated throwaway database ``tao_authoring_test`` is created on the
local docker-compose Postgres, fully migrated, truncated and seeded per
test. The app reads DATABASE_URL at import time, so it must be pointed at
the test database *before* ``app.main`` is imported inside the client
fixture.
"""

import os
import subprocess
import sys
import time
from pathlib import Path

import psycopg
import pytest

REPO = Path(__file__).resolve().parents[2]
TEST_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql://tao:tao_dev_password@localhost:54323/tao_authoring_test")
ADMIN_URL = "postgresql://tao:tao_dev_password@localhost:54323/postgres"

os.environ["DATABASE_URL"] = TEST_URL  # must precede any app import
os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault("LOG_FORMAT", "text")

TRUNCATE = [
    "audit_events", "customer_capabilities", "customers",
    "capability_jira", "jira_tickets", "capability_sources",
    "source_capabilities", "sources", "capability_markets",
    "roadmap_timing", "milestones", "capabilities", "users",
]

SEED_CAP = """
INSERT INTO capabilities (cap_id, working_name, description,
  strategic_category, moscow, visibility, scope, origin, owner, decision,
  v2_mapping, ideation_sheet, roadmap_admission, notes, review_status)
VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
"""


def wait_for_postgres(n=30):
    for i in range(n):
        try:
            psycopg.connect(ADMIN_URL, connect_timeout=2).close()
            return
        except Exception:
            time.sleep(1)
    raise RuntimeError("postgres not reachable (is docker compose db up?)")


@pytest.fixture(scope="session", autouse=True)
def prepare_database():
    wait_for_postgres()
    with psycopg.connect(ADMIN_URL, autocommit=True) as conn:
        conn.execute(
            "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
            "WHERE datname='tao_authoring_test' AND pid <> pg_backend_pid()")
        conn.execute("DROP DATABASE IF EXISTS tao_authoring_test")
        conn.execute("CREATE DATABASE tao_authoring_test")
    subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=REPO,
        env={**os.environ, "DATABASE_URL":
             TEST_URL.replace("postgresql://", "postgresql+psycopg://")},
        check=True, capture_output=True, text=True)


@pytest.fixture(autouse=True)
def reset_data():
    with psycopg.connect(TEST_URL, autocommit=True) as conn:
        conn.execute(
            "TRUNCATE " + ", ".join(TRUNCATE) + " RESTART IDENTITY CASCADE")
        conn.execute(SEED_CAP, (
            "CAP-9001", "Test capability alpha", "alpha description",
            "Create & Design", "Must", "Shared / common core", "V2 candidate",
            "v1", None, "Keep as-is", "CAP-9001", "V1 Carry-forward", None,
            None, "AI PROPOSED · PRODUCT REVIEW REQUIRED"))
        conn.execute(SEED_CAP, (
            "CAP-9002", "Test capability beta", "beta description",
            "Standards & Portability", "Should", "Market-specific", "V2 candidate",
            "new", None, "DEVELOP / VALIDATE", "CAP-9002",
            "New Needs & Gaps / Developments", "Candidate", None, None))
        conn.execute(
            "INSERT INTO capability_markets (cap_id, market_id) VALUES "
            "('CAP-9001','MKT-K12'), ('CAP-9002','MKT-K12'), ('CAP-9002','MKT-PRO')")
        conn.execute(
            "INSERT INTO sources (source_id, title, source_type, status) "
            "VALUES ('SRC-TEST-001','Test Source Doc','TestType','REGISTERED')")
        conn.execute(
            """INSERT INTO source_capabilities
                 (source_capability_id, source_id, original_name,
                  canonical_cap_id, reconciliation_relationship)
               VALUES ('SC-TEST-0001','SRC-TEST-001','Original alpha',
                       'CAP-9001','EVOLVES')""")
        conn.execute(
            "INSERT INTO capability_sources (cap_id, source_id, relationship) "
            "VALUES ('CAP-9001','SRC-TEST-001','CANONICAL_SOURCE')")
        conn.execute(
            """INSERT INTO jira_tickets
                 (jira_key, issue_type, summary, status, jira_url)
               VALUES ('PCR-TEST-1','Epic','Test epic','In Progress',
                       'https://oat-sa.atlassian.net/browse/PCR-TEST-1')""")
        conn.execute(
            "INSERT INTO roadmap_timing (cap_id, start_month, duration_months, version) "
            "VALUES ('CAP-9001', 0, 3, 1)")
    yield


@pytest.fixture()
def client():
    from fastapi.testclient import TestClient

    from app.main import app

    return TestClient(app)
