"""Compatibility checks for the additive activity-log migration."""

from __future__ import annotations

import importlib.util
import sys
import types
import unittest
from pathlib import Path


def load_migrations_module():
    """Load migration helpers without requiring a live MySQL driver/server."""
    mysql = types.ModuleType("mysql")
    connector = types.ModuleType("mysql.connector")
    connector.Error = Exception
    mysql.connector = connector
    sys.modules.setdefault("mysql", mysql)
    sys.modules.setdefault("mysql.connector", connector)
    path = Path(__file__).resolve().parents[1] / "src" / "database" / "base" / "migrations.py"
    spec = importlib.util.spec_from_file_location("activity_migrations_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class LegacyAuditCursor:
    """An old Audit_Events schema: no new columns or activity indexes exist."""

    def __init__(self):
        self.statements = []

    def execute(self, statement, parameters=None):
        self.statements.append((statement, parameters))

    @staticmethod
    def fetchone():
        return None


class ActivityMigrationTests(unittest.TestCase):
    def test_activity_upgrade_is_additive_for_existing_audit_rows(self):
        migrations = load_migrations_module()
        cursor = LegacyAuditCursor()

        migrations._apply_activity_tracking_schema(cursor)

        ddl = "\n".join(statement for statement, _ in cursor.statements)
        for column in ("outcome", "section_code", "tab_code", "actor_role", "event_category", "message", "request_id"):
            self.assertIn(f"ADD COLUMN `{column}`", ddl)
        for index in ("idx_audit_period", "idx_audit_created", "idx_audit_actor_created", "idx_audit_section_tab", "idx_audit_outcome"):
            self.assertIn(f"ADD INDEX `{index}`", ddl)
        self.assertNotIn("DROP ", ddl.upper())
        self.assertNotIn("DELETE ", ddl.upper())


if __name__ == "__main__":
    unittest.main()
