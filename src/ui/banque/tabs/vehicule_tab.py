from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, 
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from database import data_manager
from ui.table_helper import make_table_editable
from ui.banque.dialogs import VehiculeServiceDialog

class VehiculeServiceTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(4)
        
        self.tbl_vehicule = QTableWidget()
        self.tbl_vehicule.setColumnCount(6)
        self.tbl_vehicule.setHorizontalHeaderLabels([
            "DATE", "MONTANT", "DETAILS", "KILOMETRAGE", "GPL / KILOMETRE EN +", "ESSENCE / KILOMETRE EN +"
        ])
        self.tbl_vehicule.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl_vehicule.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # Setup toolbar
        self.toolbar = make_table_editable(
            self.tbl_vehicule,
            "Vehicule_Service",
            "id_suivi",
            lambda row: self.tbl_vehicule.item(row, 0).data(Qt.UserRole),
            VehiculeServiceDialog,
            self.load_data,
            self,
            add_callback=self.add_vehicule,
            add_label="Ajouter",
            delete_callback=self.delete_vehicule
        )
        layout.addWidget(self.toolbar)
        layout.addWidget(self.tbl_vehicule)
        
        # Totals and Averages Table
        self.tbl_total = QTableWidget()
        self.tbl_total.setColumnCount(6)
        self.tbl_total.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl_total.horizontalHeader().setVisible(False)
        self.tbl_total.verticalHeader().setVisible(False)
        self.tbl_total.setRowCount(2)
        self.tbl_total.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tbl_total.setFixedHeight(60)
        self.tbl_total.setFocusPolicy(Qt.NoFocus)
        self.tbl_total.setSelectionMode(QTableWidget.NoSelection)
        self.tbl_total.setStyleSheet("QTableWidget { border-top: none; }")
        layout.addWidget(self.tbl_total)

    def add_vehicule(self):
        dlg = VehiculeServiceDialog(self)
        if dlg.exec():
            self.load_data()

    def delete_vehicule(self, pk):
        record = data_manager.db.fetch_one("SELECT id_transaction_coffre FROM Vehicule_Service WHERE id_suivi = %s", (pk,))
        if record and record.get('id_transaction_coffre'):
            data_manager.db.delete_record("Mouvement_Coffre", "id_transaction", record['id_transaction_coffre'])
        success, _ = data_manager.db.delete_record("Vehicule_Service", "id_suivi", pk)
        return success

    def load_data(self):
        # Fetch all logs sorted chronologically to compute distance increments
        data = data_manager.db.fetch_all("SELECT * FROM Vehicule_Service ORDER BY date_suivi ASC, id_suivi ASC")
        
        prev_km = None
        processed_data = []
        for idx, row in enumerate(data):
            km = row['kilometrage']
            diff = 0.0
            if prev_km is not None:
                diff = float(km - prev_km)
            row['diff_km'] = diff
            row['is_first'] = (idx == 0)
            prev_km = km
            processed_data.append(row)
            
        # For display, reverse to show newest first
        display_data = list(reversed(processed_data))
        
        self.tbl_vehicule.setRowCount(len(display_data))
        
        for i, row in enumerate(display_data):
            item_date = QTableWidgetItem(str(row['date_suivi']))
            item_date.setData(Qt.UserRole, row['id_suivi'])
            item_date.setTextAlignment(Qt.AlignCenter)
            self.tbl_vehicule.setItem(i, 0, item_date)
            
            item_montant = QTableWidgetItem(f"{float(row['montant_carburant']):,.2f}")
            item_montant.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.tbl_vehicule.setItem(i, 1, item_montant)
            
            item_details = QTableWidgetItem(str(row['details'] or '-'))
            item_details.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.tbl_vehicule.setItem(i, 2, item_details)
            
            item_km = QTableWidgetItem(str(row['kilometrage']))
            item_km.setTextAlignment(Qt.AlignCenter)
            self.tbl_vehicule.setItem(i, 3, item_km)
            
            is_first = row['is_first']
            is_gpl = str(row['type_carburant']).upper() == 'GPL'
            
            if is_first:
                gpl_val = "-"
                ess_val = "-"
            else:
                gpl_val = f"{row['diff_km']:,.2f}" if is_gpl else "-"
                ess_val = f"{row['diff_km']:,.2f}" if not is_gpl else "-"
                
            item_gpl = QTableWidgetItem(gpl_val)
            item_gpl.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.tbl_vehicule.setItem(i, 4, item_gpl)
            
            item_ess = QTableWidgetItem(ess_val)
            item_ess.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.tbl_vehicule.setItem(i, 5, item_ess)
            
        # Compute totals & averages
        total_montant = sum(float(row['montant_carburant']) for row in processed_data)
        total_gpl = sum(row['diff_km'] for row in processed_data if not row['is_first'] and str(row['type_carburant']).upper() == 'GPL')
        total_essence = sum(row['diff_km'] for row in processed_data if not row['is_first'] and str(row['type_carburant']).upper() == 'ESSENCE')
        
        gpl_diffs = [row['diff_km'] for row in processed_data if not row['is_first'] and str(row['type_carburant']).upper() == 'GPL']
        essence_diffs = [row['diff_km'] for row in processed_data if not row['is_first'] and str(row['type_carburant']).upper() == 'ESSENCE']
        
        avg_gpl = sum(gpl_diffs) / len(gpl_diffs) if gpl_diffs else 0.0
        avg_essence = sum(essence_diffs) / len(essence_diffs) if essence_diffs else 0.0
        
        self.tbl_total.clear()
        
        font_bold = QFont()
        font_bold.setBold(True)
        
        # Row 0: Total
        item_tot_lbl = QTableWidgetItem("Total")
        item_tot_lbl.setFont(font_bold)
        item_tot_lbl.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.tbl_total.setItem(0, 0, item_tot_lbl)
        
        item_tot_montant = QTableWidgetItem(f"{total_montant:,.2f}")
        item_tot_montant.setFont(font_bold)
        item_tot_montant.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.tbl_total.setItem(0, 1, item_tot_montant)
        
        self.tbl_total.setItem(0, 2, QTableWidgetItem(""))
        self.tbl_total.setItem(0, 3, QTableWidgetItem(""))
        
        item_tot_gpl = QTableWidgetItem(f"{total_gpl:,.2f}")
        item_tot_gpl.setFont(font_bold)
        item_tot_gpl.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.tbl_total.setItem(0, 4, item_tot_gpl)
        
        item_tot_ess = QTableWidgetItem(f"{total_essence:,.2f}")
        item_tot_ess.setFont(font_bold)
        item_tot_ess.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.tbl_total.setItem(0, 5, item_tot_ess)
        
        # Row 1: Moyenne KM/Plein
        item_avg_lbl = QTableWidgetItem("Moyenne KM/Plein")
        item_avg_lbl.setFont(font_bold)
        item_avg_lbl.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.tbl_total.setItem(1, 0, item_avg_lbl)
        
        self.tbl_total.setItem(1, 1, QTableWidgetItem(""))
        self.tbl_total.setItem(1, 2, QTableWidgetItem(""))
        self.tbl_total.setItem(1, 3, QTableWidgetItem(""))
        
        item_avg_gpl = QTableWidgetItem(f"{avg_gpl:,.2f}")
        item_avg_gpl.setFont(font_bold)
        item_avg_gpl.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.tbl_total.setItem(1, 4, item_avg_gpl)
        
        item_avg_ess = QTableWidgetItem(f"{avg_essence:,.2f}")
        item_avg_ess.setFont(font_bold)
        item_avg_ess.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.tbl_total.setItem(1, 5, item_avg_ess)
