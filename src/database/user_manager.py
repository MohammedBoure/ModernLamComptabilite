"""Administrator-only user account lifecycle with operational audit events."""

from __future__ import annotations

import hashlib
import json
import re
import secrets

from services.activity_log_service import ActivityLogService


class UserManager:
    """Manage application accounts without ever returning or auditing passwords."""

    ROLE_CODES = ("ADMIN", "DIRECTION", "ACCOUNTANT", "CASHIER", "HR", "VIEWER")
    _USERNAME = re.compile(r"^[A-Za-z0-9._-]{3,100}$")
    _PASSWORD_ITERATIONS = 310_000

    def __init__(self, db_instance):
        self.db = db_instance
        self.activity = ActivityLogService(db_instance)

    def _actor(self, actor_username=None):
        return actor_username or getattr(self.db, "current_actor", None) or "system"

    def _assert_administrator(self, actor_username=None):
        actor = self._actor(actor_username)
        row = self.db.fetch_one(
            "SELECT role_code, is_active FROM Utilisateurs WHERE username = %s", (actor,)
        )
        if actor == "system" or not row or not row.get("is_active") or row.get("role_code") != "ADMIN":
            self.activity.record(
                actor, "USER_MANAGEMENT_ACCESS_DENIED", "Utilisateurs", outcome="DENIED",
                event_category="AUTHORIZATION", message="User-management permission denied.",
            )
            raise PermissionError("Only an active administrator can manage application users.")
        return actor

    @classmethod
    def _validate_account(cls, username, full_name, role_code, password=None, password_required=False):
        username = (username or "").strip()
        full_name = (full_name or "").strip()
        role_code = (role_code or "").strip().upper()
        if not cls._USERNAME.fullmatch(username):
            raise ValueError("Username must contain 3-100 letters, numbers, dots, hyphens, or underscores.")
        if not full_name:
            raise ValueError("Full name is required.")
        if role_code not in cls.ROLE_CODES:
            raise ValueError("Unsupported application role.")
        if password_required and len(password or "") < 8:
            raise ValueError("Password must contain at least 8 characters.")
        if password is not None and password != "" and len(password) < 8:
            raise ValueError("Password must contain at least 8 characters.")
        return username, full_name, role_code

    @classmethod
    def hash_password(cls, password):
        salt = secrets.token_bytes(16)
        digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, cls._PASSWORD_ITERATIONS)
        return f"pbkdf2_sha256${cls._PASSWORD_ITERATIONS}${salt.hex()}${digest.hex()}"

    def list_users(self, actor_username=None):
        self._assert_administrator(actor_username)
        return self.db.fetch_all(
            """SELECT id_utilisateur, username, nom_complet, role_code, is_active, created_at, updated_at
               FROM Utilisateurs ORDER BY username"""
        )

    def create_user(self, username, full_name, password, role_code, actor_username=None):
        actor = self._assert_administrator(actor_username)
        username, full_name, role_code = self._validate_account(
            username, full_name, role_code, password=password, password_required=True
        )
        if self.db.fetch_one("SELECT id_utilisateur FROM Utilisateurs WHERE username = %s", (username,)):
            raise ValueError("This username is already in use.")
        success, user_id = self.db.execute(
            """INSERT INTO Utilisateurs (username, password_hash, nom_complet, permissions, role_code, is_active)
               VALUES (%s, %s, %s, %s, %s, 1)""",
            (username, self.hash_password(password), full_name, json.dumps({"tabs": {}}), role_code),
        )
        if success:
            self.activity.record(
                actor, "USER_CREATED", "Utilisateurs", user_id,
                new_values={"username": username, "nom_complet": full_name, "role_code": role_code, "is_active": True},
                event_category="AUTHORIZATION", message="Application user account created.",
            )
        return success, user_id

    def update_user(self, user_id, username, full_name, role_code, password=None, actor_username=None):
        actor = self._assert_administrator(actor_username)
        username, full_name, role_code = self._validate_account(username, full_name, role_code, password=password)
        user = self.db.fetch_one("SELECT * FROM Utilisateurs WHERE id_utilisateur = %s", (user_id,))
        if not user:
            raise ValueError("Unknown application user.")
        duplicate = self.db.fetch_one(
            "SELECT id_utilisateur FROM Utilisateurs WHERE username = %s AND id_utilisateur <> %s", (username, user_id)
        )
        if duplicate:
            raise ValueError("This username is already in use.")
        if user.get("username") == actor and role_code != "ADMIN":
            raise ValueError("You cannot remove your own administrator role.")
        values = [username, full_name, role_code]
        query = "UPDATE Utilisateurs SET username = %s, nom_complet = %s, role_code = %s"
        if password:
            query += ", password_hash = %s"
            values.append(self.hash_password(password))
        query += " WHERE id_utilisateur = %s"
        values.append(user_id)
        success, _ = self.db.execute(query, tuple(values))
        if success:
            self.activity.record(
                actor, "USER_UPDATED", "Utilisateurs", user_id,
                old_values={key: user.get(key) for key in ("username", "nom_complet", "role_code")},
                new_values={"username": username, "nom_complet": full_name, "role_code": role_code, "password_reset": bool(password)},
                event_category="AUTHORIZATION", message="Application user account updated.",
            )
        return success

    def set_active(self, user_id, is_active, actor_username=None):
        actor = self._assert_administrator(actor_username)
        user = self.db.fetch_one("SELECT * FROM Utilisateurs WHERE id_utilisateur = %s", (user_id,))
        if not user:
            raise ValueError("Unknown application user.")
        desired = bool(is_active)
        if user.get("username") == actor and not desired:
            raise ValueError("You cannot deactivate your own account.")
        if user.get("role_code") == "ADMIN" and not desired and user.get("is_active"):
            count = self.db.fetch_one(
                "SELECT COUNT(*) AS count FROM Utilisateurs WHERE role_code = 'ADMIN' AND is_active = 1"
            ) or {}
            if int(count.get("count") or 0) <= 1:
                raise ValueError("The last active administrator cannot be deactivated.")
        success, _ = self.db.execute(
            "UPDATE Utilisateurs SET is_active = %s WHERE id_utilisateur = %s", (int(desired), user_id)
        )
        if success:
            self.activity.record(
                actor, "USER_STATUS_CHANGED", "Utilisateurs", user_id,
                old_values={"is_active": bool(user.get("is_active"))}, new_values={"is_active": desired},
                event_category="AUTHORIZATION", message="Application user account status changed.",
            )
        return success
