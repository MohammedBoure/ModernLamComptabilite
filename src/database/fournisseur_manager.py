class FournisseurManager:
    def __init__(self, db_instance):
        self.db = db_instance

    def get_fournisseurs_state(self, category_name=None, month=None, year=None):
        cat_filter_purchase = ""
        cat_filter_payment = ""
        params = []
        
        if category_name:
            cat_filter_purchase = "AND d.id_categorie = (SELECT id_categorie FROM Categories_Depenses WHERE nom_categorie = %s)"
            cat_filter_payment = "AND d2.id_categorie = (SELECT id_categorie FROM Categories_Depenses WHERE nom_categorie = %s)"

        if month and year:
            query = f"""
                SELECT 
                    f.id_fournisseur,
                    f.nom_fournisseur,
                    IFNULL((
                        SELECT SUM(d.montant_total) 
                        FROM Depenses_Achats d 
                        WHERE d.id_fournisseur = f.id_fournisseur 
                          AND MONTH(d.date_facture) = %s 
                          AND YEAR(d.date_facture) = %s
                          {cat_filter_purchase}
                    ), 0) AS total_commandes,
                    IFNULL((
                        SELECT SUM(p.montant_verse) 
                        FROM Paiements_Fournisseurs p 
                        JOIN Depenses_Achats d2 ON p.id_depense = d2.id_depense 
                        WHERE d2.id_fournisseur = f.id_fournisseur 
                          AND MONTH(p.date_paiement) = %s 
                          AND YEAR(p.date_paiement) = %s
                          {cat_filter_payment}
                    ), 0) AS total_paye
                FROM Fournisseurs f
                WHERE f.inclus_etat = 1
            """
            if category_name:
                params = [month, year, category_name, month, year, category_name]
            else:
                params = [month, year, month, year]
        else:
            query = f"""
                SELECT 
                    f.id_fournisseur,
                    f.nom_fournisseur,
                    IFNULL((
                        SELECT SUM(d.montant_total) 
                        FROM Depenses_Achats d 
                        WHERE d.id_fournisseur = f.id_fournisseur
                          {cat_filter_purchase}
                    ), 0) + f.solde_initial AS total_commandes,
                    IFNULL((
                        SELECT SUM(p.montant_verse) 
                        FROM Paiements_Fournisseurs p 
                        JOIN Depenses_Achats d2 ON p.id_depense = d2.id_depense 
                        WHERE d2.id_fournisseur = f.id_fournisseur
                          {cat_filter_payment}
                    ), 0) AS total_paye
                FROM Fournisseurs f
                WHERE f.inclus_etat = 1
            """
            if category_name:
                params = [category_name, category_name]
            else:
                params = []

        data = self.db.fetch_all(query, tuple(params) if params else None)
        for row in data:
            row['reste_a_payer'] = float(row['total_commandes'] or 0.0) - float(row['total_paye'] or 0.0)
        return data

    def get_supplier_ledger(self, id_fournisseur, category_name, month=None, year=None):
        cat_id = self.ensure_category_exists(category_name)
        
        query = """
            SELECT 
                d.id_depense,
                d.date_facture,
                d.type_document,
                d.montant_total,
                d.observation,
                IFNULL((SELECT SUM(montant_verse) FROM Paiements_Fournisseurs WHERE id_depense = d.id_depense), 0) AS total_verse,
                (SELECT GROUP_CONCAT(date_paiement ORDER BY date_paiement) FROM Paiements_Fournisseurs WHERE id_depense = d.id_depense) AS dates_paiement
            FROM Depenses_Achats d
            WHERE d.id_fournisseur = %s AND d.id_categorie = %s
        """
        params = [id_fournisseur, cat_id]
        if month and year:
            query += " AND MONTH(d.date_facture) = %s AND YEAR(d.date_facture) = %s"
            params.extend([month, year])
        query += " ORDER BY d.date_facture ASC"
        
        data = self.db.fetch_all(query, tuple(params))
        for row in data:
            row['montant_total'] = float(row['montant_total'])
            row['total_verse'] = float(row['total_verse'])
            row['reste'] = row['montant_total'] - row['total_verse']
            if row['total_verse'] == 0:
                row['statut'] = "Non Payé"
            elif row['reste'] <= 0:
                row['statut'] = "Payé"
            else:
                row['statut'] = "Partiel"
                
            if row['dates_paiement']:
                first_pay_date = row['dates_paiement'].split(',')[0]
                row['mois_paiement'] = first_pay_date
            else:
                row['mois_paiement'] = "-"
        return data

    def get_supplier_info(self, id_fournisseur):
        query = "SELECT * FROM Fournisseurs WHERE id_fournisseur = %s"
        return self.db.fetch_one(query, (id_fournisseur,))

    def get_depenses_list_by_supplier(self, id_fournisseur, month=None, year=None):
        query = """
            SELECT 
                d.id_depense, 
                f.nom_fournisseur, 
                d.type_document,
                d.date_facture, 
                d.montant_total,
                IFNULL((SELECT SUM(montant_verse) FROM Paiements_Fournisseurs WHERE id_depense = d.id_depense), 0) AS total_verse
            FROM Depenses_Achats d 
            JOIN Fournisseurs f ON d.id_fournisseur = f.id_fournisseur
            WHERE d.id_fournisseur = %s
        """
        params = [id_fournisseur]
        if month and year:
            query += " AND MONTH(d.date_facture) = %s AND YEAR(d.date_facture) = %s"
            params.extend([month, year])
        query += " ORDER BY d.date_facture DESC"
        data = self.db.fetch_all(query, tuple(params))
        for row in data:
            row['montant_total'] = float(row['montant_total'] or 0.0)
            row['total_verse'] = float(row['total_verse'] or 0.0)
            row['reste'] = max(0.0, row['montant_total'] - row['total_verse'])
        return data

    def get_fournisseurs_list(self):
        query = "SELECT id_fournisseur, nom_fournisseur FROM Fournisseurs ORDER BY nom_fournisseur"
        return self.db.fetch_all(query)

    def add_fournisseur(self, data_dict_or_name, solde_initial=None):
        if isinstance(data_dict_or_name, dict):
            data = data_dict_or_name
            cols = ", ".join(data.keys())
            placeholders = ", ".join(["%s"] * len(data))
            query = f"INSERT INTO Fournisseurs ({cols}) VALUES ({placeholders})"
            success, _ = self.db.execute(query, tuple(data.values()))
            return success
        else:
            query = "INSERT INTO Fournisseurs (nom_fournisseur, solde_initial) VALUES (%s, %s)"
            success, _ = self.db.execute(query, (data_dict_or_name, solde_initial))
            return success

    def get_achats(self, month=None, year=None):
        query = """
            SELECT d.id_depense, d.date_facture, f.nom_fournisseur, d.type_document, d.montant_total, d.mode_paiement, d.observation
            FROM Depenses_Achats d
            JOIN Fournisseurs f ON d.id_fournisseur = f.id_fournisseur
        """
        params = []
        if month and year:
            query += " WHERE MONTH(d.date_facture) = %s AND YEAR(d.date_facture) = %s"
            params.extend([month, year])
        query += " ORDER BY d.date_facture DESC"
        if not (month and year):
            query += " LIMIT 50"
        return self.db.fetch_all(query, tuple(params) if params else None)

    def get_depenses_list(self, month=None, year=None):
        query = """
            SELECT 
                d.id_depense, 
                f.nom_fournisseur, 
                d.type_document,
                d.date_facture, 
                d.montant_total,
                IFNULL((SELECT SUM(montant_verse) FROM Paiements_Fournisseurs WHERE id_depense = d.id_depense), 0) AS total_verse
            FROM Depenses_Achats d 
            JOIN Fournisseurs f ON d.id_fournisseur = f.id_fournisseur
        """
        params = []
        if month and year:
            query += " WHERE MONTH(d.date_facture) = %s AND YEAR(d.date_facture) = %s"
            params.extend([month, year])
        query += " ORDER BY d.date_facture DESC"
        data = self.db.fetch_all(query, tuple(params) if params else None)
        for row in data:
            row['montant_total'] = float(row['montant_total'] or 0.0)
            row['total_verse'] = float(row['total_verse'] or 0.0)
            row['reste'] = max(0.0, row['montant_total'] - row['total_verse'])
        return data

    def add_depense(self, id_fournisseur, id_categorie, type_document, date_facture, montant_total, mode_paiement, observation):
        query = """
            INSERT INTO Depenses_Achats (id_fournisseur, id_categorie, type_document, date_facture, montant_total, mode_paiement, observation)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        params = (id_fournisseur, id_categorie, type_document, date_facture, montant_total, mode_paiement, observation)
        success, _ = self.db.execute(query, params)
        return success

    def add_paiement(self, id_depense, date_paiement, montant_verse, mode_paiement, reference_paiement, observations):
        query = """
            INSERT INTO Paiements_Fournisseurs (id_depense, date_paiement, montant_verse, mode_paiement, reference_paiement, observations)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (id_depense, date_paiement, montant_verse, mode_paiement, reference_paiement, observations)
        success, _ = self.db.execute(query, params)
        return success

    def ensure_category_exists(self, cat_name):
        self.db.execute("INSERT IGNORE INTO Categories_Depenses (nom_categorie) VALUES (%s)", (cat_name,))
        row = self.db.fetch_one("SELECT id_categorie FROM Categories_Depenses WHERE nom_categorie = %s", (cat_name,))
        return row['id_categorie'] if row else None

    def get_profitability_summary(self, month, year):
        """Calculate the exact financial and profitability figures as in the Excel sheet."""
        # 1. Fournisseurs Total (Total des commandes)
        q_fourn = """
            SELECT SUM(montant_total) as total_cmd 
            FROM Depenses_Achats 
            WHERE MONTH(date_facture) = %s AND YEAR(date_facture) = %s
        """
        r_fourn = self.db.fetch_one(q_fourn, (month, year))
        total_cmd = float(r_fourn['total_cmd'] or 0.0) if r_fourn else 0.0

        # 2. Paie Estimation (Salaries total)
        q_paie = "SELECT SUM(net_a_payer) as total_paie FROM Fiches_Paie WHERE mois = %s AND annee = %s"
        r_paie = self.db.fetch_one(q_paie, (month, year))
        total_paie = float(r_paie['total_paie'] or 0.0) if r_paie else 0.0

        # 3. Dépenses Interne
        q_dep_int = """
            SELECT SUM(depenses) as total_dep_int 
            FROM Mouvement_Caisse 
            WHERE MONTH(date_mouvement) = %s AND YEAR(date_mouvement) = %s
        """
        r_dep_int = self.db.fetch_one(q_dep_int, (month, year))
        total_dep_int = float(r_dep_int['total_dep_int'] or 0.0) if r_dep_int else 0.0

        # Total Costs (Fournisseurs + Dépenses + Paie)
        total_costs = total_cmd + total_dep_int + total_paie

        # 4. CA LAM
        q_ca_lam = """
            SELECT SUM(caisse_cv) as cv, SUM(tpe) as tpe, SUM(depenses) as dep 
            FROM Mouvement_Caisse 
            WHERE MONTH(date_mouvement) = %s AND YEAR(date_mouvement) = %s
        """
        r_ca_lam = self.db.fetch_one(q_ca_lam, (month, year))
        ca_lam = 0.0
        if r_ca_lam:
            ca_lam = float(r_ca_lam['cv'] or 0) + float(r_ca_lam['tpe'] or 0) + float(r_ca_lam['dep'] or 0)

        # 5. CA C (Caisse C + Convention Mutuelle)
        q_ca_c = """
            SELECT SUM(caisse_c) as c, SUM(convention) as conv 
            FROM Mouvement_Caisse 
            WHERE MONTH(date_mouvement) = %s AND YEAR(date_mouvement) = %s
        """
        r_ca_c = self.db.fetch_one(q_ca_c, (month, year))
        ca_c = 0.0
        if r_ca_c:
            ca_c = float(r_ca_c['c'] or 0) + float(r_ca_c['conv'] or 0)

        # 6. CA ST (Sous-Traitants)
        q_ca_st = """
            SELECT SUM(o.montant_total) as st 
            FROM Operations_Partenaires o 
            JOIN Partenaires p ON o.id_partenaire = p.id_partenaire 
            WHERE p.type_partenaire = 'SOUS_TRAITANT' 
              AND MONTH(o.date_operation) = %s 
              AND YEAR(o.date_operation) = %s
        """
        r_ca_st = self.db.fetch_one(q_ca_st, (month, year))
        ca_st = float(r_ca_st['st'] or 0.0) if r_ca_st else 0.0

        # 7. Entrées Supp
        q_ent_supp = """
            SELECT SUM(montant) as supp 
            FROM Mouvement_Coffre 
            WHERE type_operation = 'ENTREE' 
              AND categorie_operation = 'ENTREES_SUPP' 
              AND MONTH(date_transaction) = %s 
              AND YEAR(date_transaction) = %s
        """
        r_ent_supp = self.db.fetch_one(q_ent_supp, (month, year))
        entrees_supp = float(r_ent_supp['supp'] or 0.0) if r_ent_supp else 0.0

        # Chiffre d'Affaire total (CA LAM + CA C + CA ST + ENTREES SUPP)
        chiffre_affaire = ca_lam + ca_c + ca_st + entrees_supp

        # Profitability
        profitability = chiffre_affaire - total_costs

        # Profitability percentage
        profitability_pct = 0.0
        if chiffre_affaire > 0:
            profitability_pct = (profitability / chiffre_affaire) * 100.0

        return {
            'total_cmd': total_cmd,
            'total_paie': total_paie,
            'total_dep_int': total_dep_int,
            'total_costs': total_costs,
            'ca_lam': ca_lam,
            'ca_c': ca_c,
            'ca_st': ca_st,
            'entrees_supp': entrees_supp,
            'chiffre_affaire': chiffre_affaire,
            'profitability': profitability,
            'profitability_pct': profitability_pct
        }

