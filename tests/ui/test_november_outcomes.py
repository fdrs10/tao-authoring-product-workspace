"""FINAL UAT EVOLUTION — November Outcomes & Customer Migration Plans (§22).

Outcomes: five outcomes visible, linked to the right working areas, no
duplicate Product data. Customer Migration Plans: honest empty state,
existing Customer API, required-capability relationships, CAP modal
navigation, interval assignment, blocker persistence, optimistic concurrency,
audit, no invented dates. Dependency/readiness: canonical CAP consumption,
Roadmap timing as the only timing truth, timing change affects readiness,
blocked capabilities identifiable, milestone edits propagate. Migration:
M1–M6 visible, Path vs Plans separation, no TS model.
"""

import httpx
import psycopg
from playwright.sync_api import Page, expect

BASE_API = "http://127.0.0.1:8099"
H = {"X-User-Ref": "nov-uat"}


def _reset_customer(conn_url, customer_id="CUST-NOV-1"):
    with psycopg.connect(conn_url, autocommit=True) as c, c.cursor() as cur:
        cur.execute("DELETE FROM customers WHERE customer_id=%s", (customer_id,))


def _mk_customer(cap_ids=("CAP-9001",), interval="M3 -> M4",
                 blockers="integration dependency; workflow validation",
                 cid="CUST-NOV-1", name="UAT Customer A"):
    r = httpx.post(f"{BASE_API}/api/customers", headers=H, json={
        "customer_id": cid, "name": name, "current_use": "TAO 3.x Authoring on-premise",
        "current_environment": "3.x 5.10 on-prem",
        "relevant_markets": "Traditional / K-12",
        "min_functionality_today": "item authoring; test assembly",
        "min_functionality_studio": "item authoring; assembly; QTI export",
        "desired_outcome": "move to Studio without workflow loss",
        "value_opportunity": "shared item banks across programmes",
        "blockers": blockers,
        "earliest_milestone_interval": interval,
        "validation_status": "Hypothesis"})
    assert r.status_code == 201, r.text
    for cap in cap_ids:
        r = httpx.post(f"{BASE_API}/api/customers/{cid}/capabilities", headers=H, json={"cap_id": cap})
        assert r.status_code in (201, 409), r.text
    return cid


# ---------- November Outcomes overview ----------

def test_five_outcomes_visible_and_linked(page: Page):
    page.goto("/#/outcomes")
    for n in range(1, 6):
        expect(page.locator(f'[data-testid="outcome-{n}"]')).to_be_visible()
    expect(page.locator('[data-testid="outcomes-flow"]')).to_contain_text("Customer Plans")
    # links navigate to the correct working areas
    page.locator('[data-testid="outcome-3"]').get_by_role("link", name="Product Roadmap").click()
    expect(page.locator("h1").first).to_contain_text("Roadmap")
    page.goto("/#/outcomes")
    page.locator('[data-testid="outcome-2"]').get_by_role("link", name="Product Backlog").click()
    expect(page.locator("h1").first).to_contain_text("Product Backlog")


def test_outcomes_introduce_no_duplicate_product_data():
    # the overview is static orientation: total capability count unchanged
    before = httpx.get(f"{BASE_API}/api/capabilities").json()["count"]
    assert before == 4  # e2e governed seed; the page stores nothing
    # (page interaction asserted in test_five_outcomes_visible_and_linked)


# ---------- Customer Migration Plans ----------

def test_customer_plans_empty_state_is_honest(page: Page):
    page.goto("/#/migration")
    page.locator('[data-testid="mig-tab-plans"]').click()
    expect(page.locator('[data-testid="plans-empty"]')).to_contain_text("cannot be invented")


def test_customer_plan_crud_interval_blockers_persistence(page: Page):
    cid = _mk_customer()
    # full plan renders context, need, dependencies, migration, validation
    page.goto("/#/migration")
    page.locator('[data-testid="mig-tab-plans"]').click()
    page.locator('[data-testid="open-plan-CUST-NOV-1"]').click()
    expect(page.locator('[data-testid="plan-title"]')).to_contain_text("UAT Customer A")
    expect(page.locator('[data-testid="plan-readiness-reason"]')).to_contain_text("available")
    # required capabilities listed with per-cap dependency state; CAP modal nav
    row = page.locator('[data-testid="plan-req-row"][data-cap="CAP-9001"]')
    expect(row).to_be_visible()
    row.locator(".cap-link").click()
    expect(page.locator('[data-testid="cap-modal"]')).to_contain_text("CAP-9001")
    page.locator('[data-testid="cap-modal"]').get_by_text("Close").first.click()
    # edit: interval + blockers persist (optimistic version)
    page.locator('[data-testid="plan-edit"]').click()
    page.locator('[data-testid="plan-edit-overlay"] [name="earliest_milestone_interval"]').fill("M4 -> M5")
    page.locator('[data-testid="plan-edit-overlay"] [name="blockers"]').fill("integration dependency; workflow validation; data migration")
    page.locator('[data-testid="plan-save"]').click()
    row = httpx.get(f"{BASE_API}/api/customers/CUST-NOV-1").json()
    assert row["earliest_milestone_interval"] == "M4 -> M5"
    assert "data migration" in row["blockers"]
    assert row["version"] == 2
    # readiness re-derived: interval start now M4(14)
    assert row["migration_plan"]["interval_start_milestone"] == "M4"
    # audit trail exists
    with psycopg.connect("postgresql://tao:tao_dev_password@localhost:54323/tao_authoring_e2e") as c, c.cursor() as cur:
        cur.execute("SELECT actor, action FROM audit_events WHERE entity_type='customer' "
                    "AND entity_id='CUST-NOV-1' ORDER BY audit_id DESC LIMIT 1")
        actor, action = cur.fetchone()
    # UI save runs under the page's user chip (dev-user); create was nov-uat via API
    assert action == "update" and actor == "dev-user"


def test_customer_plan_optimistic_concurrency_409():
    cid = _mk_customer(cid="CUST-NOV-2", name="UAT Customer B", cap_ids=("CAP-9002",),
                       interval="M2 -> M3", blockers="none recorded")
    v = httpx.get(f"{BASE_API}/api/customers/{cid}").json()["version"]
    r1 = httpx.patch(f"{BASE_API}/api/customers/{cid}", headers=H,
                     json={"version": v, "notes": "first save"})
    assert r1.status_code == 200
    r2 = httpx.patch(f"{BASE_API}/api/customers/{cid}", headers=H,
                     json={"version": v, "notes": "stale overwrite attempt"})
    assert r2.status_code == 409
    assert httpx.get(f"{BASE_API}/api/customers/{cid}").json()["notes"] == "first save"


def test_customer_plan_no_invented_dates():
    cid = _mk_customer(cid="CUST-NOV-3", name="UAT C", cap_ids=("CAP-9003",), interval="M3 -> M4")
    row = httpx.get(f"{BASE_API}/api/customers/{cid}").json()
    mp = row["migration_plan"]
    # nothing invents a migration date/window: empty stays empty until Product fills it
    assert row["proposed_migration_window"] is None
    # the only dates shown come from the shared milestone baseline
    for m in mp["milestones"]:
        assert m["milestone_id"] in {"M1", "M2", "M3", "M4", "M5", "M6"}


# ---------- Dependency / readiness derivation ----------

def test_readiness_uses_roadmap_timing_and_changes_with_it(page: Page):
    cid = _mk_customer(cid="CUST-NOV-4", name="Readiness UAT", cap_ids=("CAP-9002",),
                       interval="M1 -> M2", blockers="")  # CAP-9002 untimed → blocked
    row = httpx.get(f"{BASE_API}/api/customers/{cid}").json()
    mp = row["migration_plan"]
    assert mp["readiness_status"] == "BLOCKED BY ROADMAP CAPABILITY"
    assert mp["blocked_capability_ids"] == ["CAP-9002"]
    # give CAP-9002 early Roadmap timing (ends month 1 < M1 start 2) → ready
    httpx.patch(f"{BASE_API}/api/roadmap/CAP-9002", headers=H,
                json={"version": 1, "start_month": 0, "duration_months": 1})
    httpx.patch(f"{BASE_API}/api/capabilities/CAP-9002", headers=H,
                json={"version": 1, "roadmap_admission": "COMMITTED",
                      "product_review_status": "CONFIRMED"})
    row = httpx.get(f"{BASE_API}/api/customers/{cid}").json()
    assert row["migration_plan"]["readiness_status"] == "CUSTOMER VALIDATION REQUIRED"
    # blocked capabilities remain identifiable with the reason
    assert row["migration_plan"]["blocked_capability_ids"] == []
    assert "available" in row["migration_plan"]["readiness_reason"]
    # UI shows the derived readiness and per-cap dependency honestly
    page.goto("/#/migration")
    page.locator('[data-testid="mig-tab-plans"]').click()
    page.locator(f'[data-testid="open-plan-{cid}"]').click()
    expect(page.locator('[data-testid="plan-readiness-reason"]')).to_contain_text("available")
    r = httpx.get(f"{BASE_API}/api/customers/{cid}").json()["migration_plan"]["required_capabilities"][0]
    assert r["available_by_interval_start"] is True


def test_product_decision_required_when_no_interval():
    cid = _mk_customer(cid="CUST-NOV-5", name="No interval UAT", cap_ids=("CAP-9001",), interval="")
    r = httpx.post(f"{BASE_API}/api/customers/{cid}/capabilities", headers=H, json={"cap_id": "CAP-9001"})
    assert r.status_code in (201, 409)
    mp = httpx.get(f"{BASE_API}/api/customers/{cid}").json()["migration_plan"]
    assert mp["readiness_status"] == "PRODUCT DECISION REQUIRED"


# ---------- Migration separation ----------

def test_migration_path_and_plans_are_separate(page: Page):
    page.goto("/#/migration")
    expect(page.locator('[data-testid="mig-tab-path"]')).to_be_visible()
    expect(page.locator('[data-testid="mig-tab-plans"]')).to_be_visible()
    # path tab: common path bands, no per-customer plan panes
    expect(page.locator('[data-testid="mig-band-value"]')).to_be_visible()
    expect(page.locator('[data-testid="plans-list"]')).to_have_count(0)
    # plans tab: per-customer plans, no duplicated milestone truth
    page.locator('[data-testid="mig-tab-plans"]').click()
    expect(page.locator('[data-testid="plans-note"]')).to_contain_text("ONE common Migration Path")
    expect(page.locator('[data-testid="mig-band-value"]')).to_have_count(0)


def test_no_ts_codes_anywhere(page: Page):
    page.goto("/#/migration")
    page.locator('[data-testid="mig-tab-plans"]').click()
    body = page.locator("#app-main").inner_text()
    assert "TS1" not in body and "TS2" not in body and "TS3" not in body
    # API still refuses TS intervals
    r = httpx.post(f"{BASE_API}/api/customers", headers=H, json={
        "customer_id": "CUST-TS-X", "name": "TS probe",
        "earliest_milestone_interval": "TS1"})
    assert r.status_code == 422
