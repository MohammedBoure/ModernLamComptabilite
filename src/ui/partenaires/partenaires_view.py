from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTabWidget, QComboBox
from PySide6.QtGui import QFont
from PySide6.QtCore import QDate, Qt

from .tabs.sous_traitants_tab import SousTraitantsTab
from .tabs.operations_tab import OperationsPartenairesTab

class PartenairesView(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.on_filter_changed()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 20)
        layout.setSpacing(10)
        
        self.tabs = QTabWidget()
        
        # Corner widget for filters
        self.filter_widget = QWidget()
        filter_layout = QHBoxLayout(self.filter_widget)
        filter_layout.setContentsMargins(0, 0, 10, 0)
        filter_layout.setSpacing(5)
        
        lbl_month = QLabel("Mois:")
        self.cb_month = QComboBox()
        self.cb_month.addItems(["Tous", "Janvier", "Février", "Mars", "Avril", "Mai", "Juin", 
                               "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"])
        
        lbl_year = QLabel("Année:")
        self.cb_year = QComboBox()
        current_year = QDate.currentDate().year()
        self.cb_year.addItems(["Tous"] + [str(y) for y in range(current_year - 2, current_year + 5)])
        
        # Set defaults to current month/year
        self.cb_month.setCurrentIndex(QDate.currentDate().month())
        self.cb_year.setCurrentText(str(current_year))
        
        self.cb_month.currentIndexChanged.connect(self.on_filter_changed)
        self.cb_year.currentTextChanged.connect(self.on_filter_changed)
        
        filter_layout.addWidget(lbl_month)
        filter_layout.addWidget(self.cb_month)
        filter_layout.addWidget(lbl_year)
        filter_layout.addWidget(self.cb_year)
        
        self.tabs.setCornerWidget(self.filter_widget, Qt.TopRightCorner)
        
        self.tab_sous_traitants = SousTraitantsTab(self)
        self.tabs.addTab(self.tab_sous_traitants, "Sous-Traitants & Conventions")
        
        self.tab_operations = OperationsPartenairesTab(self)
        self.tabs.addTab(self.tab_operations, "Opérations")
        
        layout.addWidget(self.tabs)

    def on_filter_changed(self):
        month = self.cb_month.currentIndex()
        year = self.cb_year.currentText()
        
        filter_month = None if month == 0 else month
        filter_year = None if year == "Tous" else int(year)
        
        self.tab_sous_traitants.load_data(filter_month, filter_year)
        self.tab_operations.load_data(filter_month, filter_year)
