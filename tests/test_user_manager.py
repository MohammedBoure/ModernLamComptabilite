"""Unit tests for administrator-only application account management."""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


def load_user_manager():
    path = Path(__file__).resolve().parents[1] / "src" / "database" / "user_manager.py"
    spec = importlib.util.spec_from_file_location("user_manager_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.UserManager


class FakeDatabase:
    current_actor = "admin"

    def __init__(self, role="ADMIN"):
        self.role = role
        self.commands = []

    def fetch_one(self, query, params=None):
        if "role_code, is_active" in query:
            return {"role_code": self.role, "is_active": 1}
        if "id_utilisateur FROM Utilisateurs WHERE username" in query:
            return None
        return None

    def fetch_all(self, query, params=None):
        return []

    def execute(self, query, params=None):
        self.commands.append((query, params))
        return True, len(self.commands)


class UserManagerTests(unittest.TestCase):
    def test_admin_can_create_user_without_logging_the_password(self):
        manager = load_user_manager()(FakeDatabase())
        success, user_id = manager.create_user("cashier.one", "Cashier One", "safe-password", "CASHIER")

        self.assertTrue(success)
        self.assertEqual(user_id, 1)
        user_insert = manager.db.commands[0]
        self.assertIn("INSERT INTO Utilisateurs", user_insert[0])
        self.assertTrue(user_insert[1][1].startswith("pbkdf2_sha256$"))
        self.assertNotIn("safe-password", json.dumps(user_insert[1]))
        audit_params = manager.db.commands[1][1]
        self.assertEqual(audit_params[1], "USER_CREATED")
        self.assertNotIn("safe-password", json.dumps(audit_params))

    def test_non_admin_cannot_manage_users_and_denial_is_audited(self):
        manager = load_user_manager()(FakeDatabase(role="VIEWER"))
        with self.assertRaises(PermissionError):
            manager.list_users()
        self.assertEqual(manager.db.commands[-1][1][1], "USER_MANAGEMENT_ACCESS_DENIED")
        self.assertEqual(manager.db.commands[-1][1][8], "DENIED")


if __name__ == "__main__":
    unittest.main()
