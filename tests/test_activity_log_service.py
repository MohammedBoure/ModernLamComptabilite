import json
import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from services.activity_log_service import ActivityAccessError, ActivityLogService  # noqa: E402


class FakeDatabase:
    current_actor = "director"

    def __init__(self, role="DIRECTION"):
        self.role = role
        self.commands = []

    def fetch_one(self, query, params=None):
        if "FROM Utilisateurs" in query:
            return {"role_code": self.role}
        if "COUNT(*)" in query:
            return {"count": 0}
        if "WHERE id_event" in query:
            return None
        return None

    def fetch_all(self, query, params=None):
        return []

    def execute(self, query, params=None):
        self.commands.append((query, params))
        return True, len(self.commands)


class ActivityLogServiceTests(unittest.TestCase):
    def test_record_keeps_business_amounts_and_redacts_sensitive_values(self):
        database = FakeDatabase()
        service = ActivityLogService(database)
        service.set_context("Caisse", "Mouvement Caisse")
        service.record(
            "director", "CASH_MOVEMENT_SAVED", "Mouvement_Caisse", 17,
            old_values={"montant": 10, "password_hash": "never-log", "nin": "123"},
            new_values={"montant": 15, "telephone": "0550"},
        )
        _, params = database.commands[-1]
        self.assertEqual(params[9], "CAISSE")
        self.assertEqual(params[10], "MOUVEMENT_CAISSE")
        self.assertEqual(json.loads(params[5])["montant"], 10)
        self.assertEqual(json.loads(params[5])["password_hash"], "[REDACTED]")
        self.assertEqual(json.loads(params[6])["telephone"], "[REDACTED]")

    def test_context_can_clear_a_tab_when_switching_sections(self):
        database = FakeDatabase()
        service = ActivityLogService(database)
        service.set_context("Caisse", "Mouvement Caisse")
        service.set_context(section_code="Rapports", tab_code=None)
        service.record("director", "REPORT_READY", "Report")
        _, params = database.commands[-1]
        self.assertEqual(params[9], "RAPPORTS")
        self.assertIsNone(params[10])

    def test_activity_log_denies_partial_manager_and_records_denial(self):
        database = FakeDatabase(role="DIRECTION")
        service = ActivityLogService(database)
        with self.assertRaises(ActivityAccessError):
            service.require_view_access("reader")
        self.assertEqual(len(database.commands), 1)
        self.assertIn("Audit_Events", database.commands[0][0])
        self.assertEqual(database.commands[0][1][8], "DENIED")

    def test_list_is_paginated_and_uses_requested_filters(self):
        database = FakeDatabase(role="ADMIN")
        result = ActivityLogService(database).list_events(
            "director", {"section_code": "CAISSE", "outcome": "SUCCESS"}, page=2, page_size=50
        )
        self.assertEqual(result, {"items": [], "total": 0, "page": 2, "page_size": 50})


if __name__ == "__main__":
    unittest.main()
