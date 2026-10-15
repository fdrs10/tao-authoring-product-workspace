"""Phase 4 UI E2E — shell/smoke (§55), Ideation nav, Sources workflow,
universal CAP modal incl edit/Jira/budget/conflict, Backlog + Cross-analysis
Admission, market legend, filtering. (§21 matrix)

Headless Chromium against a real migrated DB + live uvicorn. Any page JS
error fails the test (conftest)."""

import httpx
from playwright.sync_api import Page, expect

BASE_API = "http://127.0.0.1:8099"


# ---------- shell / smoke (§20/§55) ----------

def test_shell_smoke_renders(page: Page):
    page.goto("/#/ideation/01")
    for label in ["IDEATION", "ROADMAP", "MIGRATION PATH", "SOURCES & EVIDENCE"]:
        expect(page.locator("#main-nav")).to_contain_text(label)
    expect(page.locator("#app-main")).to_contain_text("V2 Position")


def test_ideation_index_six_entries(page: Page):
    page.goto("/#/ideation/01")
    idx = page.locator(".ideation-index .idx-item")
    expect(idx).to_have_count(6)
    expect(idx.nth(0)).to_contain_text("V2 Position")
    expect(idx.nth(1)).to_contain_text("V1 Carry-forward")
    expect(idx.nth(2)).to_contain_text("3.x Direct Migration")
    expect(idx.nth(3)).to_contain_text("New Needs & Gaps")
    expect(idx.nth(4)).to_contain_text("Discontinued")
    expect(idx.nth(5)).to_contain_text("Cross-analysis")


def test_v2_position_geometry_and_open_points(page: Page):
    page.goto("/#/ideation/01")
    expect(page.locator('[data-testid="v2-formula"]')).to_contain_text("TAO Studio V2 Authoring Target Scope")
    expect(page.locator('[data-testid="v2-formula"]')).to_contain_text("Cross-analysis (not a summand)")
    expect(page.get_by_role("img", name="Approved V2 Position diagram")).to_be_visible()
    for n in ["02", "03", "04", "05"]:
        expect(page.locator(f'[data-testid="v2-open-{n}"]')).to_be_visible()


def test_ideation_sheet_rows_and_discontinued_out(page: Page):
    page.goto("/#/ideation/02")
    expect(page.get_by_text("Alpha item authoring")).to_be_visible()
    page.goto("/#/ideation/05")
    expect(page.locator("text=OUT").first).to_be_visible()
    # no invented content: CAP-9004 listed under 03 sheet
    page.goto("/#/ideation/03")
    expect(page.get_by_text("Delta null budgets")).to_be_visible()


# ---------- sources (§5/§21) ----------

def test_sources_list_human_names(page: Page):
    page.goto("/#/sources")
    expect(page.locator("#app-main h1")).to_contain_text("Sources & Evidence")
    row = page.locator('[data-testid="source-row"]', has_text="SRC-TEST-001")
    expect(row).to_contain_text("Test Source Doc")      # human name, not opaque ID
    expect(row).to_contain_text("Owner S")
    expect(row).to_contain_text("1")                    # extracted count


def test_source_drilldown_extracted_to_canonical(page: Page):
    page.goto("/#/sources")
    page.locator('[data-testid="view-extracted"][data-src="SRC-TEST-001"]').click()
    pane = page.locator('[data-testid="pane-overlay"]')
    expect(pane).to_contain_text("SC-TEST-0001")
    expect(pane).to_contain_text("Original alpha")
    expect(pane).to_contain_text("EVOLVES")
    pane.locator('[data-testid="srccap-row"] .cap-link').click()
    modal = page.locator('[data-testid="cap-modal"]')
    expect(modal).to_contain_text("CAP-9001 · Alpha item authoring")


def test_open_source_detail(page: Page):
    page.goto("/#/sources")
    page.locator('[data-testid="open-source"][data-src="SRC-TEST-001"]').click()
    pane = page.locator('[data-testid="pane-overlay"]')
    expect(pane).to_contain_text("SRC-TEST-001 · Test Source Doc")
    expect(pane).to_contain_text("data/raw/test.pdf")


def test_src_jira_001_behaves_as_source(page: Page):
    """Defect 2: Jira backlog source shows all tickets + linked CAP drill."""
    page.goto("/#/sources")
    page.locator('[data-testid="open-source"][data-src="SRC-JIRA-001"]').click()
    pane = page.locator('[data-testid="pane-overlay"]')
    expect(pane).to_contain_text("Current Authoring Jira Backlog")
    expect(pane).to_contain_text("delivery evidence")
    expect(pane.locator('[data-testid="src-jira-row"]')).to_contain_text("PCR-TEST-1")
    pane.locator('[data-testid="src-jira-expand"][data-key="PCR-TEST-1"]').click()
    expect(pane).to_contain_text("CAP-9002")


def test_customers_tab_empty_by_design(page: Page):
    page.goto("/#/sources")
    page.locator('[data-testid="tab-customers"]').click()
    expect(page.locator('[data-testid="sources-body"]')).to_contain_text("governed customer dataset")


# ---------- universal CAP modal (§7/§8/§9/§10/§11/§15) ----------

def test_universal_modal_from_cross_analysis(page: Page):
    page.goto("/#/ideation/06")
    page.locator('[data-testid="xanalysis-row"] .cap-link').first.click()
    modal = page.locator('[data-testid="cap-modal"]')
    expect(modal).to_contain_text("Full functional description")
    expect(modal).to_contain_text("Roadmap Admission")
    expect(modal).to_contain_text("Jira — delivery evidence")
    expect(modal).to_contain_text("Total")


def test_cap_edit_save(page: Page):
    page.goto("/#/ideation/06")
    page.locator('[data-testid="xanalysis-row"] .cap-link').first.click()
    page.locator('[data-testid="cap-edit-btn"]').click()
    page.locator('[name="working_name"]').fill("Alpha item authoring RENAMED")
    page.locator('[data-testid="cap-save-btn"]').click()
    expect(page.locator('[data-testid="cap-modal"] h1')).to_contain_text("RENAMED")


def test_null_budget_display_never_zero(page: Page):
    page.goto("/#/ideation/06")
    page.locator('[data-testid="xanalysis-row"]', has_text="CAP-9004").locator('.cap-link').click()
    budgets = page.locator('[data-testid="cap-budgets"]')
    expect(budgets).to_contain_text("— / —")
    expect(budgets).to_contain_text("not estimated")
    expect(budgets).not_to_contain_text("0 / 0")


def test_zero_budget_display(page: Page):
    page.goto("/#/ideation/06")
    page.locator('[data-testid="xanalysis-row"]', has_text="CAP-9003").locator('.cap-link').click()
    budgets = page.locator('[data-testid="cap-budgets"]')
    expect(budgets).to_contain_text("0 / 0 / 0")


def test_add_and_remove_jira_link(page: Page):
    """Defect 1: Add Jira Link must actually work; removal must not delete ticket."""
    page.goto("/#/ideation/06")
    # add on CAP-9001 (starts with no links)
    page.locator('[data-testid="xanalysis-row"] .cap-link').first.click()
    page.locator('[data-testid="cap-edit-btn"]').click()
    page.locator('[data-testid="jira-add-input"]').fill("PCR-TEST-1")
    page.locator('[data-testid="jira-add-btn"]').click()
    expect(page.locator('[data-testid="jira-edit-rows"]')).to_contain_text("PCR-TEST-1")
    page.get_by_text("Cancel").first.click()
    expect(page.locator('[data-testid="jira-list"]')).to_contain_text("PCR-TEST-1")
    page.get_by_text("Close").first.click()
    # remove on CAP-9002 (seeded with the link)
    page.locator('[data-testid="xanalysis-row"]', has_text="CAP-9002").locator('.cap-link').click()
    expect(page.locator('[data-testid="jira-list"]')).to_contain_text("PCR-TEST-1")
    page.locator('[data-testid="cap-edit-btn"]').click()
    page.locator('[data-testid="jira-remove"][data-key="PCR-TEST-1"]').click()
    page.get_by_text("Cancel").first.click()
    expect(page.locator('[data-testid="jira-list"]')).to_contain_text("No Jira links")
    page.get_by_text("Close").first.click()
    page.locator('[data-testid="xanalysis-row"]', has_text="CAP-9002").locator('.cap-link').click()
    # ticket record itself still exists — delivery evidence preserved
    assert httpx.get(f"{BASE_API}/api/jira/PCR-TEST-1").status_code == 200


def test_scope_review_mark_shown_not_resolved(page: Page):
    page.goto("/#/ideation/06")
    page.locator('[data-testid="xanalysis-row"]', has_text="CAP-9002").locator('.cap-link').click()
    expect(page.locator('[data-testid="cap-modal"]')).to_contain_text("SCOPE REVIEW")


# ---------- admission: same canonical field, three views (§11) ----------

def test_admission_edit_from_cross_analysis(page: Page):
    page.goto("/#/ideation/06")
    row = page.locator('[data-testid="xanalysis-row"]', has_text="CAP-9001")
    row.locator('[data-testid="adm-edit"]').select_option("CANDIDATE")
    expect(row.locator('[data-testid="adm-badge"]')).to_contain_text("CANDIDATE")
    # fresh read from the API-backed detail proves persistence
    page.goto("/#/ideation/06")
    row = page.locator('[data-testid="xanalysis-row"]', has_text="CAP-9001")
    expect(row.locator('[data-testid="adm-edit"]')).to_have_value("CANDIDATE")


def test_admission_edit_from_backlog_same_field(page: Page):
    page.goto("/#/backlog")
    page.locator('[data-testid="filter-moscow"]').select_option("")
    row = page.locator('[data-testid="backlog-row"]', has_text="CAP-9002")
    row.locator('[data-testid="adm-edit"]').select_option("COMMITTED")
    expect(row.locator('[data-testid="adm-badge"]')).to_contain_text("COMMITTED")
    # the same canonical field as the CAP editor: open modal, verify COMMITTED
    row.locator('.cap-link[data-cap]').click()
    expect(page.locator('[data-testid="cap-modal"]')).to_contain_text("COMMITTED")


def test_backlog_default_must_and_filters(page: Page):
    page.goto("/#/backlog")
    rows = page.locator('[data-testid="backlog-row"]')
    expect(rows).to_have_count(2)   # Only Must (CAP-9001, CAP-9003) by default
    expect(page.locator('[data-testid="backlog-count"]')).to_contain_text("full universe")
    page.locator('[data-testid="filter-moscow"]').select_option("")
    expect(page.locator('[data-testid="backlog-row"]')).to_have_count(4)
    expect(page.locator('[data-testid="backlog-count"]')).to_contain_text("4 capabilities")
    page.locator('[data-testid="filter-category"]').select_option("Create & Design")
    expect(page.locator('[data-testid="backlog-row"]')).to_have_count(2)
    page.locator('[data-testid="filter-admission"]').select_option("CANDIDATE")
    expect(page.locator('[data-testid="backlog-row"]')).to_have_count(0)


# ---------- conflict behaviour (§9 concurrency) ----------

def test_409_conflict_state_and_recover(page: Page):
    page.goto("/#/ideation/06")
    page.locator('[data-testid="xanalysis-row"]', has_text="CAP-9001").locator('.cap-link').click()
    page.locator('[data-testid="cap-edit-btn"]').click()
    # someone else saves while we hold the form open (version drifts to 2)
    httpx.patch(f"{BASE_API}/api/capabilities/CAP-9001",
                json={"version": 1, "notes": "server-side change"})
    page.locator('[name="working_name"]').fill("stale write")
    page.locator('[data-testid="cap-save-btn"]').click()
    expect(page.locator('[data-testid="cap-modal"]')).to_contain_text("edit conflict")
    expect(page.locator('[data-testid="cap-modal"]')).to_contain_text("version 2")
    page.locator('[data-testid="conflict-reload"]').click()
    expect(page.locator('[data-testid="cap-modal"]')).to_contain_text("v2")


# ---------- market legend (§12/§26) ----------

def test_market_legend_with_colours(page: Page):
    page.goto("/#/backlog")
    legend = page.locator(".market-legend")
    expect(legend).to_be_visible()
    for m in ["Traditional / K-12", "Professional / Credentialing", "Higher Education",
              "Governed Formative", "Assessment-led Learning", "MEXCBT / Uchida"]:
        expect(legend).to_contain_text(m)
    assert legend.locator(".dot").count() == 6
