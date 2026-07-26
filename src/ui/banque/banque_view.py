from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTabWidget
from PySide6.QtGui import QFont

from .tabs.compte_sga_tab import CompteSGATab
from .tabs.vehicule_tab import VehiculeServiceTab
from .tabs.encaissement_tab import EtatEncaissementTab
from .tabs.incineration_tab import StationIncinerationTab

class BanqueView(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 20)
        

        
        self.tabs = QTabWidget()
        
        self.tab_banque = CompteSGATab(self)
        self.tabs.addTab(self.tab_banque, "Compte SGA (Banque)")
        
        self.tab_vehicule = VehiculeServiceTab(self)
        self.tabs.addTab(self.tab_vehicule, "Véhicule de Service")
        
        self.tab_encaissement = EtatEncaissementTab(self)
        self.tabs.addTab(self.tab_encaissement, "État d'Encaissement")
        
        self.tab_incineration = StationIncinerationTab(self)
        self.tabs.addTab(self.tab_incineration, "Station Incinération Benniou")
        
        layout.addWidget(self.tabs)
