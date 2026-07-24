from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox, QPushButton
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from database import data_manager

class DashboardView(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.load_data()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 20)
        layout.setSpacing(15)
        
        # Top Bar
        top_bar_layout = QHBoxLayout()
        top_bar_layout.addStretch()
        self.btn_refresh = QPushButton("Actualiser")
        self.btn_refresh.setStyleSheet("padding: 5px 15px; font-weight: bold; background-color: #f1f5f9; border: 1px solid #cbd5e1; border-radius: 4px;")
        self.btn_refresh.clicked.connect(self.load_data)
        top_bar_layout.addWidget(self.btn_refresh)
        layout.addLayout(top_bar_layout)

        # Summary Cards
        cards_layout = QHBoxLayout()
        
        self.card_ca = self.create_card("Chiffre d'Affaire (Ce Mois)", "0.00 DZD")
        self.card_profit = self.create_card("Profitabilité (Ce Mois)", "0.00 DZD")
        self.card_depenses = self.create_card("Total Dépenses", "0.00 DZD")
        self.card_coffre = self.create_card("Coffre Stratégique (Global)", "0.00 DZD")
        self.card_coffre.setStyleSheet("QGroupBox { background-color: #e8f5e9; border-radius: 8px; border: 1px solid #c8e6c9; }")
        self.card_coffre.value_label.setStyleSheet("color: #2e7d32; font-size: 20px; font-weight: bold;")
        
        cards_layout.addWidget(self.card_ca)
        cards_layout.addWidget(self.card_profit)
        cards_layout.addWidget(self.card_depenses)
        cards_layout.addWidget(self.card_coffre)
        
        layout.addLayout(cards_layout)
        
        # Table Profitabilité
        group_table = QGroupBox("Détails de Profitabilité Mensuelle")
        table_layout = QVBoxLayout(group_table)
        
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Année", "Mois", "CA Total", "Dépenses", "Paie", "Profitabilité Nette"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        table_layout.addWidget(self.table)
        layout.addWidget(group_table)
        
    def create_card(self, title, value):
        card = QGroupBox()
        card.setStyleSheet("QGroupBox { background-color: white; border-radius: 8px; border: 1px solid #dcdde1; }")
        layout = QVBoxLayout(card)
        
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("color: #7f8fa6; font-size: 14px;")
        lbl_title.setAlignment(Qt.AlignCenter)
        
        lbl_value = QLabel(value)
        lbl_value.setStyleSheet("color: #2f3640; font-size: 20px; font-weight: bold;")
        lbl_value.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(lbl_title)
        layout.addWidget(lbl_value)
        
        # Keep a reference to the value label to update it later
        card.value_label = lbl_value
        return card
        
    def load_data(self):
        # Fetch Profitability Data using database manager
        data = data_manager.dashboard.get_monthly_profitability()
        
        self.table.setRowCount(len(data))
        for row_idx, row in enumerate(data):
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(row['annee'])))
            self.table.setItem(row_idx, 1, QTableWidgetItem(str(row['mois'])))
            self.table.setItem(row_idx, 2, QTableWidgetItem(f"{row['chiffre_affaire_total'] or 0:.2f}"))
            self.table.setItem(row_idx, 3, QTableWidgetItem(f"{row['total_depenses'] or 0:.2f}"))
            self.table.setItem(row_idx, 4, QTableWidgetItem(f"{row['total_paie'] or 0:.2f}"))
            self.table.setItem(row_idx, 5, QTableWidgetItem(f"{row['profitabilite_nette'] or 0:.2f}"))
            
        # Update Cards with the latest month
        if data:
            latest = data[0]
            self.card_ca.value_label.setText(f"{latest['chiffre_affaire_total'] or 0:.2f} DZD")
            self.card_profit.value_label.setText(f"{latest['profitabilite_nette'] or 0:.2f} DZD")
            self.card_depenses.value_label.setText(f"{latest['total_depenses'] or 0:.2f} DZD")
            
        # Update Coffre Stratégique
        summary_coffre = data_manager.caisse.get_coffre_summary(None, None)
        self.card_coffre.value_label.setText(f"{summary_coffre['coffre_net']:,.2f} DZD")
