class DashboardManager:
    def __init__(self, db_instance):
        self.db = db_instance

    def get_monthly_profitability(self):
        query = """
            SELECT annee, mois, chiffre_affaire_total, total_depenses, total_paie, profitabilite_nette 
            FROM Vue_Profitabilite_Mensuelle
            ORDER BY annee DESC, mois DESC
            LIMIT 12
        """
        return self.db.fetch_all(query)
