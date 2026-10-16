"""Overnight QA — Scenario E (two-user stale edit) as a durable script.

Runs against a scratch copy of the governed data; drops the scratch DB after.
"""
import os
import subprocess
import sys
import time

import httpx
import psycopg

PSY = "postgresql+psycopg://tao:tao_dev_password@localhost:54323/tao_scenarios"
B = "http://127.0.0.1:8099"


def main():
    proc = subprocess.Popen(
        [".venv/bin/uvicorn", "app.main:app", "--port", "8099"], cwd=".",
        env={**os.environ, "DATABASE_URL": PSY, "LOG_FORMAT": "text"},
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(40):
            try:
                httpx.get(f"{B}/health", timeout=1)
                break
            except Exception:
                time.sleep(0.5)
        alice, bob = {"X-User-Ref": "alice-qa"}, {"X-User-Ref": "bob-qa"}
        v0 = httpx.get(f"{B}/api/capabilities/CAP-0002").json()["version"]
        r_bob = httpx.patch(f"{B}/api/capabilities/CAP-0002", headers=bob,
                            json={"version": v0, "notes": "bob-qa wins"})
        r_alice = httpx.patch(f"{B}/api/capabilities/CAP-0002", headers=alice,
                              json={"version": v0, "notes": "alice-qa stale write"})
        after = httpx.get(f"{B}/api/capabilities/CAP-0002").json()
        with psycopg.connect(PSY.replace("postgresql+psycopg://", "postgresql://")) as c, c.cursor() as cur:
            cur.execute(
                """SELECT * FROM audit_events
                   WHERE entity_type='capability' AND entity_id='CAP-0002'
                   ORDER BY 1 DESC LIMIT 2""")
            tail = cur.fetchall()
        detail = r_alice.json()["detail"].get("error") if r_alice.status_code == 409 else "-"
        print(f"SCENARIO E: bob-save={r_bob.status_code} (expect 200); "
              f"alice-stale={r_alice.status_code} (expect 409); "
              f"conflict-detail={detail}; final-notes={after['notes']!r}; "
              f"version={after['version']}; audit-tail={tail}")
    finally:
        proc.terminate()
        with psycopg.connect(
                "postgresql://tao:tao_dev_password@localhost:54323/postgres",
                autocommit=True) as c:
            c.execute("DROP DATABASE IF EXISTS tao_scenarios")
        print("scratch DB dropped")


if __name__ == "__main__":
    sys.exit(main())
