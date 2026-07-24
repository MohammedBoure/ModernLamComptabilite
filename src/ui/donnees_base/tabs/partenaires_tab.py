from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
from PySide6.QtCore import Qt
from database import data_manager
from ui.table_helper import make_table_editable
from ui.partenaires.dialogs import PartenaireDialog

class DonneesBasePartenairesTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        self.tbl_partenaires = QTableWidget()
        self.tbl_partenaires.setColumnCount(4)
        self.tbl_partenaires.setHorizontalHeaderLabels([
            "ID", "Partenaire", "Type", "Solde Initial"
        ])
        self.tbl_partenaires.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tbl_partenaires.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tbl_partenaires.setSelectionBehavior(QTableWidget.SelectRows)
        
        self.toolbar = make_table_editable(
            self.tbl_partenaires, "Partenaires", "id_partenaire",
            lambda r: self.tbl_partenaires.item(r, 0).data(Qt.UserRole)
                      if self.tbl_partenaires.item(r, 0) else None,
            PartenaireDialog, self.load_data, self,
            add_callback=self.add_partenaire,
            add_label="Nouveau Partenaire",
            delete_callback=self.delete_partenaire
        )
        
        layout.addWidget(self.toolbar)
        layout.addWidget(self.tbl_partenaires)

    def load_data(self):
        data = data_manager.db.fetch_all("SELECT * FROM Partenaires ORDER BY nom_partenaire")
        self.tbl_partenaires.setRowCount(len(data))
        for i, row in enumerate(data):
            item_id = QTableWidgetItem(str(row['id_partenaire']))
            item_id.setData(Qt.UserRole, row['id_partenaire'])
            self.tbl_partenaires.setItem(i, 0, item_id)
            self.tbl_partenaires.setItem(i, 1, QTableWidgetItem(row['nom_partenaire']))
            self.tbl_partenaires.setItem(i, 2, QTableWidgetItem(row['type_partenaire']))
            self.tbl_partenaires.setItem(i, 3, QTableWidgetItem(f"{float(row['solde_initial'] or 0):.2f}"))

    def add_partenaire(self):
        dlg = PartenaireDialog(self)
        if dlg.exec():
            self.load_data()

    def delete_partenaire(self, id_partenaire):
        reply = QMessageBox.question(
            self, "Confirmation", 
            "Voulez-vous vraiment supprimer ce partenaire ?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            success, _ = data_manager.db.delete_record("Partenaires", "id_partenaire", id_partenaire)
            if success:
                QMessageBox.information(self, "Succès", "Partenaire supprimé avec succès.")
            else:
                QMessageBox.warning(self, "Erreur", "Une erreur est survenue lors de la suppression.")
            return success
        return False
