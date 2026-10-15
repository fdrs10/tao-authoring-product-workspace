"""Audit event writer (contract §30 original / Phase 3: actor+entity+before+after+changed fields).

One append-only row per material mutation, inside the same transaction as
the mutation. ``changed_fields`` is embedded as ``{"_changed": [...]}`` on
the top level of before/after payloads so consumers can diff quickly; full
before/after snapshots of the changed fields are always included.
"""

import json
from typing import Any

import psycopg


def record_audit(
    cur: psycopg.Cursor,
    entity_type: str,
    entity_id: str,
    action: str,
    actor: str,
    before: dict[str, Any] | None,
    after: dict[str, Any] | None,
    changed_fields: list[str],
) -> None:
    payload_before = dict(before or {})
    payload_after = dict(after or {})
    payload_before["_changed"] = changed_fields
    payload_after["_changed"] = changed_fields
    cur.execute(
        """
        INSERT INTO audit_events (entity_type, entity_id, action, actor,
                                  before_json, after_json)
        VALUES (%s, %s, %s, %s, %s::jsonb, %s::jsonb)
        """,
        (
            entity_type,
            entity_id,
            action,
            actor,
            json.dumps(payload_before, default=str),
            json.dumps(payload_after, default=str),
        ),
    )
