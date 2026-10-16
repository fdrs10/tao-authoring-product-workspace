"""Phase 5 UI E2E — Roadmap + Migration (§19 test matrix).

Roadmap: default Full view + hierarchy, independent expand/collapse, horizons
(0–6m/7–24m/Tail), Outcome, CAP modal reuse, drag/left/right resize with month
snapping + persisted timing, 409 timing conflict never overwrites, filters do
not reset state, Jira evidence display-only, milestone rendering + drag,
quarter report view.
Migration: shared milestone dataset, derived availability from Roadmap timing,
customer milestone intervals (never TS codes), honest empty states, milestone
edit reflected in both views.

The §55 blank-screen guard applies to every test via conftest teardown.
Reference-fixture milestones/customers below are recovered test fixtures
(v35.6) — never production data (§10/§14).
"""

import httpx
from playwright.sync_api import Page, expect

BASE_API = "http://127.0.0.1:8099"   # uvicorn managed by tests/ui/conftest.py

H = {"X-User-Ref": "phase5-test"}
MONTH_PX = None  # computed per test from track width


def _commit(cap: str, start: int, dur: int, admission: str = "COMMITTED"):
    """Promote a seeded cap to COMMITTED with timing via the public API
    (version-aware: reuses the current timing version when a row exists)."""
    v = httpx.get(f"{BASE_API}/api/capabilities/{cap}").json()["version"]
    r = httpx.patch(f"{BASE_API}/api/capabilities/{cap}",
                    headers=H, json={"version": v, "roadmap_admission": admission})
    assert r.status_code == 200, r.text
    view = httpx.get(f"{BASE_API}/api/roadmap", params={"admission": ""}).json()
    row = [i for i in view["items"] if i["cap_id"] == cap][0]
    tver = row["timing_version"] or 1
    r = httpx.patch(f"{BASE_API}/api/roadmap/{cap}",
                    headers=H, json={"version": tver, "start_month": start,
                                     "duration_months": dur})
    assert r.status_code in (200, 201), r.text


def _milestone(mid: str, name: str, pos: int, scope_type: str = "global",
               scope_ref: str | None = None):
    """Create a fixture milestone; tolerate the governed baseline (M1–M6 now
    ship with the product — UAT STRUCTURAL UPDATE §22)."""
    r = httpx.post(f"{BASE_API}/api/milestones", headers=H, json={
        "milestone_id": mid, "name": name, "position_month": pos,
        "scope_type": scope_type, "scope_ref": scope_ref})
    assert r.status_code in (201, 409), r.text


def _roadmap_timing(cap: str) -> dict:
    items = httpx.get(f"{BASE_API}/api/roadmap", params={"admission": ""}).json()["items"]
    return [i for i in items if i["cap_id"] == cap][0]


def _track_of(page: Page, bar):
    return bar.locator("xpath=..")


def _drag(page: Page, locator, dx: float):
    box = locator.bounding_box()
    cx, cy = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
    page.mouse.move(cx, cy)
    page.mouse.down()
    page.mouse.move(cx + dx, cy, steps=8)
    page.mouse.up()


# ---------- Roadmap: default view, hierarchy, width ----------

def test_roadmap_empty_state_default_committed_population(page: Page):
    # seeded caps are CANDIDATE/NULL admission → default COMMITTED view is empty
    page.goto("/#/roadmap")
    expect(page.locator('[data-testid="roadmap-empty"]')).to_be_visible()
    expect(page.locator('[data-testid="roadmap-empty"]')).to_contain_text("COMMITTED")


def test_roadmap_full_view_hierarchy_and_width(page: Page):
    _commit("CAP-9001", 0, 3)      # Create & Design · Shared / common core
    _commit("CAP-9004", 2, 4)      # Manage & Govern · market band (FOR)
    page.goto("/#/roadmap")
    expect(page.locator('[data-testid="cat-group"]')).to_have_count(2)
    expect(page.locator('[data-testid="band-row"]')).to_have_count(2)
    bars = page.locator('[data-testid="cap-bar"]')
    expect(bars).to_have_count(2)
    expect(page.locator('[data-testid="quarter-head"]')).to_have_count(9)
    # desktop width: no horizontal page scroll required (§3)
    overflow = page.evaluate(
        "() => document.documentElement.scrollWidth - window.innerWidth")
    assert overflow <= 2, f"horizontal overflow {overflow}px"


def test_roadmap_bands_independent_expand_collapse(page: Page):
    _commit("CAP-9001", 0, 3)
    _commit("CAP-9004", 2, 4)
    page.goto("/#/roadmap")
    toggles = page.locator('[data-testid="band-toggle"]')
    toggles.nth(0).click()
    expect(page.locator('[data-testid="band-drilldown"]')).to_have_count(1)
    toggles.nth(1).click()                      # second branch opens independently
    expect(page.locator('[data-testid="band-drilldown"]')).to_have_count(2)
    page.locator('[data-testid="band-toggle"]').nth(0).click()
    expect(page.locator('[data-testid="band-drilldown"]')).to_have_count(1)  # other stays open


# ---------- Roadmap: horizons (§5) ----------

def test_roadmap_horizon_views_over_same_data(page: Page):
    _commit("CAP-9001", 0, 3)
    page.goto("/#/roadmap")
    page.locator('[data-testid="hz-0-6"]').click()
    expect(page.locator('[data-testid="horizon-report"]')).to_be_visible()
    expect(page.locator('[data-testid="hz-bar"]')).to_have_count(1)
    page.locator('[data-testid="hz-7-24"]').click()
    expect(page.locator('[data-testid="hz-bar"]')).to_have_count(0)   # timing 0–3 not in 7–24
    page.locator('[data-testid="hz-tail"]').click()
    expect(page.locator('[data-testid="hz-bar"]')).to_have_count(0)
    page.locator('[data-testid="hz-full"]').click()
    expect(page.locator('[data-testid="cap-bar"]')).to_have_count(1)  # same data, full view


# ---------- Roadmap: Outcome (§6) ----------

def test_outcome_persist_and_409_recover(page: Page):
    page.goto("/#/roadmap")
    page.locator('[data-testid="view-outcome"]').click()
    ta = page.locator('[data-testid="outcome-text-0-6m"]')
    ta.fill("0–6 months: high-confidence plan narrative.")
    page.locator('[data-testid="outcome-save-0-6m"]').click()
    expect(page.locator('[data-testid="roadmap-status"]')).to_contain_text("saved")
    # reload → server state
    page.reload()
    page.locator('[data-testid="view-outcome"]').click()
    expect(page.locator('[data-testid="outcome-text-0-6m"]')).to_have_value(
        "0–6 months: high-confidence plan narrative.")
    # someone else saves while our form holds the old version → 409 → replace + warn
    r = httpx.get(f"{BASE_API}/api/outcomes").json()
    ver = [i for i in r["items"] if i["horizon"] == "0-6m"][0]["version"]
    httpx.patch(f"{BASE_API}/api/outcomes/0-6m", headers=H,
                json={"version": ver, "narrative": "server-side narrative"})
    page.locator('[data-testid="outcome-text-0-6m"]').fill("stale client text")
    page.locator('[data-testid="outcome-save-0-6m"]').click()
    expect(page.locator('[data-testid="roadmap-status"]')).to_contain_text("conflict")
    expect(page.locator('[data-testid="outcome-text-0-6m"]')).to_have_value(
        "server-side narrative")


# ---------- Roadmap: interactions (§7/§8) ----------

def test_cap_modal_reused_from_roadmap_bar(page: Page):
    _commit("CAP-9001", 0, 3)
    page.goto("/#/roadmap")
    page.locator('[data-testid="cap-bar"][data-cap="CAP-9001"]').click()
    expect(page.locator('[data-testid="cap-modal"]')).to_contain_text("CAP-9001")


def test_drag_moves_and_persists_with_month_snap(page: Page):
    _commit("CAP-9001", 0, 3)
    page.goto("/#/roadmap")
    bar = page.locator('[data-testid="cap-bar"][data-cap="CAP-9001"]')
    track = _track_of(page, bar)
    month = track.bounding_box()["width"] / 27
    _drag(page, bar, month * 2.4)        # 2.4 months → snaps to 2 (Math.round)
    expect(page.locator('[data-testid="roadmap-status"]')).to_contain_text("Saved CAP-9001")
    row = _roadmap_timing("CAP-9001")
    assert row["start_month"] == 2 and row["duration_months"] == 3
    assert row["timing_version"] == 3   # seeded v1 → _commit PATCH → v2 → drag → v3


def test_left_and_right_resize_snap_and_persist(page: Page):
    _commit("CAP-9001", 3, 4)
    page.goto("/#/roadmap")
    bar = page.locator('[data-testid="cap-bar"][data-cap="CAP-9001"]')
    track = _track_of(page, bar)
    month = track.bounding_box()["width"] / 27
    # right handle: +2 months duration (4 → 6)
    handle_r = bar.locator('[data-testid="bar-handle-right"]')
    _drag(page, handle_r, month * 2)
    row = _roadmap_timing("CAP-9001")
    assert (row["start_month"], row["duration_months"]) == (3, 6)
    # left handle dragged one month LEFT grows the bar: (3,6) → (2,7) — v10 math
    # (new duration = old start + old duration − new start = 3+6−2 = 7)
    handle_l = bar.locator('[data-testid="bar-handle-left"]')
    _drag(page, handle_l, -month * 1)
    row = _roadmap_timing("CAP-9001")
    assert (row["start_month"], row["duration_months"]) == (2, 7)


def test_timing_409_never_overwrites(page: Page):
    _commit("CAP-9001", 0, 3)
    page.goto("/#/roadmap")
    # another user saves while our page holds the form → version drifts
    cur = _roadmap_timing("CAP-9001")["timing_version"]
    httpx.patch(f"{BASE_API}/api/roadmap/CAP-9001", headers=H,
                json={"version": cur, "start_month": 6, "duration_months": 3})
    bar = page.locator('[data-testid="cap-bar"][data-cap="CAP-9001"]')
    track = _track_of(page, bar)
    _drag(page, bar, track.bounding_box()["width"] / 27 * 2)
    expect(page.locator('[data-testid="roadmap-status"]')).to_contain_text("conflict")
    row = _roadmap_timing("CAP-9001")
    assert (row["start_month"], row["duration_months"]) == (6, 3)   # server truth intact


def test_filters_do_not_reset_state(page: Page):
    _commit("CAP-9001", 0, 3)
    _commit("CAP-9004", 2, 4)
    page.goto("/#/roadmap")
    page.locator('[data-testid="band-toggle"]').first.click()
    expect(page.locator('[data-testid="band-drilldown"]')).to_have_count(1)
    # filter change must not reset expansion/timing/outcome (§16)
    page.locator('[data-testid="rfilter-moscow"]').select_option("Must")
    expect(page.locator('[data-testid="band-drilldown"]')).to_have_count(1)
    row = _roadmap_timing("CAP-9001")
    assert row["start_month"] == 0 and row["duration_months"] == 3
    page.locator('[data-testid="rfilter-moscow"]').select_option("")
    expect(page.locator('[data-testid="band-drilldown"]')).to_have_count(1)


def test_jira_target_release_display_only(page: Page):
    _commit("CAP-9002", 1, 2)   # CAP-9002 carries jira PCR-TEST-1 (seeded link)
    page.goto("/#/roadmap")
    bar = page.locator('[data-testid="cap-bar"][data-cap="CAP-9002"]')
    expect(bar).to_have_count(1)   # D-R1 confirmed: each CAP renders exactly once (market = filter, not lane)
    title = bar.first.get_attribute("title")
    assert "PCR-TEST-1" in title                    # evidence visible (§9)
    row = _roadmap_timing("CAP-9002")
    assert (row["start_month"], row["duration_months"]) == (1, 2)   # Product timing untouched


# ---------- Roadmap: milestones (§10) ----------

def test_milestone_lines_render_and_drag_persists(page: Page):
    _commit("CAP-9001", 0, 3)
    _milestone("MT1", "Fixture milestone one", 4)
    page.goto("/#/roadmap")
    page.locator('[data-testid="rfilter-admission"]').select_option("All")  # D-R3 default is COMMITTED
    line = page.locator('[data-testid="milestone-line"][data-ms="MT1"]')
    # D-R1: a global milestone renders on every category lane (labelled once
    # per category) — assert presence, drag the first instance.
    expect(line.first).to_be_visible(timeout=10000)
    # baseline M1–M6 exist; the fixture label appears on its own line(s)
    expect(page.locator('[data-testid="milestone-label"]', has_text="Fixture milestone one").first).to_be_visible()
    track = _track_of(page, line.first)
    _drag(page, line.first, track.bounding_box()["width"] / 27 * 2)   # 4 → 6
    row = [m for m in httpx.get(f"{BASE_API}/api/milestones").json()["items"]
           if m["milestone_id"] == "MT1"][0]
    assert row["position_month"] == 6


def test_quarter_view_report(page: Page):
    _commit("CAP-9001", 0, 3)
    page.goto("/#/roadmap")
    page.locator('[data-testid="quarter-head"][data-q="0"]').click()
    expect(page.locator('[data-testid="quarter-modal"]')).to_be_visible()
    expect(page.locator('[data-testid="quarter-title"]')).to_contain_text("2026 Q4")
    chip = page.locator('[data-testid="quarter-chip"][data-cap="CAP-9001"]')
    expect(chip.first).to_be_visible()
    chip.first.click()   # click-through reuses the universal CAP modal
    expect(page.locator('[data-testid="cap-modal"]')).to_contain_text("CAP-9001")


# ---------- Migration (§12–§15) ----------

def test_migration_states_are_honest(page: Page):
    """Since the UAT structural update the M1–M6 baseline ships as governed
    data (§22/§23); customers remain honestly empty (D3)."""
    page.goto("/#/migration")
    expect(page.locator('[data-testid="milestone-row"]')).to_have_count(6)
    expect(page.locator('[data-testid="customers-empty"]')).to_contain_text("D3")


def test_migration_derived_availability_and_shared_milestones(page: Page):
    _commit("CAP-9001", 0, 3)          # ends month 3 → unlocked before M1@4
    _commit("CAP-9004", 3, 4)          # 3..7 → in flight during M1→M2
    _milestone("MT1", "Fixture M1", 4)
    _milestone("MT2", "Fixture M2", 12)
    page.goto("/#/migration")
    expect(page.locator('[data-testid="milestone-row"]', has_text="Fixture")).to_have_count(2)
    iv1 = page.locator('[data-testid="interval-row"]', has_text="MT1 → M2")  # M1 → M2
    expect(iv1.locator('[data-testid="interval-unlocked"][data-cap="CAP-9001"]')).to_have_count(1)
    expect(iv1.locator('[data-testid="interval-inflight"][data-cap="CAP-9004"]')).to_have_count(1)


def test_migration_timing_change_updates_derivation(page: Page):
    _commit("CAP-9001", 0, 3)
    _milestone("MT1", "Fixture M1", 4)
    _milestone("MT2", "Fixture M2", 12)
    page.goto("/#/migration")
    iv1 = page.locator('[data-testid="interval-row"]', has_text="MT1 → M2")
    expect(iv1.locator('[data-testid="interval-unlocked"][data-cap="CAP-9001"]')).to_have_count(1)
    # Product moves the work → derivation follows (no manual duplication, §13)
    _commit("CAP-9001", 5, 4)          # now in flight during M1→M2
    page.reload()                       # same-hash goto would not re-render
    page.wait_for_timeout(600)
    iv1 = page.locator('[data-testid="interval-row"]', has_text="MT1 → M2")
    expect(iv1.locator('[data-testid="interval-unlocked"][data-cap="CAP-9001"]')).to_have_count(0)
    expect(iv1.locator('[data-testid="interval-inflight"][data-cap="CAP-9001"]')).to_have_count(1)


def test_customer_transition_interval_and_blockers(page: Page):
    r = httpx.post(f"{BASE_API}/api/customers", headers=H, json={
        "customer_id": "CUST-FIX-1", "name": "Reference fixture customer",
        "current_use": "3.x authoring",
        "desired_outcome": "Studio authoring",
        "blockers": "data migration; training",
        "earliest_milestone_interval": "M1 -> M2"})
    assert r.status_code == 201
    _milestone("MT1", "Fixture M1", 4)
    page.goto("/#/migration")
    row = page.locator('[data-testid="customer-row"][data-customer="CUST-FIX-1"]')
    expect(row.locator('[data-testid="cust-interval"]')).to_have_text("M1 -> M2")
    expect(row.locator('[data-testid="cust-blockers"]')).to_contain_text("training")


def test_milestone_edit_reflected_in_both_views(page: Page):
    _commit("CAP-9001", 0, 3)
    _milestone("MT1", "Fixture M1", 4)
    page.goto("/#/migration")
    page.locator('[data-testid="ms-edit-MT1"]').click()
    page.locator('[data-testid="ms-pos"]').select_option("8")
    page.locator('[data-testid="ms-save"]').click()
    # shared dataset: API updated
    row = [m for m in httpx.get(f"{BASE_API}/api/milestones").json()["items"]
           if m["milestone_id"] == "MT1"][0]
    assert row["position_month"] == 8
    # roadmap view shows the moved line (re-render fetches fresh milestones)
    page.goto("/#/roadmap")
    line = page.locator('[data-testid="milestone-line"][data-ms="MT1"]')
    expect(line).to_have_count(1)
    left = line.evaluate("el => parseFloat(el.style.left)")
    assert abs(left - ((8 + 0.5) / 27 * 100)) < 0.5
