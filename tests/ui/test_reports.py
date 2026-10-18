"""FINAL STRUCTURAL STEP — Reports / Deliverables regression tests (§11).

Contracts D1–D5 with fixed target dates and predefined section structures;
previews consume canonical data; missing data stays explicit; M1–M6 in D4 come
from the governed milestone dataset; D5 requires a governed customer and uses
its required capabilities; generation records version metadata and never
mutates Product Truth; Pilot Set uses selected governed customers only
(DEPP/INVALSI/NSA/NCCER are never invented).
"""

import httpx
import pytest

BASE_API = "http://127.0.0.1:8099"
H = {"X-User-Ref": "reports-uat"}


@pytest.fixture()
def seeded_db():
    """Governed seed (same data setup as the page fixture) — reports consume
    canonical capabilities; without this the throwaway DB is empty."""
    import psycopg
    from tests.ui.conftest import SEED, TRUNCATE
    url = "postgresql://tao:tao_dev_password@localhost:54323/tao_authoring_e2e"
    with psycopg.connect(url, autocommit=True) as conn:
        conn.execute("TRUNCATE " + ", ".join(TRUNCATE) + " RESTART IDENTITY CASCADE")
        conn.execute(SEED)
        for script in ("scripts/import/import_milestones.py",
                       "scripts/import/materialize_source_documents.py"):
            import subprocess, os, sys
            subprocess.run([sys.executable, script], cwd=conn.info.host and os.getcwd(),
                           env={**os.environ, "DATABASE_URL":
                                url.replace("postgresql://", "postgresql+psycopg://")},
                           check=True, capture_output=True)
    yield

TARGET_DATES = {
    "D1": "30 October 2026", "D2": "30 October 2026", "D3": "13 November 2026",
    "D4": "13 November 2026", "D5": "20 November 2026",
}

SECTION_TOTALS = {"D1": 11, "D2": 10, "D3": 11, "D4": 15, "D5": 19}


# ---------- contracts, dates, section structures ----------

def test_contracts_visible_with_target_dates_and_sections(seeded_db):
    rows = httpx.get(f"{BASE_API}/api/reports").json()["items"]
    by_id = {r["report_id"]: r for r in rows}
    for rid, total in SECTION_TOTALS.items():
        assert rid in by_id
        assert by_id[rid]["target_delivery"] == TARGET_DATES[rid]
        assert by_id[rid]["sections_total"] == total


def test_d4_sections_include_canonical_m1_m6(seeded_db):
    html = httpx.get(f"{BASE_API}/api/reports/D4/preview").text
    ms = httpx.get(f"{BASE_API}/api/milestones").json()["items"]
    assert [m["milestone_id"] for m in ms] == ["M1", "M2", "M3", "M4", "M5", "M6"]
    # M1–M6 content comes from the canonical milestone dataset (not duplicated truth)
    for m in ms:
        assert m["name"] in html
    assert "TS1 · Foundation" not in html   # TS state model absent (the rejection notice itself is intentional)


def test_previews_consume_canonical_data_and_print_friendly(seeded_db):
    html = httpx.get(f"{BASE_API}/api/reports/D2/preview").text
    assert "CAP-9001" in html, html[-600:] and "Alpha item authoring" in html  # governed seed
    assert "@media print" in html and "Print / Save as PDF" in html
    assert "Report ID" in html and "Version" in html              # version metadata block
    d1 = httpx.get(f"{BASE_API}/api/reports/D1/preview").text
    assert "SRC-JIRA-001" in d1                                   # sources consumed


def test_missing_data_stays_explicit(seeded_db):
    d2 = httpx.get(f"{BASE_API}/api/reports/D2/preview").text
    assert "Awaiting Product data" in d2          # no Features exist → explicit, never AI-filled
    assert "not yet Product-reviewed" in d2


def test_generation_records_version_metadata_and_never_mutates_truth(seeded_db):
    before_caps = httpx.get(f"{BASE_API}/api/capabilities").json()["count"]
    before_detail = httpx.get(f"{BASE_API}/api/capabilities/CAP-9001").json()
    r = httpx.post(f"{BASE_API}/api/reports/D3/generate", headers=H)
    assert r.status_code == 200
    body = r.json()
    assert body["report_id"] == "D3" and body["sections_total"] == 11
    v = body["version"]
    hist = httpx.get(f"{BASE_API}/api/reports/D3/generations").json()["items"]
    assert hist[0]["version"] == v and hist[0]["actor"] == "reports-uat"
    assert hist[0]["params"] == {}
    assert hist[0]["source_snapshot"]["capabilities"] == before_caps
    # Product Truth untouched
    after_caps = httpx.get(f"{BASE_API}/api/capabilities").json()["count"]
    after_detail = httpx.get(f"{BASE_API}/api/capabilities/CAP-9001").json()
    assert after_caps == before_caps
    assert after_detail["version"] == before_detail["version"]
    assert after_detail["working_name"] == before_detail["working_name"]


# ---------- D5 per-customer ----------

def test_d5_requires_governed_customer(seeded_db):
    r = httpx.get(f"{BASE_API}/api/reports/D5/preview")
    assert r.status_code == 400
    assert r.json()["detail"]["error"] == "customer_required"
    r = httpx.get(f"{BASE_API}/api/reports/D5/preview", params={"customer_id": "CUST-NOPE"})
    assert r.status_code == 404
    assert r.json()["detail"]["error"] == "customer_not_found"


def test_d5_uses_customer_required_capabilities_and_reflects_roadmap_change(seeded_db):
    H2 = {"X-User-Ref": "reports-d5"}
    cid = "CUST-RPT-1"
    httpx.delete(f"{BASE_API}/api/customers/{cid}", headers=H2)
    import psycopg
    with psycopg.connect("postgresql://tao:tao_dev_password@localhost:54323/tao_authoring_e2e", autocommit=True) as c, c.cursor() as cur:
        cur.execute("DELETE FROM customer_capabilities WHERE customer_id=%s", (cid,))
        cur.execute("DELETE FROM customers WHERE customer_id=%s", (cid,))
    assert httpx.post(f"{BASE_API}/api/customers", headers=H2, json={
        "customer_id": cid, "name": "Report D5 customer",
        "earliest_milestone_interval": "M3 -> M4",
        "validation_status": "Hypothesis"}).status_code == 201
    # required capability with early timing (ends month 3 ≤ M3 start 11 → available)
    r_link = httpx.post(f"{BASE_API}/api/customers/{cid}/capabilities", headers=H2,
                        json={"cap_id": "CAP-9001"})
    assert r_link.status_code == 201, r_link.text
    html = httpx.get(f"{BASE_API}/api/reports/D5/preview", params={"customer_id": cid}).text
    open("/tmp/d5dump.html", "w").write(html)
    detail = httpx.get(f"{BASE_API}/api/customers/{cid}").json()
    open("/tmp/d5detail.json", "w").write(str(detail))
    assert "CAP-9001" in html, html[-600:] and "Alpha item authoring" in html
    assert "Report D5 customer" in html
    # Roadmap timing change is reflected in a regenerated D5 (§10: consumed truth)
    httpx.patch(f"{BASE_API}/api/roadmap/CAP-9001", headers=H2,
                json={"version": 1, "start_month": 20, "duration_months": 5})
    html = httpx.get(f"{BASE_API}/api/reports/D5/preview", params={"customer_id": cid}).text
    assert "blocked" in html.lower(), html[-1500:]
    assert "after the proposed interval start" in html, html[-1500:]
    # restore the fixture state for other suites (per-test truncate handles it too)
    httpx.patch(f"{BASE_API}/api/roadmap/CAP-9001", headers=H2,
                json={"version": 2, "start_month": 0, "duration_months": 3})


# ---------- Pilot Set ----------

def test_pilot_set_never_invents_intended_customers():
    r = httpx.post(f"{BASE_API}/api/reports/PILOT/generate", headers=H,
                   json={"customer_ids": ["DEPP", "INVALSI", "NSA", "NCCER"]})
    assert r.status_code == 422
    body = r.json()["detail"]
    assert body["error"] == "unknown_customers"
    assert set(body["customers"]) == {"DEPP", "INVALSI", "NSA", "NCCER"}


def test_pilot_set_uses_selected_governed_customers_only(seeded_db):
    H2 = {"X-User-Ref": "pilot-uat"}
    cid = "CUST-PILOT-1"
    import psycopg
    with psycopg.connect("postgresql://tao:tao_dev_password@localhost:54323/tao_authoring_e2e", autocommit=True) as c, c.cursor() as cur:
        cur.execute("DELETE FROM customer_capabilities WHERE customer_id=%s", (cid,))
        cur.execute("DELETE FROM customers WHERE customer_id=%s", (cid,))
    assert httpx.post(f"{BASE_API}/api/customers", headers=H2, json={
        "customer_id": cid, "name": "Pilot governed customer",
        "earliest_milestone_interval": "M2 -> M3"}).status_code == 201
    r = httpx.post(f"{BASE_API}/api/reports/PILOT/generate", headers=H,
                   json={"customer_ids": [cid], "pilot": True})
    assert r.status_code == 200
    body = r.json()
    assert body["report_type"] == "pilot-set" and body["version"] >= 1
    assert [d["customer_id"] for d in body["documents"]] == [cid]
    assert "Pilot governed customer" in body["documents"][0]["html"]
    # snapshot metadata recorded
    hist = httpx.get(f"{BASE_API}/api/reports/PILOT/generations").json()["items"]
    assert hist and hist[0]["source_snapshot"]["capabilities"] == 4
    # no invented pilot names appear
    assert "DEPP" not in body["documents"][0]["html"]
    # cleanup (test fixture only)
    httpx.delete(f"{BASE_API}/api/customers/{cid}", headers=H2) if False else None
    with psycopg.connect("postgresql://tao:tao_dev_password@localhost:54323/tao_authoring_e2e", autocommit=True) as c, c.cursor() as cur:
        cur.execute("DELETE FROM customer_capabilities WHERE customer_id=%s", (cid,))
        cur.execute("DELETE FROM customers WHERE customer_id=%s", (cid,))
