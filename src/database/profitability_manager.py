"""Approved, auditable profitability transfers between accounting periods."""

from __future__ import annotations

try:
    from .governance_manager import GovernanceManager
except ImportError:  # Direct manager execution used by legacy tests/tools.
    from governance_manager import GovernanceManager


class ProfitabilityManager:
    APPROVAL_ROLES = {"ADMIN", "DIRECTION", "ACCOUNTANT"}

    def __init__(self, db_instance):
        self.db = db_instance
        self.governance = GovernanceManager(db_instance)

    def create_movement(
        self, source_period_id, destination_period_id, amount, designation,
        actor_username, movement_type="CARRYOVER",
    ):
        if source_period_id == destination_period_id:
            raise ValueError("Source and destination periods must be different.")
        if float(amount) <= 0:
            raise ValueError("Profitability movement amount must be positive.")
        if movement_type not in {"CARRYOVER", "ALLOCATION", "REVERSAL"}:
            raise ValueError("Unsupported profitability movement type.")
        destination = self.db.fetch_one(
            "SELECT * FROM Accounting_Periods WHERE id_period = %s", (destination_period_id,)
        )
        if not destination:
            raise ValueError("Unknown destination accounting period.")
        self.governance.assert_writable_period(
            f"{destination['annee']}-{int(destination['mois']):02d}-01", actor_username
        )
        source = self.db.fetch_one(
            "SELECT * FROM Accounting_Periods WHERE id_period = %s", (source_period_id,)
        )
        if not source:
            raise ValueError("Unknown source accounting period.")
        success, entity_id = self.db.execute(
            """INSERT INTO Profitability_Movements
               (source_period_id, destination_period_id, amount, movement_type, designation, created_by)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (source_period_id, destination_period_id, amount, movement_type, designation, actor_username),
        )
        if success:
            self.governance.record_audit(
                actor_username, "PROFITABILITY_MOVEMENT_CREATED", "Profitability_Movements", entity_id,
                destination_period_id,
                new_values={"source_period_id": source_period_id, "amount": amount, "movement_type": movement_type},
                reason=designation,
            )
        return success, entity_id

    def approve_movement(self, movement_id, actor_username):
        if not self.governance.has_role(actor_username, self.APPROVAL_ROLES):
            raise PermissionError("The current user cannot approve profitability movements.")
        movement = self.db.fetch_one(
            "SELECT * FROM Profitability_Movements WHERE id_movement = %s", (movement_id,)
        )
        if not movement or movement["status"] != "PENDING":
            raise ValueError("Only pending profitability movements can be approved.")
        destination = self.db.fetch_one(
            "SELECT * FROM Accounting_Periods WHERE id_period = %s", (movement["destination_period_id"],)
        )
        self.governance.assert_writable_period(
            f"{destination['annee']}-{int(destination['mois']):02d}-01", actor_username
        )
        success, _ = self.db.execute(
            """UPDATE Profitability_Movements
               SET status = 'APPROVED', approved_by = %s, approved_at = NOW()
               WHERE id_movement = %s AND status = 'PENDING'""",
            (actor_username, movement_id),
        )
        if success:
            self.db.execute(
                """INSERT IGNORE INTO Monthly_Carryovers
                   (period_id, carryover_type, amount, source_period_id, notes)
                   VALUES (%s, 'PROFITABILITY', %s, %s, %s)""",
                (movement["destination_period_id"], movement["amount"], movement["source_period_id"], movement["designation"]),
            )
            self.governance.record_audit(
                actor_username, "PROFITABILITY_MOVEMENT_APPROVED", "Profitability_Movements", movement_id,
                movement["destination_period_id"], new_values={"status": "APPROVED"},
            )
        return success

    def void_movement(self, movement_id, actor_username, reason):
        if not (reason or "").strip():
            raise ValueError("A reason is required to void a profitability movement.")
        if not self.governance.has_role(actor_username, {"ADMIN"}):
            raise PermissionError("Only an administrator can void profitability movements.")
        movement = self.db.fetch_one(
            "SELECT * FROM Profitability_Movements WHERE id_movement = %s", (movement_id,)
        )
        if not movement or movement["status"] == "VOID":
            raise ValueError("The profitability movement is not available for voiding.")
        success, _ = self.db.execute(
            "UPDATE Profitability_Movements SET status = 'VOID' WHERE id_movement = %s", (movement_id,)
        )
        if success:
            self.governance.record_audit(
                actor_username, "PROFITABILITY_MOVEMENT_VOIDED", "Profitability_Movements", movement_id,
                movement["destination_period_id"], old_values={"status": movement["status"]}, reason=reason.strip(),
            )
        return success

    def list_for_period(self, period_id):
        return self.db.fetch_all(
            """SELECT * FROM Profitability_Movements
               WHERE source_period_id = %s OR destination_period_id = %s
               ORDER BY created_at DESC, id_movement DESC""",
            (period_id, period_id),
        )
