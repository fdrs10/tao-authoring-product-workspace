"""Phase 3 API tests: success, validation, not-found, stale-version
conflict and audit-generation across all routers."""


# ---------- health ----------

def test_health_endpoints(client):
    r = client.get("/health")
    assert r.status_code == 200 and r.json()["status"] == "ok"
    r = client.get("/health/db")
    assert r.status_code == 200 and r.json()["database"] is True


# ---------- capabilities ----------

def test_capability_list_and_filters(client):
    r = client.get("/api/capabilities")
    assert r.status_code == 200
    data = r.json()
    names = {c["cap_id"] for c in data["items"]}
    assert {"CAP-9001", "CAP-9002"} <= names

    r = client.get("/api/capabilities", params={"admission": "UNSET"})
    ids = {c["cap_id"] for c in r.json()["items"]}
    assert "CAP-9001" in ids and "CAP-9002" not in ids
    r = client.get("/api/capabilities", params={"admission": "Candidate"})
    ids = {c["cap_id"] for c in r.json()["items"]}
    assert ids == {"CAP-9002"}
    r = client.get("/api/capabilities",
                   params={"market": "Professional / Credentialing"})
    assert {c["cap_id"] for c in r.json()["items"]} == {"CAP-9002"}
    r = client.get("/api/capabilities",
                   params={"category": "Create & Design"})
    ids = {c["cap_id"] for c in r.json()["items"]}
    assert "CAP-9001" in ids and "CAP-9002" not in ids


def test_capability_detail_lineage_and_derived_total(client):
    r = client.get("/api/capabilities/CAP-9001")
    assert r.status_code == 200
    cap = r.json()
    assert cap["cap_id"] == "CAP-9001"
    assert cap["roadmap_admission"] is None          # UNSET stays NULL
    assert cap["total_budget_hours"] is None         # NULL ≠ 0 budgets
    assert cap["analysis_budget_hours"] is None
    assert cap["roadmap_timing"]["start_month"] == 0
    assert [m["name"] for m in cap["markets"]] == ["Traditional / K-12"]
    assert cap["sources"][0]["source_id"] == "SRC-TEST-001"
    assert cap["source_capabilities"][0]["source_capability_id"] == "SC-TEST-0001"
    assert cap["source_capabilities"][0]["reconciliation_relationship"] == "EVOLVES"
    assert cap["jira"] == []


def test_capability_not_found(client):
    assert client.get("/api/capabilities/CAP-9999").status_code == 404
    assert client.patch("/api/capabilities/CAP-9999",
                        json={"version": 1, "working_name": "x"}).status_code == 404
    assert client.post("/api/capabilities/CAP-9999/jira",
                       json={"jira_key": "PCR-TEST-1"}).status_code == 404


def test_patch_capability_success_totals_and_version(client):
    r = client.patch("/api/capabilities/CAP-9001", json={
        "version": 1, "working_name": "alpha renamed",
        "analysis_budget_hours": 96, "execution_budget_hours": 40})
    assert r.status_code == 200 and r.json()["updated"] is True
    assert r.json()["version"] == 2
    cap = client.get("/api/capabilities/CAP-9001").json()
    assert cap["working_name"] == "alpha renamed"
    assert cap["total_budget_hours"] == 136.0        # 96 + 40


def test_patch_null_semantics_preserved(client):
    """Editing another field must not touch NULL admission or NULL budgets."""
    r = client.patch("/api/capabilities/CAP-9001", json={
        "version": 1, "notes": "editorial note"})
    assert r.status_code == 200
    cap = client.get("/api/capabilities/CAP-9001").json()
    assert cap["roadmap_admission"] is None          # never coerced to BACKLOG
    assert cap["analysis_budget_hours"] is None      # never coerced to 0
    assert cap["total_budget_hours"] is None


def test_patch_version_conflict(client):
    ok = client.patch("/api/capabilities/CAP-9001",
                      json={"version": 1, "working_name": "first edit"})
    assert ok.status_code == 200
    stale = client.patch("/api/capabilities/CAP-9001",
                         json={"version": 1, "working_name": "stale edit"})
    assert stale.status_code == 409
    body = stale.json()["detail"]
    assert body["current_version"] == 2
    cap = client.get("/api/capabilities/CAP-9001").json()
    assert cap["working_name"] == "first edit"      # stale not applied


def test_patch_validation_errors(client):
    r = client.patch("/api/capabilities/CAP-9001", json={
        "version": 1, "roadmap_admission": "BOGUS"})
    assert r.status_code == 422
    r = client.patch("/api/capabilities/CAP-9001", json={
        "version": 1, "markets": ["No Such Market"]})
    assert r.status_code == 422 and "unknown_markets" in str(r.json()["detail"])
    r = client.patch("/api/capabilities/CAP-9001", json={
        "version": 1, "analysis_budget_hours": -1})
    assert r.status_code == 422
    r = client.patch("/api/capabilities/CAP-9001", json={"version": 1})
    assert r.status_code == 400
    r = client.patch("/api/capabilities/CAP-9001",
                     json={"version": 1, "cap_id": "CAP-0135"})
    assert r.status_code == 422                      # extra fields forbidden


def test_markets_replacement(client):
    r = client.patch("/api/capabilities/CAP-9002", json={
        "version": 1, "markets": ["Higher Education"]})
    assert r.status_code == 200 and "markets" in r.json()["changed"]
    cap = client.get("/api/capabilities/CAP-9002").json()
    assert [m["name"] for m in cap["markets"]] == ["Higher Education"]


# ---------- jira relationships ----------

def test_jira_link_lifecycle(client):
    r = client.post("/api/capabilities/CAP-9001/jira",
                    json={"jira_key": "PCR-AWAY-99"})
    assert r.status_code == 404                      # unknown ticket rejected

    r = client.post("/api/capabilities/CAP-9001/jira",
                    json={"jira_key": "PCR-TEST-1"})
    assert r.status_code == 201 and r.json()["created"] is True
    cap = client.get("/api/capabilities/CAP-9001").json()
    assert cap["jira"][0]["jira_key"] == "PCR-TEST-1"
    assert cap["jira"][0]["status"] == "In Progress"

    r = client.post("/api/capabilities/CAP-9001/jira",
                    json={"jira_key": "PCR-TEST-1", "note": "relinked"})
    assert r.json()["created"] is False              # update path

    r = client.get("/api/jira/PCR-TEST-1")
    assert any(c["cap_id"] == "CAP-9001" for c in r.json()["capabilities"])

    r = client.delete("/api/capabilities/CAP-9001/jira/PCR-TEST-1")
    assert r.status_code == 200 and r.json()["deleted"] is True
    assert client.get("/api/capabilities/CAP-9001").json()["jira"] == []
    assert client.delete("/api/capabilities/CAP-9001/jira/PCR-TEST-1"
                         ).status_code == 404
    # ticket itself survives — Jira is evidence, the link was the relation
    assert client.get("/api/jira/PCR-TEST-1").status_code == 200


def test_jira_endpoints(client):
    r = client.get("/api/jira")
    assert r.status_code == 200
    assert any(t["jira_key"] == "PCR-TEST-1" for t in r.json()["items"])
    assert client.get("/api/jira/PCR-NOPE-1").status_code == 404
    r = client.get("/api/jira", params={"status": "In Progress"})
    assert all(t["status"] == "In Progress" for t in r.json()["items"])


# ---------- sources ----------

def test_sources_endpoints(client):
    r = client.get("/api/sources")
    assert r.status_code == 200
    src = next(s for s in r.json()["items"] if s["source_id"] == "SRC-TEST-001")
    assert src["extracted_capability_count"] == 1
    assert src["title"] == "Test Source Doc"         # human name, not opaque ID

    r = client.get("/api/sources/SRC-TEST-001")
    assert r.status_code == 200 and r.json()["extracted_capability_count"] == 1
    assert client.get("/api/sources/SRC-NOPE").status_code == 404

    r = client.get("/api/sources/SRC-TEST-001/capabilities")
    assert r.status_code == 200 and r.json()["count"] == 1
    row = r.json()["items"][0]
    assert row["original_name"] == "Original alpha"  # Source Truth verbatim
    assert row["canonical_cap_id"] == "CAP-9001"     # reconciliation target
    assert row["canonical_cap_name"] == "Test capability alpha"
    assert client.get("/api/sources/SRC-NOPE/capabilities").status_code == 404


# ---------- roadmap + milestones ----------

def test_roadmap_default_committed_and_filters(client):
    r = client.get("/api/roadmap")
    assert r.status_code == 200 and r.json()["count"] == 0   # nothing COMMITTED yet
    r = client.get("/api/roadmap", params={"admission": "Candidate"})
    assert [i["cap_id"] for i in r.json()["items"]] == ["CAP-9002"]
    r = client.get("/api/roadmap", params={"admission": "UNSET"})
    assert {i["cap_id"] for i in r.json()["items"]} == {"CAP-9001"}
    r = client.get("/api/roadmap",
                   params={"admission": "", "category": "Create & Design"})
    ids = {i["cap_id"] for i in r.json()["items"]}
    assert "CAP-9001" in ids and "CAP-9002" not in ids


def test_roadmap_timing_patch_and_conflict(client):
    r = client.patch("/api/roadmap/CAP-9001",
                     json={"version": 1, "start_month": 2, "duration_months": 4})
    assert r.status_code == 200
    stale = client.patch("/api/roadmap/CAP-9001",
                         json={"version": 1, "start_month": 9, "duration_months": 4})
    assert stale.status_code == 409
    timing = client.get("/api/capabilities/CAP-9001").json()["roadmap_timing"]
    assert timing["start_month"] == 2 and timing["version"] == 2
    # upsert create-path for a cap without a timing row
    r = client.patch("/api/roadmap/CAP-9002",
                     json={"version": 1, "start_month": 3, "duration_months": 6})
    assert r.status_code == 200
    assert client.patch("/api/roadmap/CAP-9999",
                        json={"version": 1, "start_month": 0, "duration_months": 1}
                        ).status_code == 404
    r = client.patch("/api/roadmap/CAP-9001",
                     json={"version": 2, "start_month": 0, "duration_months": 0})
    assert r.status_code == 422                      # duration_months >= 1


def test_milestones_crud_and_conflicts(client):
    assert client.get("/api/milestones").json()["count"] == 0   # D2: no invention
    r = client.post("/api/milestones", json={
        "milestone_id": "M1", "name": "R1a Launch", "position_month": 6,
        "milestone_date": "2027-03-31"})
    assert r.status_code == 201
    assert client.post("/api/milestones", json={
        "milestone_id": "M1", "name": "dup"}).status_code == 409
    r = client.patch("/api/milestones/M1",
                     json={"version": 1, "name": "R1a Launch GA"})
    assert r.status_code == 200
    stale = client.patch("/api/milestones/M1",
                         json={"version": 1, "name": "stale"})
    assert stale.status_code == 409
    r = client.get("/api/milestones")
    assert r.json()["items"][0]["name"] == "R1a Launch GA"
    assert client.patch("/api/milestones/NOPE",
                        json={"version": 1, "name": "x"}).status_code == 404


# ---------- customers ----------

def test_customers_master_data_contract(client):
    assert client.get("/api/customers").json()["count"] == 0   # D3: empty by design

    r = client.post("/api/customers", json={
        "customer_id": "CUST-TEST", "name": "Test Customer",
        "earliest_milestone_interval": "M3 -> M4"})
    assert r.status_code == 201
    r = client.post("/api/customers", json={
        "customer_id": "CUST-TS", "name": "bad interval",
        "earliest_milestone_interval": "TS2"})
    assert r.status_code == 422                      # §40: no TS codes
    assert client.post("/api/customers", json={
        "customer_id": "CUST-TEST", "name": "dup"}).status_code == 409

    r = client.patch("/api/customers/CUST-TEST",
                     json={"version": 1, "validation_status": "VALIDATED"})
    assert r.status_code == 200
    stale = client.patch("/api/customers/CUST-TEST",
                         json={"version": 1, "name": "stale"})
    assert stale.status_code == 409

    r = client.post("/api/customers/CUST-TEST/capabilities",
                    json={"cap_id": "CAP-9001"})
    assert r.status_code == 201
    assert client.post("/api/customers/CUST-TEST/capabilities",
                       json={"cap_id": "CAP-9001"}).status_code == 409
    assert client.post("/api/customers/CUST-TEST/capabilities",
                       json={"cap_id": "CAP-9999"}).status_code == 404
    r = client.get("/api/customers/CUST-TEST")
    assert r.json()["required_capabilities"][0]["cap_id"] == "CAP-9001"
    r = client.delete("/api/customers/CUST-TEST/capabilities/CAP-9001")
    assert r.status_code == 200
    assert client.delete("/api/customers/CUST-TEST/capabilities/CAP-9001"
                         ).status_code == 404
    assert client.get("/api/customers/NOPE").status_code == 404


# ---------- audit + identity ----------

def test_audit_generation_and_actor_headers(client):
    client.patch("/api/capabilities/CAP-9001",
                 json={"version": 1, "working_name": "audit me"})
    client.patch("/api/capabilities/CAP-9001",
                 headers={"X-User-Ref": "dev-alice"},
                 json={"version": 2, "notes": "second edit"})

    import psycopg

    from tests.api.conftest import TEST_URL
    with psycopg.connect(TEST_URL) as conn:
        rows = conn.execute(
            "SELECT entity_type, entity_id, action, actor, "
            "before_json::text, after_json::text FROM audit_events "
            "WHERE entity_id='CAP-9001' ORDER BY audit_id").fetchall()
    assert len(rows) == 2
    assert rows[0][2] == "update" and rows[0][3] == "dev-user"
    assert '"working_name"' in rows[0][5] and '"_changed"' in rows[0][5]
    assert rows[1][3] == "dev-alice"                 # identity abstraction honored
    import json as _json
    after = _json.loads(rows[1][5])
    assert after["_changed"] == ["notes"]
