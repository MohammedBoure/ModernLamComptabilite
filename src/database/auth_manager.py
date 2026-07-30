"""Authentication with role-derived access and migration-safe password hashing."""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import secrets

from database import data_manager


ROLE_SECTIONS = {
    "ADMIN": ["Dashboard", "HR", "Caisse", "Cloture", "Fournisseurs", "Partenaires", "Banque", "Rapports", "DonneesBase", "Users", "Activity", "Settings"],
    "DIRECTION": ["Dashboard", "HR", "Caisse", "Cloture", "Fournisseurs", "Partenaires", "Banque", "Rapports", "DonneesBase", "Settings"],
    "ACCOUNTANT": ["Dashboard", "Caisse", "Cloture", "Fournisseurs", "Partenaires", "Banque", "Rapports"],
    "CASHIER": ["Dashboard", "Caisse", "Cloture", "Banque"],
    "HR": ["Dashboard", "HR", "Rapports"],
    "VIEWER": ["Dashboard", "Rapports"],
}
PASSWORD_ITERATIONS = 310_000


class AuthManager:
    @staticmethod
    def hash_password(password):
        """Store passwords as PBKDF2 records; plain text is never newly written."""
        salt = secrets.token_bytes(16)
        digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PASSWORD_ITERATIONS)
        return "pbkdf2_sha256${}${}${}".format(
            PASSWORD_ITERATIONS, salt.hex(), digest.hex()
        )

    @staticmethod
    def check_password(stored_password, supplied_password):
        """Accept legacy plain text once so its account can be upgraded on login."""
        if not stored_password or supplied_password is None:
            return False
        if not stored_password.startswith("pbkdf2_sha256$"):
            return hmac.compare_digest(str(stored_password), str(supplied_password))
        try:
            algorithm, iterations, salt_hex, expected_hex = stored_password.split("$", 3)
            if algorithm != "pbkdf2_sha256":
                return False
            actual = hashlib.pbkdf2_hmac(
                "sha256", supplied_password.encode("utf-8"), bytes.fromhex(salt_hex), int(iterations)
            ).hex()
            return hmac.compare_digest(expected_hex, actual)
        except (TypeError, ValueError):
            return False

    @staticmethod
    def is_legacy_password(stored_password):
        return bool(stored_password) and not str(stored_password).startswith("pbkdf2_sha256$")

    @staticmethod
    def permissions_for_role(role_code):
        return {"sections": ROLE_SECTIONS.get(role_code or "VIEWER", ROLE_SECTIONS["VIEWER"]), "tabs": {}}

    @staticmethod
    def _hydrate_user(user):
        if not user:
            return None
        role_code = user.get("role_code") or "VIEWER"
        user["role_code"] = role_code
        # Roles are authoritative; legacy JSON can only carry tab-level refinements.
        try:
            legacy = json.loads(user.get("permissions") or "{}")
        except (TypeError, json.JSONDecodeError):
            legacy = {}
        user["permissions"] = AuthManager.permissions_for_role(role_code)
        # The partial administrator is intentionally unrestricted inside all
        # operational sections; ignore legacy tab restrictions for this role.
        if role_code not in {"ADMIN", "DIRECTION"}:
            user["permissions"]["tabs"] = legacy.get("tabs", {}) if isinstance(legacy, dict) else {}
        return user

    @staticmethod
    def initialize_default_admin():
        """Create a PBKDF2-protected administrator if no users exist."""
        try:
            result = data_manager.db.fetch_one("SELECT COUNT(*) AS count FROM Utilisateurs")
            if result and result["count"] == 0:
                query = """
                    INSERT INTO Utilisateurs (username, password_hash, nom_complet, permissions, role_code, is_active)
                    VALUES (%s, %s, %s, %s, 'ADMIN', 1)
                """
                permissions = json.dumps(AuthManager.permissions_for_role("ADMIN"))
                data_manager.db.execute(query, ("admin", AuthManager.hash_password("admin123"), "Administrateur", permissions))
                logging.info("Default administrator account created; change its password before production use.")
        except Exception as error:
            logging.error("Error initializing default admin: %s", error)

    @staticmethod
    def authenticate(username, password):
        """Authenticate an active user and transparently upgrade legacy credentials."""
        try:
            user = data_manager.db.fetch_one(
                "SELECT * FROM Utilisateurs WHERE username = %s AND is_active = 1", (username,)
            )
            if not user or not AuthManager.check_password(user.get("password_hash"), password):
                data_manager.activity.record(
                    username or "anonymous", "LOGIN_FAILED", "Authentication", outcome="FAILED",
                    event_category="AUTHENTICATION", message="Invalid username or password.",
                )
                return None
            if AuthManager.is_legacy_password(user["password_hash"]):
                id_column = "id_user" if "id_user" in user else "id_utilisateur"
                data_manager.db.execute(
                    f"UPDATE Utilisateurs SET password_hash = %s WHERE {id_column} = %s",
                    (AuthManager.hash_password(password), user.get(id_column)),
                )
            data_manager.db.current_actor = user["username"]
            hydrated = AuthManager._hydrate_user(user)
            data_manager.activity.record(
                user["username"], "LOGIN_SUCCEEDED", "Authentication", event_category="AUTHENTICATION",
                message="Authenticated application session started.", actor_role=hydrated.get("role_code"),
            )
            return hydrated
        except Exception as error:
            logging.error("Error during authentication: %s", error)
            return None
    @staticmethod
    def get_user_by_username(username):
        try:
            user = data_manager.db.fetch_one(
                "SELECT * FROM Utilisateurs WHERE username = %s AND is_active = 1", (username,)
            )
            if user:
                data_manager.db.current_actor = user["username"]
            return AuthManager._hydrate_user(user)
        except Exception as error:
            logging.error("Error getting user by username: %s", error)
            return None
