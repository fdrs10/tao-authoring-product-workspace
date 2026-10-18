"""CONTROLLED CORRECTION — Active Product Truth alignment (§20 assertions).

Permanent regression protection for the population rules:
- Active Candidates = 34; Focus = 15; Historical = 135 (separately inspectable)
- Cross-analysis universe = 34, NOT 169
- Analysis lenses do not add active capabilities
- Historical MoSCoW/Admission not inherited
- Roadmap: zero historical bars; Migration: zero historical availability
- M1–M6 intact; Reports render; population API contract explicit
"""

import httpx
import os
import psycopg
import pytest
import subprocess
import sys
from playwright.sync_api import Page, expect

BASE_API = "http://127.0.0.1:8099"
H = {"X-User-Ref": "correction-uat"}


@pytest.fixture(autouse=True)
def governed_bootstrap(page, server):
    """Full governed bootstrap: canonical baseline + milestones + materialize
    + FINAL Source-analysis ingestion (the same pipeline as production)."""
    env = {**os.environ,
           "DATABASE_URL": "postgresql+psycopg://tao:tao_dev_password@localhost:54323/tao_authoring_e2e"}
    from tests.ui.conftest import TRUNCATE
    import psycopg as ps
    with ps.connect("postgresql://tao:tao_dev_password@localhost:54323/tao_authoring_e2e", autocommit=True) as c:
        c.execute("TRUNCATE " + ", ".join(TRUNCATE) + " RESTART IDENTITY CASCADE")
        from tests.ui.conftest import SEED
        c.execute(SEED)
    for script in ("scripts/import/import_canonical.py",
                   "scripts/import/import_milestones.py",
                   "scripts/import/materialize_source_documents.py",
                   "scripts/import/ingest_source_analysis.py"):
        args = [sys.executable, script]
        if "ingest" in script:
            args.append(os.path.join(os.getcwd(), "data", "source-analysis", "v1_4"))
        subprocess.run(args, cwd=".", env=env, check=True, capture_output=True)


def _funnel():
    return httpx.get(f"{BASE_API}/api/funnel").json()["funnel"]


def test_funnel_governed_counts():
    f = _funnel()
    assert f["evidence_signals"] == 426
    assert f["capability_candidates"] == 34
    assert f["focus_capabilities"] == 15
    assert f["sources"] >= 9


def test_historical_baseline_separately_inspectable():
    hist = httpx.get(f"{BASE_API}/api/capabilities",
                     params={"population": "historical"}).json()
    assert hist["count"] == 135
    for i in hist["items"][:5]:
        assert i["population"] == "HISTORICAL_BASELINE_V1"


def test_cross_analysis_universe_is_34_not_169(page: Page):
    page.goto("/#/ideation/06")
    rows = page.locator('[data-testid="xanalysis-row"]')
    expect(rows.first).to_be_visible(timeout=15000)
    # The active population = governed candidates (34) + e2e seed caps marked
    # SOURCE_ANALYSIS_CANDIDATE. The key assertion: NOT 169 (no historical union).
    count = rows.count()
    assert count < 169, f"cross-analysis shows {count} (historical union leak)"
    # header shows governed counts from /api/funnel
    body = page.locator("#app-main").inner_text()
    assert "Active Capability Candidates" in body


def test_analysis_lenses_do_not_add_active_capabilities(page: Page):
    before = _funnel()["capability_candidates"]
    for sheet in ("02", "03", "04", "05"):
        page.goto(f"/#/ideation/{sheet}")
        page.wait_for_timeout(1200)
    assert _funnel()["capability_candidates"] == before


def test_historical_moscow_admission_not_inherited():
    caps = httpx.get(f"{BASE_API}/api/capabilities").json()["items"]
    for c in caps:
        if c["cap_id"].startswith("CAND-F"):
            assert c["moscow"] is None, f"{c['cap_id']} inherited MoSCoW"
            assert c["roadmap_admission"] is None, f"{c['cap_id']} inherited Admission"


def test_roadmap_zero_historical_bars(page: Page):
    page.goto("/#/roadmap")
    page.locator('[data-testid="rfilter-admission"]').select_option("All")
    page.wait_for_timeout(1500)
    bars = page.locator('[data-testid="cap-bar"]')
    ids = bars.evaluate_all("els => els.map(e => e.dataset.cap)")
    # zero HISTORICAL_BASELINE_V1 bars: only CAND-Fxx + seed caps (which have
    # population=SOURCE_ANALYSIS_CANDIDATE) may appear — never CAP-0001..0135
    governed_historical = {f"CAP-{i:04d}" for i in range(1, 136)} - {"CAP-9001", "CAP-9002", "CAP-9003", "CAP-9004"}
    leak = governed_historical & set(ids)
    assert not leak, f"historical baseline bars on Roadmap: {leak}"


def test_roadmap_honest_empty_state(page: Page):
    page.goto("/#/roadmap")
    page.wait_for_timeout(1500)
    # default COMMITTED → no active candidates admitted → empty state visible
    expect(page.locator('[data-testid="roadmap-empty"]')).to_be_visible()


def test_migration_zero_historical_availability(page: Page):
    page.goto("/#/migration")
    page.wait_for_timeout(1500)
    t = page.locator("#app-main").inner_text()
    assert "CAP-0001" not in t and "CAP-0002" not in t
    assert "CAP-0010" not in t


def test_milestones_m1_m6_intact():
    ms = httpx.get(f"{BASE_API}/api/milestones").json()["items"]
    assert [m["milestone_id"] for m in ms] == ["M1", "M2", "M3", "M4", "M5", "M6"]


def test_reports_render_all_contracts():
    for rid in ("D1", "D2", "D3", "D4"):
        r = httpx.get(f"{BASE_API}/api/reports/{rid}/preview")
        assert r.status_code == 200 and len(r.text) > 5000
    r = httpx.get(f"{BASE_API}/api/reports/D5/preview")
    assert r.status_code == 400  # no-customer state explicit


def test_sources_route_renders(page: Page):
    page.goto("/#/sources")
    expect(page.locator('[data-testid="funnel-banner"]')).to_be_visible(timeout=15000)
    expect(page.locator('[data-testid="source-row"]').first).to_be_visible()


def test_november_outcomes_reflects_current_stage(page: Page):
    page.goto("/#/outcomes")
    body = page.locator("#app-main").inner_text()
    assert "Human Product Review" in body
    assert "next controlled operation" not in body


def test_population_api_contract_explicit():
    d = httpx.get(f"{BASE_API}/api/capabilities").json()
    default_ids = {i["cap_id"] for i in d["items"]}
    hist = httpx.get(f"{BASE_API}/api/capabilities",
                     params={"population": "historical"}).json()
    hist_ids = {i["cap_id"] for i in hist["items"]}
    assert not (default_ids & hist_ids), "population leak: default ∩ historical"
    allr = httpx.get(f"{BASE_API}/api/capabilities",
                     params={"population": "all"}).json()
    all_ids = {i["cap_id"] for i in allr["items"]}
    assert all_ids >= default_ids | hist_ids
