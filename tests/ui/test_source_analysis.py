"""CONTROLLED OPERATION — Source-analysis ingestion + funnel regression (§21/§22).

All fixtures live in the throwaway e2e database; governed data untouched.
"""

import httpx
import pytest
from playwright.sync_api import Page, expect

BASE_API = "http://127.0.0.1:8099"
H = {"X-User-Ref": "ingest-uat"}


@pytest.fixture(scope="module", autouse=True)
def ingested(server):
    """Governed baselines + ingestion once per module (all idempotent):
    old canonical baseline → milestone baseline → source-analysis package."""
    import subprocess
    env = {**__import__("os").environ,
           "DATABASE_URL": "postgresql+psycopg://tao:tao_dev_password@localhost:54323/tao_authoring_e2e"}
    for script in ("scripts/import/import_canonical.py",
                   "scripts/import/import_milestones.py",
                   "scripts/import/materialize_source_documents.py",
                   "scripts/import/ingest_source_analysis.py",
                   "scripts/product_review/enrich_candidates.py"):
        subprocess.run([sys_path(), script,
                        "/Users/felixdiaz/.kimchi/docs/v1_4_extract/TAO_Authoring_Capability_Evidence_Focus_Guide_v1_4_VERIFIED"
                        if "ingest" in script else ""],
                       cwd=".", env=env, check=True, capture_output=True)


def sys_path():
    import sys
    return sys.executable


def _reingest():
    import subprocess
    env = {**__import__("os").environ,
           "DATABASE_URL": "postgresql+psycopg://tao:tao_dev_password@localhost:54323/tao_authoring_e2e"}
    subprocess.run([sys_path(), "scripts/import/ingest_source_analysis.py",
                    "/Users/felixdiaz/Projects/tao-authoring-product-workspace/data/source-analysis/v1_4"],
                   cwd=".", env=env, check=True, capture_output=True)


# ---------- Funnel + population ----------

def test_funnel_counts_match_governed_package():
    f = httpx.get(f"{BASE_API}/api/funnel").json()["funnel"]
    assert f["evidence_signals"] == 426
    assert f["capability_candidates"] == 34
    assert f["focus_capabilities"] == 15
    assert f["historical_baseline"] == 135
    srcs = {s["source_id"] for s in httpx.get(f"{BASE_API}/api/sources").json()["items"]}
    governed = {"SRC-3X-001", "SRC-V1-001", "SRC-GAP-001", "SRC-NEW-001",
                "SRC-COMP-001", "SRC-JIRA-001", "SRC-OECD-001",
                "SRC-NYSED-001", "SRC-STRATEGY-001"}
    assert governed <= srcs            # all 9 governed sources registered


def test_default_population_is_active_candidates_not_135():
    active = httpx.get(f"{BASE_API}/api/capabilities").json()
    assert active["count"] >= 34
    ids = [i["cap_id"] for i in active["items"]]
    assert len(ids) == len(set(ids))                  # no duplicates
    assert "CAP-0001" not in ids                      # historical baseline excluded
    assert sum(1 for i in ids if i.startswith("CAND-F")) >= 34
    hist = httpx.get(f"{BASE_API}/api/capabilities",
                     params={"population": "historical"}).json()
    assert hist["count"] == 135
    allrows = httpx.get(f"{BASE_API}/api/capabilities",
                        params={"population": "all"}).json()
    # 135 historical + 34 candidates (+ any capability later created by other
    # suites' Product actions, e.g. promotions — order-dependent extras allowed)
    assert allrows["count"] >= hist["count"] + 34


def test_evidence_universe_and_source_lineage():
    ev = httpx.get(f"{BASE_API}/api/evidence").json()
    assert ev["count"] == 426
    srcs = {e["source_id"] for e in ev["items"] if True} | {
        e["source_id"] for e in
        httpx.get(f"{BASE_API}/api/evidence", params={"limit": 500, "offset": 400}).json()["items"]}
    assert srcs <= {"SRC-3X-001", "SRC-V1-001", "SRC-GAP-001", "SRC-NEW-001",
                    "SRC-COMP-001", "SRC-JIRA-001", "SRC-OECD-001",
                    "SRC-NYSED-001", "SRC-STRATEGY-001"}
    for e in ev["items"]:
        assert e["source_id"]                          # every record has lineage


def test_mexcbt_dimension_works_independently():
    ev = httpx.get(f"{BASE_API}/api/evidence", params={"limit": 500}).json()["items"]
    mex = [e for e in ev if (e["mexcbt_relevance"] or "").upper() == "YES"]
    assert mex, "package must contain MEXCBT-relevant signals"
    cand = httpx.get(f"{BASE_API}/api/candidates", params={"mexcbt_only": "1"}).json()
    assert cand["count"] > 0
    assert all(c["mexcbt_signals"] > 0 for c in cand["items"])


# ---------- Candidates governance ----------

def test_candidates_focus_subset_no_duplicates():
    all_c = httpx.get(f"{BASE_API}/api/candidates").json()["items"]
    focus = httpx.get(f"{BASE_API}/api/candidates", params={"focus": "yes"}).json()["items"]
    assert len(all_c) == 34 and len(focus) == 15
    all_ids = [c["candidate_id"] for c in all_c]
    assert len(all_ids) == len(set(all_ids))
    for f in focus:
        assert f["candidate_id"] in all_ids
        assert f["is_focus"] is True


def test_candidate_disposition_change_requires_rationale_and_version():
    c0 = httpx.get(f"{BASE_API}/api/candidates").json()["items"][0]
    cid, v = c0["candidate_id"], c0["version"]
    # no rationale → 422
    r = httpx.patch(f"{BASE_API}/api/candidates/{cid}", headers=H,
                    json={"version": v, "ideation_disposition": "NOT SELECTED FOR IDEATION"})
    assert r.status_code == 422
    # bad disposition → 422
    r = httpx.patch(f"{BASE_API}/api/candidates/{cid}", headers=H,
                    json={"version": v, "ideation_disposition": "DELETED", "rationale": "because"})
    assert r.status_code == 422
    # valid → 200, audited, NOT deleted
    r = httpx.patch(f"{BASE_API}/api/candidates/{cid}", headers=H,
                    json={"version": v, "ideation_disposition": "NOT SELECTED FOR IDEATION",
                          "rationale": "Product decision: out of first-release scope"})
    assert r.status_code == 200
    row = httpx.get(f"{BASE_API}/api/candidates").json()["items"]
    row = [c for c in row if c["candidate_id"] == cid][0]
    assert row["ideation_disposition"] == "NOT SELECTED FOR IDEATION"
    # funnel active count dropped (34 → 33)
    assert httpx.get(f"{BASE_API}/api/funnel").json()["funnel"]["capability_candidates"] == 33
    # restore
    httpx.patch(f"{BASE_API}/api/candidates/{cid}", headers=H,
                json={"version": row["version"], "ideation_disposition": "ACTIVE FOR IDEATION",
                      "rationale": "restored for UAT"})
    assert httpx.get(f"{BASE_API}/api/funnel").json()["funnel"]["capability_candidates"] == 34


def test_candidate_stale_update_409():
    c0 = httpx.get(f"{BASE_API}/api/candidates").json()["items"][0]
    r = httpx.patch(f"{BASE_API}/api/candidates/{c0['candidate_id']}", headers=H,
                    json={"version": c0["version"] - 1 if c0["version"] > 1 else 99,
                          "rationale": "stale"})
    assert r.status_code in (409, 422)   # version mismatch → 409


def test_promote_evidence_to_candidate():
    ev = httpx.get(f"{BASE_API}/api/evidence", params={"limit": 500}).json()["items"]
    target = next(e for e in ev if (e["current_treatment"] or "") == "UNRECONCILED")
    before = httpx.get(f"{BASE_API}/api/funnel").json()["funnel"]["capability_candidates"]
    # no rationale → 422
    r = httpx.post(f"{BASE_API}/api/candidates/F01/promote", headers=H,
                   json={"evidence_id": target["evidence_id"], "name": "Promoted without rationale"})
    assert r.status_code == 422
    r = httpx.post(f"{BASE_API}/api/candidates/F01/promote", headers=H,
                   json={"evidence_id": target["evidence_id"],
                         "name": "Promoted UAT capability",
                         "rationale": "Product review: signal merits standalone candidacy"})
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["lineage"]["source_evidence"] == target["evidence_id"]
    after = httpx.get(f"{BASE_API}/api/funnel").json()["funnel"]["capability_candidates"]
    assert after == before + 1
    # promoted candidate is active + lineage preserved
    row = httpx.get(f"{BASE_API}/api/candidates").json()["items"]
    row = [c for c in row if c["candidate_id"] == body["candidate_id"]][0]
    assert row["ideation_disposition"] == "ACTIVE FOR IDEATION"
    assert target["source_id"] in (row["source_ids"] or "")
    # cleanup: mark NOT SELECTED so other tests keep the governed 34 active
    httpx.patch(f"{BASE_API}/api/candidates/{body['candidate_id']}", headers=H,
                json={"version": 1, "ideation_disposition": "NOT SELECTED FOR IDEATION",
                      "rationale": "UAT promotion test — retired from active set"})


def test_promote_unknown_evidence_404():
    r = httpx.post(f"{BASE_API}/api/candidates/F01/promote", headers=H,
                   json={"evidence_id": "NOPE-999", "name": "x", "rationale": "because reasons"})
    assert r.status_code == 404


# ---------- Ideation consumes active population ----------

def test_ideation_shows_active_candidates(page: Page):
    _reingest()   # page fixture truncates candidates — re-apply governed ingestion
    page.goto("/#/ideation/00")
    rows = page.locator('[data-testid="candidate-row"]')
    expect(rows.first).to_be_visible(timeout=15000)
    expect(rows).to_have_count(34, timeout=10000)
    # Focus filter → 15
    page.locator('[data-testid="candidate-filters"] select[data-cf="focus"]').select_option("yes")
    expect(rows).to_have_count(15, timeout=10000)
    # MEXCBT filter works independently (combined with Focus)
    page.locator('[data-testid="candidate-filters"] select[data-cf="mexcbt"]').select_option("yes")
    expect(page.locator('[data-testid="candidate-count"]')).to_contain_text("Showing")
    # Clear restores 34
    page.locator('[data-testid="cand-filter-clear"]').click()
    expect(rows).to_have_count(34, timeout=10000)


def test_sources_funnel_banner_and_tabs(page: Page):
    _reingest()
    page.goto("/#/sources")
    expect(page.locator('[data-testid="funnel-banner"]')).to_contain_text("426 Evidence Signals")
    expect(page.locator('[data-testid="funnel-banner"]')).to_contain_text("34 Capability Candidates")
    for tab in ("tab-evidence", "tab-analysis", "tab-candidates", "tab-focus"):
        expect(page.locator(f'[data-testid="{tab}"]')).to_be_visible()
    page.locator('[data-testid="tab-evidence"]').click()
    expect(page.locator('[data-testid="evidence-row"]').first).to_be_visible()
    page.locator('[data-testid="tab-candidates"]').click()
    expect(page.locator('[data-testid="candidate-analysis-row"]').first).to_be_visible()
