class BanqueManager:
    def __init__(self, db_instance):
        self.db = db_instance

    def get_sga_transactions(self):
        # Retrieve all transactions EXCEPT the hidden 'Solde Initial' transaction
        query = "SELECT * FROM Vue_Solde_Compte_SGA WHERE designation != 'Solde Initial 2025' ORDER BY date_transaction ASC, id_transaction ASC"
        return self.db.fetch_all(query)

    def get_solde_initial(self):
        query = "SELECT entrees FROM Compte_SGA WHERE designation = 'Solde Initial 2025' AND date_transaction = '2025-12-31' LIMIT 1"
        res = self.db.fetch_one(query)
        return float(res['entrees']) if res else 0.0

    def update_solde_initial(self, montant):
        # Check if it exists
        query_check = "SELECT id_transaction FROM Compte_SGA WHERE designation = 'Solde Initial 2025' AND date_transaction = '2025-12-31'"
        res = self.db.fetch_one(query_check)
        if res:
            query = "UPDATE Compte_SGA SET entrees = %s WHERE id_transaction = %s"
            success, _ = self.db.execute(query, (montant, res['id_transaction']))
        else:
            query = "INSERT INTO Compte_SGA (date_transaction, entrees, sorties, designation) VALUES ('2025-12-31', %s, 0, 'Solde Initial 2025')"
            success, _ = self.db.execute(query, (montant,))
        return success

    def get_solde_actuel(self):
        query = "SELECT solde_actuel FROM Vue_Solde_Compte_SGA ORDER BY date_transaction DESC, id_transaction DESC LIMIT 1"
        res = self.db.fetch_one(query)
        return float(res['solde_actuel']) if res else 0.0

    def add_sga_transaction(self, date_transaction, n_cheque, beneficiaire, entrees, sorties, designation):
        query = """
            INSERT INTO Compte_SGA (date_transaction, n_cheque, beneficiaire, entrees, sorties, designation)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (date_transaction, n_cheque, beneficiaire, entrees, sorties, designation)
        success, _ = self.db.execute(query, params)
        return success

    def update_sga_transaction(self, id_transaction, date_transaction, n_cheque, beneficiaire, entrees, sorties, designation):
        query = """
            UPDATE Compte_SGA 
            SET date_transaction=%s, n_cheque=%s, beneficiaire=%s, entrees=%s, sorties=%s, designation=%s
            WHERE id_transaction=%s
        """
        params = (date_transaction, n_cheque, beneficiaire, entrees, sorties, designation, id_transaction)
        success, _ = self.db.execute(query, params)
        return success

    def delete_sga_transaction(self, id_transaction):
        query = "DELETE FROM Compte_SGA WHERE id_transaction=%s"
        success, _ = self.db.execute(query, (id_transaction,))
        return success

    def get_vehicule_logs(self):
        query = "SELECT * FROM Vehicule_Service ORDER BY date_suivi DESC LIMIT 50"
        return self.db.fetch_all(query)

    def add_vehicule_log(self, date_suivi, kilometrage, montant_carburant, type_carburant, details):
        # 1. Insert Mouvement_Coffre
        coffre_query = """
            INSERT INTO Mouvement_Coffre (date_transaction, type_operation, categorie_operation, montant, designation)
            VALUES (%s, %s, %s, %s, %s)
        """
        coffre_params = (date_suivi, 'SORTIE', 'DEPENSE_VEHICULE', montant_carburant, f"Carburant {type_carburant} ({kilometrage} km) - {details}")
        success_coffre, lastrowid = self.db.execute(coffre_query, coffre_params)

        if not success_coffre:
            return False

        # 2. Insert Vehicule_Service
        query = """
            INSERT INTO Vehicule_Service (date_suivi, kilometrage, montant_carburant, type_carburant, details, id_transaction_coffre)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (date_suivi, kilometrage, montant_carburant, type_carburant, details, lastrowid)
        success, _ = self.db.execute(query, params)
        return success

    def get_encaissements(self):
        query = "SELECT * FROM Etat_Encaissement ORDER BY date_encaissement DESC LIMIT 50"
        return self.db.fetch_all(query)

    def add_encaissement(self, date_encaissement, designation, montant, observations):
        query = """
            INSERT INTO Etat_Encaissement (date_encaissement, designation, montant, observations)
            VALUES (%s, %s, %s, %s)
        """
        params = (date_encaissement, designation, montant, observations)
        success, _ = self.db.execute(query, params)
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

