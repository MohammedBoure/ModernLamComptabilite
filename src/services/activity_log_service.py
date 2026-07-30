"""Immutable operational activity tracking backed by ``Audit_Events``."""

from __future__ import annotations

import csv
import json
import re
import uuid
from datetime import date, datetime
from pathlib import Path


class ActivityAccessError(PermissionError):
    """Raised when a user is not allowed to inspect the activity log."""


class ActivityLogService:
    VIEW_ROLES = {"ADMIN"}
    _UNSET = object()
    SENSITIVE_MARKERS = {
        "password", "hash", "token", "secret", "nin", "nss", "adresse",
        "address", "tel", "phone", "photo", "document", "storage_path",
    }

    def __init__(self, db_instance):
        self.db = db_instance

    @staticmethod
    def slug(value):
        value = re.sub(r"[^A-Za-z0-9]+", "_", str(value or "").strip()).strip("_")
        return value.upper()[:100] or None

    def set_context(self, section_code=_UNSET, tab_code=_UNSET):
        current = dict(getattr(self.db, "activity_context", {}) or {})
        if section_code is not self._UNSET:
            current["section_code"] = self.slug(section_code)
        if tab_code is not self._UNSET:
            current["tab_code"] = self.slug(tab_code)
        self.db.activity_context = current

    def current_context(self):
        return dict(getattr(self.db, "activity_context", {}) or {})

    def actor(self, actor_username=None):
        return actor_username or getattr(self.db, "current_actor", None) or "system"

    def actor_role(self, actor_username):
        if actor_username == "system":
            return "SYSTEM"
        row = self.db.fetch_one(
            "SELECT role_code FROM Utilisateurs WHERE username = %s AND is_active = 1", (actor_username,)
        )
        return row.get("role_code") if row else None

    def require_view_access(self, actor_username=None):
        actor = self.actor(actor_username)
        role = self.actor_role(actor)
        if role not in self.VIEW_ROLES:
            self.record(
                actor, "ACTIVITY_LOG_ACCESS_DENIED", "Activity_Log", outcome="DENIED",
                event_category="AUTHORIZATION", message="Activity log access denied.", actor_role=role,
            )
            raise ActivityAccessError("Only a full administrator can view the activity log.")
        return actor, role

    @classmethod
    def redact(cls, value, key_hint=""):
        normalized = str(key_hint or "").lower()
        if any(marker in normalized for marker in cls.SENSITIVE_MARKERS):
            return "[REDACTED]"
        if isinstance(value, dict):
            return {str(key): cls.redact(item, str(key)) for key, item in value.items()}
        if isinstance(value, (list, tuple)):
            return [cls.redact(item, key_hint) for item in value]
        if isinstance(value, (date, datetime)):
            return value.isoformat()
        return value

    def record(
        self, actor_username, action_code, entity_type, entity_id=None, period_id=None,
        old_values=None, new_values=None, reason=None, outcome="SUCCESS", event_category="BUSINESS",
        message=None, section_code=None, tab_code=None, actor_role=None, request_id=None,
    ):
        actor = self.actor(actor_username)
        context = self.current_context()
        role = actor_role if actor_role is not None else self.actor_role(actor)
        outcome = str(outcome or "SUCCESS").upper()
        if outcome not in {"SUCCESS", "DENIED", "FAILED"}:
            raise ValueError("Unsupported activity outcome.")
        payload = (
            actor, action_code, entity_type, str(entity_id) if entity_id is not None else None,
            period_id, json.dumps(self.redact(old_values), ensure_ascii=False) if old_values is not None else None,
            json.dumps(self.redact(new_values), ensure_ascii=False) if new_values is not None else None,
            reason, outcome, self.slug(section_code) or context.get("section_code"),
            self.slug(tab_code) or context.get("tab_code"), role, event_category,
            message, request_id or str(uuid.uuid4()),
        )
        success, event_id = self.db.execute(
            """INSERT INTO Audit_Events
               (actor_username, action_code, entity_type, entity_id, period_id, old_values, new_values,
                reason, outcome, section_code, tab_code, actor_role, event_category, message, request_id)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            payload,
        )
        return success, event_id

    def list_events(self, actor_username=None, filters=None, page=1, page_size=100):
        self.require_view_access(actor_username)
        filters = filters or {}
        page = max(1, int(page))
        page_size = min(200, max(1, int(page_size)))
        where, params = [], []
        filter_map = {
            "actor_username": "event.actor_username = %s",
            "section_code": "event.section_code = %s",
            "tab_code": "event.tab_code = %s",
            "action_code": "event.action_code = %s",
            "outcome": "event.outcome = %s",
            "event_category": "event.event_category = %s",
            "period_id": "event.period_id = %s",
        }
        for key, clause in filter_map.items():
            if filters.get(key) not in (None, "", "ALL"):
                where.append(clause)
                params.append(filters[key])
        if filters.get("date_from"):
            where.append("DATE(event.created_at) >= %s")
            params.append(filters["date_from"])
        if filters.get("date_to"):
            where.append("DATE(event.created_at) <= %s")
            params.append(filters["date_to"])
        if filters.get("search"):
            where.append("(event.entity_id LIKE %s OR event.entity_type LIKE %s OR event.reason LIKE %s OR event.message LIKE %s)")
            needle = f"%{filters['search']}%"
            params.extend([needle, needle, needle, needle])
        where_sql = " WHERE " + " AND ".join(where) if where else ""
        total_row = self.db.fetch_one("SELECT COUNT(*) AS count FROM Audit_Events event" + where_sql, tuple(params)) or {}
        rows = self.db.fetch_all(
            """SELECT event.* FROM Audit_Events event""" + where_sql +
            " ORDER BY event.created_at DESC, event.id_event DESC LIMIT %s OFFSET %s",
            tuple(params + [page_size, (page - 1) * page_size]),
        )
        return {"items": rows, "total": int(total_row.get("count") or 0), "page": page, "page_size": page_size}

    def get_event(self, event_id, actor_username=None):
        self.require_view_access(actor_username)
        event = self.db.fetch_one("SELECT * FROM Audit_Events WHERE id_event = %s", (event_id,))
        if not event:
            return None
        for key in ("old_values", "new_values"):
            raw = event.get(key)
            if isinstance(raw, str):
                try:
                    event[key] = self.redact(json.loads(raw))
                except json.JSONDecodeError:
                    event[key] = raw
            else:
                event[key] = self.redact(raw)
        return event

    def export_csv(self, output_path, actor_username=None, filters=None):
        actor, _ = self.require_view_access(actor_username)
        result = self.list_events(actor, filters, page=1, page_size=200)
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        headers = ["created_at", "actor_username", "actor_role", "section_code", "tab_code", "action_code", "entity_type", "entity_id", "outcome", "reason", "message"]
        with path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=headers)
            writer.writeheader()
            writer.writerows({key: row.get(key) for key in headers} for row in result["items"])
        self.record(actor, "ACTIVITY_LOG_EXPORTED", "Audit_Events", event_category="EXPORT", message=str(path))
        return path
