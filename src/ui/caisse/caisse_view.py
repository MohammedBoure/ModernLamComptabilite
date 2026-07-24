from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtGui import QFont

from .tabs.caisse_coffre_tab import CaisseCoffreTab

class CaisseView(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 20)
        
        self.tab_caisse_coffre = CaisseCoffreTab(self)
        layout.addWidget(self.tab_caisse_coffre)

    def set_permissions(self, allowed_tabs):
        if hasattr(self.tab_caisse_coffre, 'set_permissions'):
            self.tab_caisse_coffre.set_permissions(allowed_tabs)
