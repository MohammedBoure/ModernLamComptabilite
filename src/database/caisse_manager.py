"""Cash, coffre, and closure operations guarded by accounting governance."""

from __future__ import annotations

try:
    from .financial_calculations import calculate_cash_closure, calculate_coffre_summary
    from .governance_manager import GovernanceManager
except ImportError:  # Direct manager execution used by legacy tests/tools.
    from financial_calculations import calculate_cash_closure, calculate_coffre_summary
    from governance_manager import GovernanceManager


class CaisseManager:
    def __init__(self, db_instance):
        self.db = db_instance
        self.governance = GovernanceManager(db_instance)

    @staticmethod
    def _row(result):
        return result[0] if result else {}

    def get_caisse_movements(self, month=None, year=None):
        query = "SELECT * FROM Mouvement_Caisse"
        params = []
        if month and year:
            query += " WHERE MONTH(date_mouvement) = %s AND YEAR(date_mouvement) = %s"
            params.extend([month, year])
        query += " ORDER BY date_mouvement DESC"
        return self.db.fetch_all(query, tuple(params) if params else None)

    def add_caisse_movement(
        self, date_mouvement, caisse_cv, caisse_c, tpe, depenses, remboursement,
        convention, sous_traitants, actor_username="system",
    ):
        period = self.governance.assert_writable_period(date_mouvement, actor_username)
        query = """
            INSERT INTO Mouvement_Caisse
            (date_mouvement, caisse_cv, caisse_c, tpe, depenses, remboursement, convention, sous_traitants, period_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            caisse_cv=VALUES(caisse_cv), caisse_c=VALUES(caisse_c), tpe=VALUES(tpe),
            depenses=VALUES(depenses), remboursement=VALUES(remboursement),
            convention=VALUES(convention), sous_traitants=VALUES(sous_traitants), period_id=VALUES(period_id)
        """
        values = (caisse_cv, caisse_c, tpe, depenses, remboursement, convention, sous_traitants)
        success, entity_id = self.db.execute(query, (date_mouvement, *values, period["id_period"]))
        if success:
            self.governance.record_audit(
                actor_username, "CASH_MOVEMENT_SAVED", "Mouvement_Caisse", entity_id,
                period["id_period"], new_values={"date": str(date_mouvement), "values": list(values)},
            )
        return success

    def get_clotures(self, month=None, year=None):
        query = "SELECT * FROM Cloture_Caisse"
        params = []
        if month and year:
            query += " WHERE MONTH(date_cloture) = %s AND YEAR(date_cloture) = %s"
            params.extend([month, year])
        query += " ORDER BY date_cloture DESC"
        return self.db.fetch_all(query, tuple(params) if params else None)

    def add_cloture(self, date_cloture, utilisateur, montant_reel, montant_virtuel, remarques, actor_username=None):
        actor = actor_username or utilisateur or "system"
        closure = calculate_cash_closure(montant_reel, montant_virtuel)
        if closure["difference"] != 0 and not (remarques or "").strip():
            raise ValueError("A note is required when the real and virtual cash amounts differ.")
        period = self.governance.assert_writable_period(date_cloture, actor)
        self.db.execute(
            "INSERT IGNORE INTO Mouvement_Caisse (date_mouvement, period_id) VALUES (%s, %s)",
            (date_cloture, period["id_period"]),
        )
        success, entity_id = self.db.execute(
            """INSERT INTO Cloture_Caisse
               (date_cloture, utilisateur, montant_reel, montant_virtuel, remarques, period_id)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (date_cloture, utilisateur, closure["montant_reel"], closure["montant_virtuel"], remarques, period["id_period"]),
        )
        if success:
            self.governance.record_audit(
                actor, "CASH_CLOSURE_CREATED", "Cloture_Caisse", entity_id, period["id_period"],
                new_values=closure, reason=(remarques or "").strip() or None,
            )
        return success

    def get_depenses_caisse(self, month=None, year=None):
        query = "SELECT * FROM Details_Depenses_Caisse"
        params = []
        if month and year:
            query += " WHERE MONTH(date_mouvement) = %s AND YEAR(date_mouvement) = %s"
            params.extend([month, year])
        query += " ORDER BY date_mouvement DESC"
        return self.db.fetch_all(query, tuple(params) if params else None)

    def add_depense_caisse(self, date_mouvement, designation, montant, actor_username="system"):
        period = self.governance.assert_writable_period(date_mouvement, actor_username)
        self.db.execute(
            "INSERT IGNORE INTO Mouvement_Caisse (date_mouvement, period_id) VALUES (%s, %s)",
            (date_mouvement, period["id_period"]),
        )
        success, entity_id = self.db.execute(
            """INSERT INTO Details_Depenses_Caisse (date_mouvement, designation, montant, period_id)
               VALUES (%s, %s, %s, %s)""",
            (date_mouvement, designation, montant, period["id_period"]),
        )
        if success:
            self.governance.record_audit(
                actor_username, "CASH_EXPENSE_CREATED", "Details_Depenses_Caisse", entity_id,
                period["id_period"], new_values={"designation": designation, "montant": montant},
            )
        return success

    def get_etat_differences(self, month=None, year=None):
        query = """
            SELECT utilisateur, SUM(montant_reel - montant_virtuel) AS montant_total
            FROM Cloture_Caisse
        """
        params = []
        if month and year:
            query += " WHERE MONTH(date_cloture) = %s AND YEAR(date_cloture) = %s"
            params.extend([month, year])
        query += " GROUP BY utilisateur ORDER BY utilisateur"
        return self.db.fetch_all(query, tuple(params) if params else None)

    def get_coffre_movements(self, month=None, year=None):
        query = "SELECT * FROM Mouvement_Coffre"
        params = []
        if month and year:
            query += " WHERE MONTH(date_transaction) = %s AND YEAR(date_transaction) = %s"
            params.extend([month, year])
        query += " ORDER BY date_transaction DESC"
        return self.db.fetch_all(query, tuple(params) if params else None)

    def _period_for(self, month, year):
        if not month or not year:
            return None
        return self.db.fetch_one(
            "SELECT id_period FROM Accounting_Periods WHERE mois = %s AND annee = %s", (month, year)
        )

    def get_coffre_summary(self, month=None, year=None):
        date_filter = ""
        params = ()
        if month and year:
            date_filter = " WHERE MONTH(date_mouvement) = %s AND YEAR(date_mouvement) = %s"
            params = (month, year)
        cash = self.db.fetch_one(
            """SELECT COALESCE(SUM(caisse_cv), 0) AS caisse_cv, COALESCE(SUM(caisse_c), 0) AS caisse_c,
                      COALESCE(SUM(tpe), 0) AS tpe FROM Mouvement_Caisse""" + date_filter,
            params or None,
        ) or {}
        coffre_filter = ""
        if month and year:
            coffre_filter = " WHERE MONTH(date_transaction) = %s AND YEAR(date_transaction) = %s"
        coffre = self.db.fetch_one(
            """SELECT
                COALESCE(SUM(CASE WHEN type_operation = 'ENTREE' AND categorie_operation = 'ENTREES_SUPP'
                    AND payment_status = 'PAID' THEN montant ELSE 0 END), 0) AS entrees_supp,
                COALESCE(SUM(CASE WHEN type_operation = 'SORTIE' AND payment_status = 'PAID'
                    THEN montant ELSE 0 END), 0) AS sorties
               FROM Mouvement_Coffre""" + coffre_filter,
            params or None,
        ) or {}
        partner_filter = ""
        if month and year:
            partner_filter = " WHERE MONTH(payment.date_paiement) = %s AND YEAR(payment.date_paiement) = %s"
        partners = self.db.fetch_one(
            """SELECT
                COALESCE(SUM(CASE WHEN partner.type_partenaire = 'SOUS_TRAITANT' THEN payment.montant_verse ELSE 0 END), 0) AS sous_traitants_payes,
                COALESCE(SUM(CASE WHEN partner.type_partenaire = 'CONVENTION' THEN payment.montant_verse ELSE 0 END), 0) AS conventions_payees
               FROM Paiements_Partenaires payment
               JOIN Operations_Partenaires operation_row ON operation_row.id_operation = payment.id_operation
               JOIN Partenaires partner ON partner.id_partenaire = operation_row.id_partenaire""" + partner_filter,
            params or None,
        ) or {}
        profitability_in = 0
        period = self._period_for(month, year)
        if period:
            row = self.db.fetch_one(
                """SELECT COALESCE(SUM(amount), 0) AS amount FROM Profitability_Movements
                   WHERE destination_period_id = %s AND status = 'APPROVED'""",
                (period["id_period"],),
            ) or {}
            profitability_in = row.get("amount", 0)
        return calculate_coffre_summary(cash, coffre, partners, profitability_in)

    def add_coffre_movement(
        self, date_transaction, type_operation, categorie_operation, montant, designation,
        actor_username="system", payment_status="PAID", remarks=None,
    ):
        period = self.governance.assert_writable_period(date_transaction, actor_username)
        if payment_status not in {"PENDING", "PAID", "VOID"}:
            raise ValueError("Unsupported coffre payment status.")
        success, entity_id = self.db.execute(
            """INSERT INTO Mouvement_Coffre
               (date_transaction, type_operation, categorie_operation, montant, designation, period_id, payment_status, remarks)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
            (date_transaction, type_operation, categorie_operation, montant, designation, period["id_period"], payment_status, remarks),
        )
        if success:
            self.governance.record_audit(
                actor_username, "COFFRE_MOVEMENT_CREATED", "Mouvement_Coffre", entity_id,
                period["id_period"], new_values={"type": type_operation, "category": categorie_operation, "amount": montant, "payment_status": payment_status},
                reason=remarks,
            )
        return success
