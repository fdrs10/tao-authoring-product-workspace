"""Phase 5 API tests — Roadmap/Outcome/Milestone contract (§18/§19).

Covers: outcome narratives (versioned, audited, NULL-able, 409), timing PATCH
returning the new version, milestone position updates with optimistic
concurrency. Phase 3 suites already cover capability/timing basics; here we
add the Phase 5 surface.
"""

import httpx
import pytest


# ---------- outcomes (§6: Roadmap | Outcome, server-persisted) ----------

def test_outcomes_get_creates_three_rows(client):
    r = client.get("/api/outcomes")
    assert r.status_code == 200
    data = r.json()
    assert data["count"] == 3
    assert [i["horizon"] for i in data["items"]] == ["0-6m", "7-24m", "tail"]
    for item in data["items"]:
        assert item["narrative"] is None      # never invented content
        assert item["version"] == 1


def test_outcome_patch_updates_version_and_audit(client):
    r = client.patch("/api/outcomes/0-6m",
                     json={"version": 1, "narrative": "First 6 months narrative."})
    assert r.status_code == 200 and r.json()["version"] == 2
    r2 = client.get("/api/outcomes")
    row = [i for i in r2.json()["items"] if i["horizon"] == "0-6m"][0]
    assert row["narrative"] == "First 6 months narrative."
    assert row["version"] == 2
    assert row["updated_by"] == "dev-user"   # actor default when no X-User-Ref


def test_outcome_stale_version_409_never_overwrites(client):
    client.patch("/api/outcomes/7-24m", json={"version": 1, "narrative": "v1 text"})
    r = client.patch("/api/outcomes/7-24m",
                     json={"version": 1, "narrative": "stale overwrite attempt"})
    assert r.status_code == 409
    assert r.json()["detail"]["error"] == "version_conflict"
    assert r.json()["detail"]["current_version"] == 2
    # server text survived
    row = [i for i in client.get("/api/outcomes").json()["items"]
           if i["horizon"] == "7-24m"][0]
    assert row["narrative"] == "v1 text"


def test_outcome_unknown_horizon_404(client):
    r = client.patch("/api/outcomes/2029", json={"version": 1, "narrative": "x"})
    assert r.status_code == 404


def test_outcome_explicit_null_narrative_allowed(client):
    client.patch("/api/outcomes/tail", json={"version": 1, "narrative": "temp"})
    r = client.patch("/api/outcomes/tail", json={"version": 2, "narrative": None})
    assert r.status_code == 200
    row = [i for i in client.get("/api/outcomes").json()["items"]
           if i["horizon"] == "tail"][0]
    assert row["narrative"] is None


# ---------- roadmap timing (§7: persisted, optimistic) ----------

def test_roadmap_timing_patch_returns_new_version(client):
    r1 = client.patch("/api/roadmap/CAP-9001",
                      json={"version": 1, "start_month": 2, "duration_months": 4})
    assert r1.status_code == 200 and r1.json()["version"] == 2
    r2 = client.patch("/api/roadmap/CAP-9001",
                      json={"version": 2, "start_month": 5, "duration_months": 2})
    assert r2.status_code == 200 and r2.json()["version"] == 3
    view = client.get("/api/roadmap", params={"admission": ""}).json()
    row = [i for i in view["items"] if i["cap_id"] == "CAP-9001"][0]
    assert (row["start_month"], row["duration_months"], row["timing_version"]) == (5, 2, 3)


def test_roadmap_timing_conflict_detail(client):
    client.patch("/api/roadmap/CAP-9001",
                 json={"version": 1, "start_month": 1, "duration_months": 2})
    r = client.patch("/api/roadmap/CAP-9001",
                     json={"version": 1, "start_month": 9, "duration_months": 9})
    assert r.status_code == 409
    d = r.json()["detail"]
    assert d["error"] == "version_conflict" and d["current_version"] == 2


# ---------- milestones (§10: shared dataset, versioned) ----------

def test_milestone_patch_position_and_conflict(client):
    r0 = client.post("/api/milestones", json={
        "milestone_id": "M1", "name": "Fixture milestone",
        "position_month": 4, "scope_type": "global"})
    assert r0.status_code == 201

    r = client.patch("/api/milestones/M1", json={"version": 1, "position_month": 6})
    assert r.status_code == 200 and r.json()["version"] == 2
    row = [m for m in client.get("/api/milestones").json()["items"]
           if m["milestone_id"] == "M1"][0]
    assert row["position_month"] == 6

    r2 = client.patch("/api/milestones/M1", json={"version": 1, "position_month": 9})
    assert r2.status_code == 409
    assert r2.json()["detail"]["current_version"] == 2
    # server value survived the refused write
    row = [m for m in client.get("/api/milestones").json()["items"]
           if m["milestone_id"] == "M1"][0]
    assert row["position_month"] == 6


def test_customer_ts_codes_refused_422(client):
    r = client.post("/api/customers", json={
        "customer_id": "C-TS", "name": "TS customer",
        "earliest_milestone_interval": "TS1"})
    assert r.status_code == 422
    assert "TS" in str(r.json()["detail"])
