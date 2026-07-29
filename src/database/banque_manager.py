"""Bank, SGA, vehicle, and collection operations."""

from __future__ import annotations

from datetime import date, datetime

try:
    from .governance_manager import GovernanceManager
except ImportError:  # Direct manager execution used by legacy tests/tools.
    from governance_manager import GovernanceManager


class BanqueManager:
    def __init__(self, db_instance):
        self.db = db_instance
        self.governance = GovernanceManager(db_instance)

    @staticmethod
    def _year(value=None):
        if value is None:
            return date.today().year
        if isinstance(value, datetime):
            return value.year
        if isinstance(value, date):
            return value.year
        return int(value)

    def get_sga_transactions(self, year=None):
        selected_year = self._year(year)
        return self.db.fetch_all(
            """SELECT * FROM Compte_SGA
               WHERE YEAR(date_transaction) = %s AND is_void = 0
               ORDER BY date_transaction ASC, id_transaction ASC""",
            (selected_year,),
        )

    def get_solde_initial(self, year=None):
        selected_year = self._year(year)
        row = self.db.fetch_one(
            "SELECT montant FROM SGA_Opening_Balances WHERE annee = %s", (selected_year,)
        )
        return float(row["montant"]) if row else 0.0

    def update_solde_initial(self, montant, year=None, actor_username="system", source_year=None, notes=None):
        selected_year = self._year(year)
        period = self.governance.assert_writable_period(f"{selected_year}-01-01", actor_username)
        success, _ = self.db.execute(
            """INSERT INTO SGA_Opening_Balances
               (annee, montant, source_year, notes, created_by, updated_by, updated_at)
               VALUES (%s, %s, %s, %s, %s, %s, NOW())
               ON DUPLICATE KEY UPDATE montant=VALUES(montant), source_year=VALUES(source_year),
                   notes=VALUES(notes), updated_by=VALUES(updated_by), updated_at=NOW()""",
            (selected_year, montant, source_year, notes, actor_username, actor_username),
        )
        if success:
            self.governance.record_audit(
                actor_username, "SGA_OPENING_BALANCE_SAVED", "SGA_Opening_Balances", selected_year,
                period["id_period"], new_values={"year": selected_year, "amount": montant, "source_year": source_year}, reason=notes,
            )
        return success

    def get_solde_actuel(self, year=None):
        selected_year = self._year(year)
        row = self.db.fetch_one(
            """SELECT COALESCE(SUM(entrees - sorties), 0) AS movement_total
               FROM Compte_SGA WHERE YEAR(date_transaction) = %s AND is_void = 0""",
            (selected_year,),
        ) or {}
        return self.get_solde_initial(selected_year) + float(row.get("movement_total") or 0)

    def add_sga_transaction(
        self, date_transaction, n_cheque, beneficiaire, entrees, sorties, designation,
        actor_username="system",
    ):
        period = self.governance.assert_writable_period(date_transaction, actor_username)
        success, entity_id = self.db.execute(
            """INSERT INTO Compte_SGA
               (date_transaction, n_cheque, beneficiaire, entrees, sorties, designation, period_id)
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (date_transaction, n_cheque, beneficiaire, entrees, sorties, designation, period["id_period"]),
        )
        if success:
            self.governance.record_audit(
                actor_username, "SGA_TRANSACTION_CREATED", "Compte_SGA", entity_id, period["id_period"],
                new_values={"date": str(date_transaction), "entrees": entrees, "sorties": sorties, "designation": designation},
            )
        return success

    def update_sga_transaction(
        self, id_transaction, date_transaction, n_cheque, beneficiaire, entrees, sorties,
        designation, actor_username="system",
    ):
        old = self.db.fetch_one("SELECT * FROM Compte_SGA WHERE id_transaction = %s", (id_transaction,))
        if not old or old.get("is_void"):
            raise ValueError("The SGA transaction does not exist or has already been voided.")
        self.governance.assert_writable_period(old["date_transaction"], actor_username)
        period = self.governance.assert_writable_period(date_transaction, actor_username)
        success, _ = self.db.execute(
            """UPDATE Compte_SGA
               SET date_transaction=%s, n_cheque=%s, beneficiaire=%s, entrees=%s, sorties=%s,
                   designation=%s, period_id=%s
               WHERE id_transaction=%s AND is_void=0""",
            (date_transaction, n_cheque, beneficiaire, entrees, sorties, designation, period["id_period"], id_transaction),
        )
        if success:
            self.governance.record_audit(
                actor_username, "SGA_TRANSACTION_UPDATED", "Compte_SGA", id_transaction, period["id_period"],
                old_values={"date": str(old["date_transaction"]), "entrees": old.get("entrees"), "sorties": old.get("sorties")},
                new_values={"date": str(date_transaction), "entrees": entrees, "sorties": sorties, "designation": designation},
                reason="Accounting transaction corrected",
            )
        return success

    def delete_sga_transaction(self, id_transaction, reason, actor_username="system"):
        """Void a transaction instead of physically deleting financial evidence."""
        if not (reason or "").strip():
            raise ValueError("A reason is required to void an SGA transaction.")
        old = self.db.fetch_one("SELECT * FROM Compte_SGA WHERE id_transaction = %s", (id_transaction,))
        if not old or old.get("is_void"):
            raise ValueError("The SGA transaction does not exist or has already been voided.")
        period = self.governance.assert_writable_period(old["date_transaction"], actor_username)
        success, _ = self.db.execute(
            """UPDATE Compte_SGA SET is_void=1, void_reason=%s, voided_by=%s, voided_at=NOW()
               WHERE id_transaction=%s AND is_void=0""",
            (reason.strip(), actor_username, id_transaction),
        )
        if success:
            self.governance.record_audit(
                actor_username, "SGA_TRANSACTION_VOIDED", "Compte_SGA", id_transaction, period["id_period"],
                old_values={"entrees": old.get("entrees"), "sorties": old.get("sorties"), "designation": old.get("designation")},
                reason=reason.strip(),
            )
        return success
    def get_vehicule_logs(self):
        query = "SELECT * FROM Vehicule_Service ORDER BY date_suivi DESC LIMIT 50"
        return self.db.fetch_all(query)

    def add_vehicule_log(self, date_suivi, kilometrage, montant_carburant, type_carburant, details, actor_username="system"):
        period = self.governance.assert_writable_period(date_suivi, actor_username)
        coffre_query = """
            INSERT INTO Mouvement_Coffre
            (date_transaction, type_operation, categorie_operation, montant, designation, period_id, payment_status)
            VALUES (%s, 'SORTIE', 'DEPENSE_VEHICULE', %s, %s, %s, 'PAID')
        """
        designation = f"Carburant {type_carburant} ({kilometrage} km) - {details}"
        success_coffre, coffre_id = self.db.execute(
            coffre_query, (date_suivi, montant_carburant, designation, period["id_period"])
        )
        if not success_coffre:
            return False
        success, entity_id = self.db.execute(
            """INSERT INTO Vehicule_Service
               (date_suivi, kilometrage, montant_carburant, type_carburant, details, id_transaction_coffre, period_id)
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (date_suivi, kilometrage, montant_carburant, type_carburant, details, coffre_id, period["id_period"]),
        )
        if success:
            self.governance.record_audit(
                actor_username, "VEHICLE_LOG_CREATED", "Vehicule_Service", entity_id, period["id_period"],
                new_values={"kilometrage": kilometrage, "montant_carburant": montant_carburant, "type_carburant": type_carburant},
                reason=details,
            )
        return success
    def get_encaissements(self):
        query = "SELECT * FROM Etat_Encaissement ORDER BY date_encaissement DESC LIMIT 50"
        return self.db.fetch_all(query)

    def add_encaissement(self, date_encaissement, designation, montant, observations, actor_username="system"):
        period = self.governance.assert_writable_period(date_encaissement, actor_username)
        success, entity_id = self.db.execute(
            """INSERT INTO Etat_Encaissement
               (date_encaissement, designation, montant, observations, period_id)
               VALUES (%s, %s, %s, %s, %s)""",
            (date_encaissement, designation, montant, observations, period["id_period"]),
        )
        if success:
            self.governance.record_audit(
                actor_username, "COLLECTION_CREATED", "Etat_Encaissement", entity_id, period["id_period"],
                new_values={"montant": montant, "designation": designation}, reason=observations,
            )
        return success
    # --- Station d'Incinération Benniou ---
    def get_incinerations(self, month=None, year=None):
        query = "SELECT * FROM Station_Incineration"
        params = []
        where_clauses = []
        if month and month > 0:
            where_clauses.append("MONTH(date_suivi) = %s")
            params.append(month)
        if year and year > 0:
            where_clauses.append("YEAR(date_suivi) = %s")
            params.append(year)
        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)
        query += " ORDER BY date_suivi ASC, id_incineration ASC"
        return self.db.fetch_all(query, tuple(params))

    def add_incineration(self, date_suivi, date_remise, poids_kg, prix_unitaire_kg, montant_total, etat_paiement, observations):
        query = """
            INSERT INTO Station_Incineration (date_suivi, date_remise, poids_kg, prix_unitaire_kg, montant_total, etat_paiement, observations)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        params = (date_suivi, date_remise, poids_kg, prix_unitaire_kg, montant_total, etat_paiement, observations)
        success, _ = self.db.execute(query, params)
        return success

    def update_incineration(self, id_incineration, date_suivi, date_remise, poids_kg, prix_unitaire_kg, montant_total, etat_paiement, observations):
        query = """
            UPDATE Station_Incineration 
            SET date_suivi=%s, date_remise=%s, poids_kg=%s, prix_unitaire_kg=%s, montant_total=%s, etat_paiement=%s, observations=%s
            WHERE id_incineration=%s
        """
        params = (date_suivi, date_remise, poids_kg, prix_unitaire_kg, montant_total, etat_paiement, observations, id_incineration)
        success, _ = self.db.execute(query, params)
        return success

    def delete_incineration(self, id_incineration):
        query = "DELETE FROM Station_Incineration WHERE id_incineration=%s"
        success, _ = self.db.execute(query, (id_incineration,))
        return success

    def get_incineration_stats(self, month=None, year=None):
        query = """
            SELECT 
                IFNULL(SUM(poids_kg), 0) AS total_poids_kg,
                IFNULL(SUM(montant_total), 0) AS total_montant,
                IFNULL(SUM(CASE WHEN etat_paiement = 'NON_PAYE' THEN montant_total ELSE 0 END), 0) AS total_non_paye,
                IFNULL(MAX(poids_kg), 0) AS max_poids_kg,
                IFNULL(MIN(poids_kg), 0) AS min_poids_kg,
                IFNULL(AVG(poids_kg), 0) AS moyenne_poids_kg
            FROM Station_Incineration
        """
        params = []
        where_clauses = []
        if month and month > 0:
            where_clauses.append("MONTH(date_suivi) = %s")
            params.append(month)
        if year and year > 0:
            where_clauses.append("YEAR(date_suivi) = %s")
            params.append(year)
        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)
        res = self.db.fetch_one(query, tuple(params))
        return res or {
            "total_poids_kg": 0.0, "total_montant": 0.0, "total_non_paye": 0.0,
            "max_poids_kg": 0.0, "min_poids_kg": 0.0, "moyenne_poids_kg": 0.0
        }

    # --- Rapport Analytique des Achats ---
    def get_analytique_achats(self, month, year):
        categories = {}
        
        # 1. Salaires
        paie_q = "SELECT IFNULL(SUM(net_a_payer), 0) as total FROM Fiches_Paie WHERE mois=%s AND annee=%s"
        res_paie = self.db.fetch_one(paie_q, (month, year))
        if res_paie and float(res_paie['total']) > 0:
            categories["Salaires"] = float(res_paie['total'])

        # 2. Véhicule de Service
        veh_q = "SELECT IFNULL(SUM(montant_carburant), 0) as total FROM Vehicule_Service WHERE MONTH(date_suivi)=%s AND YEAR(date_suivi)=%s"
        res_veh = self.db.fetch_one(veh_q, (month, year))
        if res_veh and float(res_veh['total']) > 0:
            categories["Véhicule de Service"] = float(res_veh['total'])

        # 3. Sous-traitances
        st_q = "SELECT IFNULL(SUM(montant_total), 0) as total FROM Operations_Partenaires WHERE MONTH(date_operation)=%s AND YEAR(date_operation)=%s"
        res_st = self.db.fetch_one(st_q, (month, year))
        if res_st and float(res_st['total']) > 0:
            categories["Sous-traitances"] = float(res_st['total'])

        # 4. Expenses by category from Depenses_Achats
        cat_q = """
            SELECT IFNULL(c.nom_categorie, 'Réactifs & Consommables') as nom_cat, IFNULL(SUM(d.montant_total), 0) as total
            FROM Depenses_Achats d
            LEFT JOIN Categories_Depenses c ON d.id_categorie = c.id_categorie
            WHERE MONTH(d.date_facture)=%s AND YEAR(d.date_facture)=%s
            GROUP BY c.nom_categorie
        """
        cat_rows = self.db.fetch_all(cat_q, (month, year))
        for r in cat_rows:
            if float(r['total']) > 0:
                categories[r['nom_cat']] = categories.get(r['nom_cat'], 0.0) + float(r['total'])

        # 5. Dépenses Internes from Details_Depenses_Caisse
        int_q = "SELECT IFNULL(SUM(montant), 0) as total FROM Details_Depenses_Caisse WHERE MONTH(date_mouvement)=%s AND YEAR(date_mouvement)=%s"
        res_int = self.db.fetch_one(int_q, (month, year))
        if res_int and float(res_int['total']) > 0:
            categories["Dépenses Internes"] = float(res_int['total'])

        total_achats = sum(categories.values())
        
        breakdown = []
        for cat_name, val in categories.items():
            pct = (val / total_achats * 100.0) if total_achats > 0 else 0.0
            breakdown.append({
                "categorie": cat_name,
                "montant": val,
                "pourcentage": pct
            })

        return {
            "total_achats": total_achats,
            "categories": breakdown
        }

