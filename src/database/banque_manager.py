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
