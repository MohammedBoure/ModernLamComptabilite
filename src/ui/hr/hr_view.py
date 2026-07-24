from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTabWidget, QComboBox
from PySide6.QtGui import QFont
from PySide6.QtCore import QDate, Qt

from .tabs.employes_tab import EmployesTab
from .tabs.presences_tab import PresencesTab
from .tabs.salaires_tab import SalairesTab

class HRView(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 20)
        
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
        
        self.cb_month.setCurrentIndex(QDate.currentDate().month())
        self.cb_year.setCurrentText(str(current_year))
        
        self.cb_month.currentIndexChanged.connect(self.on_filter_changed)
        self.cb_year.currentTextChanged.connect(self.on_filter_changed)
        
        filter_layout.addWidget(lbl_month)
        filter_layout.addWidget(self.cb_month)
        filter_layout.addWidget(lbl_year)
        filter_layout.addWidget(self.cb_year)
        
        self.tabs.setCornerWidget(self.filter_widget, Qt.TopRightCorner)
        
        # Tab 1: Employés
        self.tab_employes = EmployesTab(self)
        self.tabs.addTab(self.tab_employes, "Employés")
        
        # Tab 2: Présences
        self.tab_presences = PresencesTab(self)
        self.tabs.addTab(self.tab_presences, "Présences")
        
        # Tab 3: Salaires
        self.tab_salaires = SalairesTab(self)
        self.tabs.addTab(self.tab_salaires, "Salaires (Fiches de Paie)")
        
        layout.addWidget(self.tabs)
        
        self.on_filter_changed()

    def on_filter_changed(self):
        month = self.cb_month.currentIndex()
        year = self.cb_year.currentText()
        
        filter_month = None if month == 0 else month
        filter_year = None if year == "Tous" else int(year)
        
        # Pass filters to tabs if they support it
        if hasattr(self.tab_presences, 'load_data'):
            self.tab_presences.load_data(filter_month, filter_year)
        if hasattr(self.tab_salaires, 'load_data_filtered'):
            self.tab_salaires.load_data_filtered(filter_month, filter_year)
