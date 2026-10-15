"""Phase 6 tests — governed export (contract §7) + source-document storage.

The export must contain every Product Truth entity group without scraping
the UI. The source-document store keeps ONLY document artifacts in external
storage — PostgreSQL keeps source metadata and lineage.
"""

import httpx


def test_export_contains_all_product_truth(client):
    r = client.get("/api/export")
    assert r.status_code == 200
    data = r.json()
    assert data["export"] == "tao-authoring-product-truth"
    assert data["app_version"]

    entities = data["entities"]
    # §7 minimum: capabilities (MoSCoW/Admission/budgets are capability fields)
    for table in [
        "capabilities", "capability_markets", "markets", "sources",
        "source_capabilities", "capability_sources", "jira_tickets",
        "capability_jira", "roadmap_timing", "roadmap_outcomes",
        "milestones", "customers", "customer_capabilities",
    ]:
        assert table in entities, f"missing {table} in export"
    caps = entities["capabilities"]
    assert caps, "seeded capabilities must be present"
    for cap in caps:
        assert "moscow" in cap and "roadmap_admission" in cap
        assert "analysis_budget_hours" in cap and "execution_budget_hours" in cap
    # NULL semantics survive the round-trip (§11: NULL ≠ 0 / UNSET)
    null_budget = [c for c in caps if c["analysis_budget_hours"] is None]
    assert null_budget, "seed data includes NULL budgets"
    assert "roadmap_admission" in caps[0]


def test_export_counts_match_api_surface(client):
    data = client.get("/api/export").json()
    caps_api = client.get("/api/capabilities").json()
    markets_api = client.get("/api/markets").json()
    assert data["counts"]["capabilities"] == caps_api["count"]
    assert data["counts"]["markets"] == len(markets_api["items"])
    timing = [i for i in data["entities"]["roadmap_timing"]
              if i["cap_id"] == "CAP-9001"][0]
    assert timing["start_month"] == 0 and timing["duration_months"] == 3


def test_source_doc_store_keeps_artifacts_out_of_product_truth(tmp_path):
    """Local artifact store round-trip; metadata/lineage stay in PostgreSQL."""
    from app.docstore import LocalDocStore

    store = LocalDocStore(tmp_path)
    ref = store.put("SRC-TEST-001", "handoff.pdf", b"%PDF-1.4 fake")
    assert ref.startswith("local://")
    assert store.get(ref) == b"%PDF-1.4 fake"
    assert store.list("SRC-TEST-001") == ["handoff.pdf"]
    # artifacts are plain files under the store root — never inside the DB
    assert (tmp_path / "SRC-TEST-001" / "handoff.pdf").read_bytes() == b"%PDF-1.4 fake"


def test_source_doc_store_unknown_ref_404(tmp_path):
    from app.docstore import LocalDocStore, DocNotFound

    store = LocalDocStore(tmp_path)
    try:
        store.get("local://nope/none.pdf")
        raise AssertionError("expected DocNotFound")
    except DocNotFound:
        pass
