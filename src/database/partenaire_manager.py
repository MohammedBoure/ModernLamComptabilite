class PartenaireManager:
    def __init__(self, db_instance):
        self.db = db_instance

    def get_partenaires(self):
        query = "SELECT * FROM Partenaires"
        return self.db.fetch_all(query)

    def add_partenaire(self, data_dict_or_name, type_partenaire=None, solde_initial=None):
        if isinstance(data_dict_or_name, dict):
            data = data_dict_or_name
            cols = ", ".join(data.keys())
            placeholders = ", ".join(["%s"] * len(data))
            query = f"INSERT INTO Partenaires ({cols}) VALUES ({placeholders})"
            success, _ = self.db.execute(query, tuple(data.values()))
            return success
        else:
            query = "INSERT INTO Partenaires (nom_partenaire, type_partenaire, solde_initial) VALUES (%s, %s, %s)"
            params = (data_dict_or_name, type_partenaire, solde_initial)
            success, _ = self.db.execute(query, params)
            return success

    def get_operations(self, month=None, year=None):
        query = """
            SELECT o.id_operation, o.date_operation, p.nom_partenaire, o.type_document, o.montant_total, o.date_reception, o.etat_paiement, o.observation
            FROM Operations_Partenaires o
            JOIN Partenaires p ON o.id_partenaire = p.id_partenaire
        """
        params = []
        if month and year:
            query += " WHERE MONTH(o.date_operation) = %s AND YEAR(o.date_operation) = %s"
            params.extend([month, year])
        query += " ORDER BY o.date_operation DESC"
        if not (month and year):
            query += " LIMIT 50"
        return self.db.fetch_all(query, tuple(params) if params else None)

    def get_operations_list(self):
        query = """
            SELECT o.id_operation, p.nom_partenaire, o.date_operation, o.montant_total 
            FROM Operations_Partenaires o
            JOIN Partenaires p ON o.id_partenaire = p.id_partenaire
            ORDER BY o.date_operation DESC
        """
        return self.db.fetch_all(query)

    def add_operation(self, id_partenaire, type_document, date_operation, date_reception, montant_total, etat_paiement, observation):
        query = """
            INSERT INTO Operations_Partenaires (id_partenaire, type_document, date_operation, date_reception, montant_total, etat_paiement, observation)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        params = (id_partenaire, type_document, date_operation, date_reception, montant_total, etat_paiement, observation)
        success, _ = self.db.execute(query, params)
        return success

    def add_paiement(self, id_operation, date_paiement, montant_verse, mode_paiement, reference_paiement, observations):
        query = """
            INSERT INTO Paiements_Partenaires (id_operation, date_paiement, montant_verse, mode_paiement, reference_paiement, observations)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (id_operation, date_paiement, montant_verse, mode_paiement, reference_paiement, observations)
        success, _ = self.db.execute(query, params)
        return success

    def get_partenaires_state(self, type_partenaire, month, year):
        type_filter = ""
        type_params = []
        if type_partenaire and type_partenaire != "TOUS":
            type_filter = "WHERE p.type_partenaire = %s"
            type_params.append(type_partenaire)
            
        if month and year:
            query = f"""
                SELECT 
                    p.id_partenaire,
                    p.nom_partenaire,
                    p.type_partenaire,
                    
                    -- MONTANT (operations in this month)
                    IFNULL((SELECT SUM(o.montant_total) FROM Operations_Partenaires o WHERE o.id_partenaire = p.id_partenaire AND MONTH(o.date_operation) = %s AND YEAR(o.date_operation) = %s), 0) AS montant,
                    
                    -- VERSEMENT (payments in this month)
                    IFNULL((SELECT SUM(pm.montant_verse) FROM Paiements_Partenaires pm JOIN Operations_Partenaires o ON pm.id_operation = o.id_operation WHERE o.id_partenaire = p.id_partenaire AND MONTH(pm.date_paiement) = %s AND YEAR(pm.date_paiement) = %s), 0) AS versement,
                    
                    -- DATE DE RECEPTION (latest reception date in this month)
                    (SELECT MAX(o.date_reception) FROM Operations_Partenaires o WHERE o.id_partenaire = p.id_partenaire AND MONTH(o.date_operation) = %s AND YEAR(o.date_operation) = %s) AS date_reception,
                    
                    -- MODE PAIEMENT (latest payment mode in this month)
                    (SELECT pm.mode_paiement FROM Paiements_Partenaires pm JOIN Operations_Partenaires o ON pm.id_operation = o.id_operation WHERE o.id_partenaire = p.id_partenaire AND MONTH(pm.date_paiement) = %s AND YEAR(pm.date_paiement) = %s ORDER BY pm.date_paiement DESC, pm.id_paiement DESC LIMIT 1) AS mode_paiement,
                    
                    -- RESTE MOIS PRECEDANTS
                    -- solde_initial + operations_before - payments_before
                    p.solde_initial + 
                    IFNULL((SELECT SUM(o.montant_total) FROM Operations_Partenaires o WHERE o.id_partenaire = p.id_partenaire AND (YEAR(o.date_operation) < %s OR (YEAR(o.date_operation) = %s AND MONTH(o.date_operation) < %s))), 0) -
                    IFNULL((SELECT SUM(pm.montant_verse) FROM Paiements_Partenaires pm JOIN Operations_Partenaires o ON pm.id_operation = o.id_operation WHERE o.id_partenaire = p.id_partenaire AND (YEAR(pm.date_paiement) < %s OR (YEAR(pm.date_paiement) = %s AND MONTH(pm.date_paiement) < %s))), 0) AS reste_mois_precedants,
                    
                    -- REMARQUES (concatenated observations in this month)
                    (SELECT GROUP_CONCAT(o.observation SEPARATOR '; ') FROM Operations_Partenaires o WHERE o.id_partenaire = p.id_partenaire AND MONTH(o.date_operation) = %s AND YEAR(o.date_operation) = %s) AS remarques
                FROM Partenaires p
                {type_filter}
            """
            params = [
                month, year,
                month, year,
                month, year,
                month, year,
                year, year, month,
                year, year, month,
                month, year
            ]
            params.extend(type_params)
        else:
            query = f"""
                SELECT 
                    p.id_partenaire,
                    p.nom_partenaire,
                    p.type_partenaire,
                    
                    -- MONTANT (all operations)
                    IFNULL((SELECT SUM(o.montant_total) FROM Operations_Partenaires o WHERE o.id_partenaire = p.id_partenaire), 0) AS montant,
                    
                    -- VERSEMENT (all payments)
                    IFNULL((SELECT SUM(pm.montant_verse) FROM Paiements_Partenaires pm JOIN Operations_Partenaires o ON pm.id_operation = o.id_operation WHERE o.id_partenaire = p.id_partenaire), 0) AS versement,
                    
                    -- DATE DE RECEPTION (latest reception date)
                    (SELECT MAX(o.date_reception) FROM Operations_Partenaires o WHERE o.id_partenaire = p.id_partenaire) AS date_reception,
                    
                    -- MODE PAIEMENT (latest payment mode)
                    (SELECT pm.mode_paiement FROM Paiements_Partenaires pm JOIN Operations_Partenaires o ON pm.id_operation = o.id_operation WHERE o.id_partenaire = p.id_partenaire ORDER BY pm.date_paiement DESC, pm.id_paiement DESC LIMIT 1) AS mode_paiement,
                    
                    -- RESTE MOIS PRECEDANTS
                    p.solde_initial AS reste_mois_precedants,
                    
                    -- REMARQUES
                    (SELECT GROUP_CONCAT(o.observation SEPARATOR '; ') FROM Operations_Partenaires o WHERE o.id_partenaire = p.id_partenaire) AS remarques
                FROM Partenaires p
                {type_filter}
            """
            params = type_params
            
        data = self.db.fetch_all(query, tuple(params) if params else None)
        for row in data:
            row['montant'] = float(row['montant'] or 0.0)
            row['versement'] = float(row['versement'] or 0.0)
            row['reste'] = row['montant'] - row['versement']
            row['reste_mois_precedants'] = float(row['reste_mois_precedants'] or 0.0)
            row['reste_total'] = row['reste'] + row['reste_mois_precedants']
        return data

    def get_partner_ledger(self, id_partenaire, month=None, year=None):
        query = """
            SELECT 
                o.id_operation,
                o.date_operation,
                o.type_document,
                o.montant_total,
                o.date_reception,
                o.etat_paiement,
                o.observation,
                IFNULL((SELECT SUM(montant_verse) FROM Paiements_Partenaires WHERE id_operation = o.id_operation), 0) AS total_verse,
                (SELECT GROUP_CONCAT(date_paiement ORDER BY date_paiement) FROM Paiements_Partenaires WHERE id_operation = o.id_operation) AS dates_paiement
            FROM Operations_Partenaires o
            WHERE o.id_partenaire = %s
        """
        params = [id_partenaire]
        if month and year:
            query += " AND MONTH(o.date_operation) = %s AND YEAR(o.date_operation) = %s"
            params.extend([month, year])
        query += " ORDER BY o.date_operation ASC"
        
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

    def get_partner_info(self, id_partenaire):
        query = "SELECT * FROM Partenaires WHERE id_partenaire = %s"
        return self.db.fetch_one(query, (id_partenaire,))

    def get_operations_list_by_partner(self, id_partenaire):
        query = """
            SELECT o.id_operation, p.nom_partenaire, o.date_operation, o.montant_total 
            FROM Operations_Partenaires o
            JOIN Partenaires p ON o.id_partenaire = p.id_partenaire
            WHERE o.id_partenaire = %s
            ORDER BY o.date_operation DESC
        """
        return self.db.fetch_all(query, (id_partenaire,))
