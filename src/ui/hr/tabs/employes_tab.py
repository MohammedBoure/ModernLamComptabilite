from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
)
from PySide6.QtCore import Qt, QDate, QSize
from PySide6.QtGui import QFont, QColor
import datetime
from database import data_manager
from ui.table_helper import make_table_editable
from ui.hr.dialogs import EmployeDialog


def calculate_age(date_naissance_str):
    if not date_naissance_str:
        return ""
    try:
        dn = datetime.datetime.strptime(str(date_naissance_str), "%Y-%m-%d").date()
        today = datetime.date.today()
        age = today.year - dn.year - ((today.month, today.day) < (dn.month, dn.day))
        return f"{age} ans"
    except:
        return ""


def calculate_conge_restant(date_embauche_str, date_demission_str, jours_pris):
    if not date_embauche_str:
        return ""
    try:
        de = datetime.datetime.strptime(str(date_embauche_str), "%Y-%m-%d").date()
        if date_demission_str:
            end_date = datetime.datetime.strptime(str(date_demission_str), "%Y-%m-%d").date()
        else:
            end_date = datetime.date.today()
            
        if end_date < de:
            return "0 j"
            
        months = (end_date.year - de.year) * 12 + (end_date.month - de.month)
        if de.day <= 15:
            months += 1
            
        jours_acquis = max(0, months) * 2.5
        jours_restants = max(0.0, jours_acquis - float(jours_pris or 0))
        return f"{jours_restants} j"
    except:
        return ""


class EmployesTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Title
        lbl_title = QLabel("Direction des Ressources Humaines (DRH) - Registre Unifié")
        lbl_title.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        lbl_title.setFont(title_font)
        lbl_title.setStyleSheet("color: #2c3e50; margin-bottom: 5px;")
        layout.addWidget(lbl_title)

        # Description
        lbl_desc = QLabel("Ce tableau fusionne les informations personnelles, les contrats et les congés des employés.")
        lbl_desc.setAlignment(Qt.AlignCenter)
        lbl_desc.setStyleSheet("color: #7f8c8d; margin-bottom: 10px;")
        layout.addWidget(lbl_desc)

        self.tbl_employes = QTableWidget()
        self.tbl_employes.setColumnCount(20)
        self.tbl_employes.setHorizontalHeaderLabels([
            "N°", "NOM/PRÉNOM", "FONCTION", "DATE NAISSANCE", "ÂGE", 
            "LIEU DE NAISSANCE", "ADRESSE", "TÉL 01", "TÉL 02", "NIN", "N° SS", "N° ANEM",
            "DATE D'EMBAUCHE", "DATE D'INSC. CNAS", "TYPE CONTRAT", "CONTRAT DU", "AU", "DÉMISSION",
            "CONGÉ (RESTANT)", "REMARQUE"
        ])
        
        # Adjust resize mode to fit contents rather than stretch, as it's too large
        self.tbl_employes.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.tbl_employes.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tbl_employes.setSelectionBehavior(QTableWidget.SelectRows)
        self.tbl_employes.setSelectionMode(QTableWidget.SingleSelection)
        self.tbl_employes.setAlternatingRowColors(True)

        toolbar = make_table_editable(
            self.tbl_employes, "Employes", "id_employe",
            lambda r: int(self.tbl_employes.item(r, 0).data(Qt.UserRole))
                      if self.tbl_employes.item(r, 0) else None,
            EmployeDialog, self.load_data, self,
            add_callback=self.add_employe,
            add_label="+ Nouveau Dossier Employé"
        )
        layout.addWidget(toolbar)
        layout.addWidget(self.tbl_employes)

    def add_employe(self):
        dlg = EmployeDialog(self)
        if dlg.exec():
            self.load_data()

    def load_data(self):
        data = data_manager.hr.get_drh_master_list()
        self.tbl_employes.setRowCount(len(data))
        
        for i, row in enumerate(data):
            # Calculate Age
            age_str = calculate_age(row.get('date_naissance'))
            
            # Calculate Congé
            conge_str = calculate_conge_restant(
                row.get('date_embauche'), 
                row.get('date_demission'), 
                row.get('jours_conge_pris')
            )
            
            # Store full row in memory via id_employe UserRole to edit easily
            item_id = QTableWidgetItem(str(row['id_employe']))
            item_id.setData(Qt.UserRole, row['id_employe'])
            item_id.setTextAlignment(Qt.AlignCenter)
            
            item_conge = QTableWidgetItem(conge_str)
            item_conge.setTextAlignment(Qt.AlignCenter)
            item_conge.setFont(QFont("Arial", 9, QFont.Bold))
            if conge_str and float(conge_str.replace(" j", "")) > 0:
                item_conge.setForeground(QColor("#2e7d32")) # Green for available leaves
            else:
                item_conge.setForeground(QColor("#c62828")) # Red
                
            item_nom = QTableWidgetItem(str(row.get('nom_prenom') or ''))
            # Photo Thumbnail
            photo_path = row.get('photo_path')
            import os
            from PySide6.QtGui import QIcon, QPixmap
            if photo_path and os.path.exists(photo_path):
                pixmap = QPixmap(photo_path).scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                item_nom.setIcon(QIcon(pixmap))
                
            self.tbl_employes.setItem(i, 0, item_id)
            self.tbl_employes.setItem(i, 1, item_nom)
            self.tbl_employes.setItem(i, 2, QTableWidgetItem(str(row.get('fonction') or '')))
            self.tbl_employes.setItem(i, 3, QTableWidgetItem(str(row.get('date_naissance') or '')))
            self.tbl_employes.setItem(i, 4, QTableWidgetItem(age_str))
            self.tbl_employes.setItem(i, 5, QTableWidgetItem(str(row.get('lieu_naissance') or '')))
            self.tbl_employes.setItem(i, 6, QTableWidgetItem(str(row.get('adresse') or '')))
            self.tbl_employes.setItem(i, 7, QTableWidgetItem(str(row.get('tel_1') or '')))
            self.tbl_employes.setItem(i, 8, QTableWidgetItem(str(row.get('tel_2') or '')))
            self.tbl_employes.setItem(i, 9, QTableWidgetItem(str(row.get('nin') or '')))
            self.tbl_employes.setItem(i, 10, QTableWidgetItem(str(row.get('nss') or '')))
            self.tbl_employes.setItem(i, 11, QTableWidgetItem(str(row.get('n_anem') or '')))
            self.tbl_employes.setItem(i, 12, QTableWidgetItem(str(row.get('date_embauche') or '')))
            self.tbl_employes.setItem(i, 13, QTableWidgetItem(str(row.get('date_inscription_cnas') or '')))
            self.tbl_employes.setItem(i, 14, QTableWidgetItem(str(row.get('type_contrat') or '')))
            self.tbl_employes.setItem(i, 15, QTableWidgetItem(str(row.get('date_embauche') or ''))) # Contrat DU
            self.tbl_employes.setItem(i, 16, QTableWidgetItem(str(row.get('date_fin_contrat') or ''))) # AU
            self.tbl_employes.setItem(i, 17, QTableWidgetItem(str(row.get('date_demission') or ''))) # DÉMISSION
            self.tbl_employes.setItem(i, 18, item_conge)
            self.tbl_employes.setItem(i, 19, QTableWidgetItem(str(row.get('remarque_drh') or '')))
            
        if self.tbl_employes.rowCount() > 0:
            self.tbl_employes.resizeColumnsToContents()
            self.tbl_employes.setIconSize(QSize(32, 32))
            self.tbl_employes.setRowHeight(i, 40)
            self.tbl_employes.setColumnWidth(1, 250) # Nom
            self.tbl_employes.setColumnWidth(6, 250) # Adresse
