"""Period locking, role checks, audit, and accounting-policy services."""

from __future__ import annotations

import json
from datetime import date, datetime


class PeriodLockedError(PermissionError):
    """Raised when a write targets an accounting period that is not writable."""


class GovernanceManager:
    ADMIN_ROLES = {"ADMIN"}
    CLOSE_ROLES = {"ADMIN", "DIRECTION", "ACCOUNTANT"}
    WRITE_ROLES = {"ADMIN", "DIRECTION", "ACCOUNTANT", "CASHIER", "HR"}

    def __init__(self, db_instance):
        self.db = db_instance

    @staticmethod
    def _to_date(value):
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, date):
            return value
        return datetime.strptime(str(value), "%Y-%m-%d").date()

    def actor(self, actor_username=None):
        """Use the authenticated application actor instead of legacy ``system`` callers."""
        if actor_username and actor_username != "system":
            return actor_username
        return getattr(self.db, "current_actor", None) or actor_username or "system"

    def has_role(self, username, permitted_roles):
        user = self.db.fetch_one(
            "SELECT role_code, is_active FROM Utilisateurs WHERE username = %s", (username,)
        )
        return bool(user and user.get("is_active") and user.get("role_code") in permitted_roles)

    def assert_can_write(self, actor_username=None, permitted_roles=None):
        actor = self.actor(actor_username)
        # Bootstrap/migration scripts run before an application user exists. Production UI
        # calls resolve this to Database.current_actor during authentication.
        if actor == "system":
            return actor
        if not self.has_role(actor, permitted_roles or self.WRITE_ROLES):
            raise PermissionError("The current user is not permitted to create or modify this record.")
        return actor

    def get_or_create_period(self, activity_date, actor_username="system"):
        actor = self.actor(actor_username)
        activity_date = self._to_date(activity_date)
        period = self.db.fetch_one(
            "SELECT * FROM Accounting_Periods WHERE annee = %s AND mois = %s",
            (activity_date.year, activity_date.month),
        )
        if period:
            return period
        success, period_id = self.db.execute(
            """INSERT INTO Accounting_Periods (annee, mois, status, opened_by)
               VALUES (%s, %s, 'OPEN', %s)""",
            (activity_date.year, activity_date.month, actor),
        )
        if not success:
            raise RuntimeError("Unable to create the accounting period.")
        return {"id_period": period_id, "annee": activity_date.year, "mois": activity_date.month, "status": "OPEN"}

    def assert_writable_period(self, activity_date, actor_username="system"):
        actor = self.assert_can_write(actor_username)
        period = self.get_or_create_period(activity_date, actor)
        if period["status"] in {"CLOSED", "PENDING_CLOSE"}:
            raise PeriodLockedError(f"Accounting period {period['mois']:02}/{period['annee']} is locked.")
        return period

    def record_audit(self, actor_username, action_code, entity_type, entity_id=None, period_id=None, old_values=None, new_values=None, reason=None):
        actor = self.actor(actor_username)
        success, _ = self.db.execute(
            """INSERT INTO Audit_Events
               (actor_username, action_code, entity_type, entity_id, period_id, old_values, new_values, reason)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
            (
                actor, action_code, entity_type,
                str(entity_id) if entity_id is not None else None, period_id,
                json.dumps(old_values, ensure_ascii=False) if old_values is not None else None,
                json.dumps(new_values, ensure_ascii=False) if new_values is not None else None,
                reason,
            ),
        )
        return success

    def approved_policy_for(self, policy_code, effective_date):
        effective_date = self._to_date(effective_date)
        return self.db.fetch_one(
            """SELECT * FROM Calculation_Policies
               WHERE policy_code = %s AND approval_status = 'APPROVED' AND effective_from <= %s
               ORDER BY effective_from DESC, version_no DESC LIMIT 1""",
            (policy_code, effective_date),
        )

    def close_period(self, period_id, actor_username, close_note=""):
        actor = self.actor(actor_username)
        if not self.has_role(actor, self.CLOSE_ROLES):
            raise PermissionError("The current user cannot close accounting periods.")
        period = self.db.fetch_one("SELECT * FROM Accounting_Periods WHERE id_period = %s", (period_id,))
        if not period:
            raise ValueError("Unknown accounting period.")
        if period["status"] not in {"OPEN", "REOPENED"}:
            raise PeriodLockedError("Only open periods can be closed.")
        if not self.approved_policy_for("FINANCIAL_FORMULA", date(int(period["annee"]), int(period["mois"]), 1)):
            raise ValueError("An approved financial calculation policy is required before closing.")
        unexplained = self.db.fetch_one(
            """SELECT COUNT(*) AS count FROM Cloture_Caisse WHERE period_id = %s
               AND montant_reel <> montant_virtuel
               AND (remarques IS NULL OR TRIM(remarques) = '')""",
            (period_id,),
        )
        if unexplained and unexplained["count"]:
            raise ValueError("All cash differences require an explanation before closing.")
        drafts = self.db.fetch_one(
            "SELECT COUNT(*) AS count FROM Fiches_Paie WHERE period_id = %s AND statut = 'DRAFT'",
            (period_id,),
        )
        if drafts and drafts["count"]:
            raise ValueError("All payroll sheets must be validated before closing.")
        success, _ = self.db.execute(
            """UPDATE Accounting_Periods
               SET status = 'CLOSED', closed_at = NOW(), closed_by = %s, close_note = %s
               WHERE id_period = %s""",
            (actor, close_note, period_id),
        )
        if success:
            self.record_audit(actor, "PERIOD_CLOSED", "Accounting_Period", period_id, period_id, new_values={"status": "CLOSED"}, reason=close_note)
        return success

    def reopen_period(self, period_id, actor_username, reason):
        actor = self.actor(actor_username)
        if not reason or not reason.strip():
            raise ValueError("A reason is required to reopen a period.")
        if not self.has_role(actor, self.ADMIN_ROLES):
            raise PermissionError("Only an administrator can reopen an accounting period.")
        success, _ = self.db.execute(
            "UPDATE Accounting_Periods SET status = 'REOPENED' WHERE id_period = %s AND status = 'CLOSED'",
            (period_id,),
        )
        if success:
            self.db.execute(
                """INSERT INTO Period_Reopen_Requests
                   (period_id, requested_by, reason, status, approved_by, approved_at)
                   VALUES (%s, %s, %s, 'APPROVED', %s, NOW())""",
                (period_id, actor, reason.strip(), actor),
            )
            self.record_audit(actor, "PERIOD_REOPENED", "Accounting_Period", period_id, period_id, new_values={"status": "REOPENED"}, reason=reason.strip())
        return success
