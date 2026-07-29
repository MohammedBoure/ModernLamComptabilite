from .base.database import Database
from .caisse_manager import CaisseManager
from .hr_manager import HRManager
from .fournisseur_manager import FournisseurManager
from .partenaire_manager import PartenaireManager
from .banque_manager import BanqueManager
from .dashboard_manager import DashboardManager
from .rapport_manager import RapportManager
from .governance_manager import GovernanceManager
from .profitability_manager import ProfitabilityManager

class ComptabiliteDataManager:
    def __init__(self, db_instance):
        self.db = db_instance
        self.caisse = CaisseManager(db_instance)
        self.hr = HRManager(db_instance)
        self.fournisseurs = FournisseurManager(db_instance)
        self.partenaires = PartenaireManager(db_instance)
        self.banque = BanqueManager(db_instance)
        self.dashboard = DashboardManager(db_instance)
        self.rapports = RapportManager(db_instance)
        self.governance = GovernanceManager(db_instance)
        self.profitability = ProfitabilityManager(db_instance)

# Initialize the new robust database with connection pooling and schema init
db = Database()

# Global data manager instance exposed to UI classes
data_manager = ComptabiliteDataManager(db)

