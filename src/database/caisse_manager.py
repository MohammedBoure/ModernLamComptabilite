class CaisseManager:
    def __init__(self, db_instance):
        self.db = db_instance

    def get_caisse_movements(self, month=None, year=None):
        query = "SELECT * FROM Mouvement_Caisse"
        params = []
        if month and year:
            query += " WHERE MONTH(date_mouvement) = %s AND YEAR(date_mouvement) = %s"
            params.extend([month, year])
        query += " ORDER BY date_mouvement DESC"
        return self.db.fetch_all(query, tuple(params) if params else None)

    def add_caisse_movement(self, date_mouvement, caisse_cv, caisse_c, tpe, depenses, remboursement, convention, sous_traitants):
        query = """
            INSERT INTO Mouvement_Caisse 
            (date_mouvement, caisse_cv, caisse_c, tpe, depenses, remboursement, convention, sous_traitants)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
            caisse_cv=VALUES(caisse_cv), caisse_c=VALUES(caisse_c), tpe=VALUES(tpe), 
            depenses=VALUES(depenses), remboursement=VALUES(remboursement), 
            convention=VALUES(convention), sous_traitants=VALUES(sous_traitants)
        """
        params = (date_mouvement, caisse_cv, caisse_c, tpe, depenses, remboursement, convention, sous_traitants)
        success, _ = self.db.execute(query, params)
        return success

    def get_clotures(self, month=None, year=None):
        query = "SELECT * FROM Cloture_Caisse"
        params = []
        if month and year:
            query += " WHERE MONTH(date_cloture) = %s AND YEAR(date_cloture) = %s"
            params.extend([month, year])
        query += " ORDER BY date_cloture DESC"
        return self.db.fetch_all(query, tuple(params) if params else None)

    def add_cloture(self, date_cloture, utilisateur, montant_reel, montant_virtuel, remarques):
        # Ensure a Mouvement_Caisse exists for that date to prevent foreign key issues
        self.db.execute("INSERT IGNORE INTO Mouvement_Caisse (date_mouvement) VALUES (%s)", (date_cloture,))
        
        query = """
            INSERT INTO Cloture_Caisse (date_cloture, utilisateur, montant_reel, montant_virtuel, remarques)
            VALUES (%s, %s, %s, %s, %s)
        """
        params = (date_cloture, utilisateur, montant_reel, montant_virtuel, remarques)
        success, _ = self.db.execute(query, params)
        return success

    def get_depenses_caisse(self, month=None, year=None):
        query = "SELECT * FROM Details_Depenses_Caisse"
        params = []
        if month and year:
            query += " WHERE MONTH(date_mouvement) = %s AND YEAR(date_mouvement) = %s"
            params.extend([month, year])
        query += " ORDER BY date_mouvement DESC"
        return self.db.fetch_all(query, tuple(params) if params else None)

    def add_depense_caisse(self, date_mouvement, designation, montant):
        self.db.execute("INSERT IGNORE INTO Mouvement_Caisse (date_mouvement) VALUES (%s)", (date_mouvement,))
        query = "INSERT INTO Details_Depenses_Caisse (date_mouvement, designation, montant) VALUES (%s, %s, %s)"
        params = (date_mouvement, designation, montant)
        success, _ = self.db.execute(query, params)
        return success

    def get_etat_differences(self, month=None, year=None):
        query = """
            SELECT utilisateur, SUM(montant_reel - montant_virtuel) as montant_total 
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

    def get_coffre_summary(self, month=None, year=None):
        query = """
            SELECT 
                SUM(CASE WHEN type_operation = 'ENTREE' AND categorie_operation = 'CA_LAM' THEN montant ELSE 0 END) as ca_lam,
                SUM(CASE WHEN type_operation = 'ENTREE' AND categorie_operation = 'CA_CONVENTION' THEN montant ELSE 0 END) as ca_convention,
                SUM(CASE WHEN type_operation = 'ENTREE' AND categorie_operation = 'CA_ST' THEN montant ELSE 0 END) as ca_st,
                SUM(CASE WHEN type_operation = 'ENTREE' AND categorie_operation = 'ENTREES_SUPP' THEN montant ELSE 0 END) as ca_supp,
                SUM(CASE WHEN type_operation = 'SORTIE' THEN montant ELSE 0 END) as total_sorties
            FROM Mouvement_Coffre
        """
        params = []
        if month and year:
            query += " WHERE MONTH(date_transaction) = %s AND YEAR(date_transaction) = %s"
            params.extend([month, year])
            
        result = self.db.fetch_all(query, tuple(params) if params else None)
        if result and len(result) > 0:
            row = result[0]
            ca_lam = float(row.get('ca_lam') or 0)
            ca_conv = float(row.get('ca_convention') or 0)
            ca_st = float(row.get('ca_st') or 0)
            ca_supp = float(row.get('ca_supp') or 0)
            global_ca = ca_lam + ca_conv + ca_st + ca_supp
            total_sorties = float(row.get('total_sorties') or 0)
            coffre_net = global_ca - total_sorties
            
            return {
                'ca_lam': ca_lam,
                'ca_convention': ca_conv,
                'ca_st': ca_st,
                'ca_supp': ca_supp,
                'global': global_ca,
                'total_sorties': total_sorties,
                'coffre_net': coffre_net
            }
        return {
            'ca_lam': 0, 'ca_convention': 0, 'ca_st': 0, 'ca_supp': 0,
            'global': 0, 'total_sorties': 0, 'coffre_net': 0
        }

    def add_coffre_movement(self, date_transaction, type_operation, categorie_operation, montant, designation):
        query = """
            INSERT INTO Mouvement_Coffre (date_transaction, type_operation, categorie_operation, montant, designation)
            VALUES (%s, %s, %s, %s, %s)
        """
        params = (date_transaction, type_operation, categorie_operation, montant, designation)
        success, _ = self.db.execute(query, params)
        return success
