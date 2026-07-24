from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from .tabs.fournisseurs_tab import DonneesBaseFournisseursTab
from .tabs.partenaires_tab import DonneesBasePartenairesTab

class DonneesBaseView(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 20)
        
        self.tabs = QTabWidget()
        
        self.tab_fournisseurs = DonneesBaseFournisseursTab(self)
        self.tabs.addTab(self.tab_fournisseurs, "Fournisseurs")
        
        self.tab_partenaires = DonneesBasePartenairesTab(self)
        self.tabs.addTab(self.tab_partenaires, "Sous-Traitants / Conventions")
        
        layout.addWidget(self.tabs)
        
        # Load initial data
        self.tab_fournisseurs.load_data()
        self.tab_partenaires.load_data()
