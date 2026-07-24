from PySide6.QtWidgets import QWidget, QVBoxLayout
from .tabs.etat_tab import EtatFournisseursTab

class FournisseursView(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.on_filter_changed()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 15)
        layout.setSpacing(0)
        
        self.tab_fournisseurs = EtatFournisseursTab(self)
        layout.addWidget(self.tab_fournisseurs)

    @property
    def cb_month(self):
        return self.tab_fournisseurs.cb_month

    @property
    def cb_year(self):
        return self.tab_fournisseurs.cb_year

    def on_filter_changed(self):
        if hasattr(self, 'tab_fournisseurs') and hasattr(self.tab_fournisseurs, 'on_filter_changed'):
            self.tab_fournisseurs.on_filter_changed()

    def load_data(self):
        self.on_filter_changed()
