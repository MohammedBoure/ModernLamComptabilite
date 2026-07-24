from PySide6.QtWidgets import (
    QWidget, QVBoxLayout,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt
from database import data_manager
from ui.table_helper import make_table_editable
from ui.partenaires.dialogs import PartenaireDialog


class ListePartenairesTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(4)

        self.tbl_partenaires = QTableWidget()
        self.tbl_partenaires.setColumnCount(4)
        self.tbl_partenaires.setHorizontalHeaderLabels(
            ["ID", "Nom", "Type", "Solde Initial"]
        )
        self.tbl_partenaires.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl_partenaires.setEditTriggers(QTableWidget.NoEditTriggers)

        toolbar = make_table_editable(
            self.tbl_partenaires, "Partenaires", "id_partenaire",
            lambda r: self.tbl_partenaires.item(r, 0).data(Qt.UserRole)
                      if self.tbl_partenaires.item(r, 0) else None,
            PartenaireDialog, self.load_data, self,
            add_callback=self.add_partenaire,
            add_label="Nouveau Partenaire",
        )
        layout.addWidget(toolbar)
        layout.addWidget(self.tbl_partenaires)

    def add_partenaire(self):
        dlg = PartenaireDialog(self)
        if dlg.exec():
            self.load_data(getattr(self, "month", None), getattr(self, "year", None))

    def load_data(self, month=None, year=None):
        self.month = month
        self.year = year
        data = data_manager.partenaires.get_partenaires()
        self.tbl_partenaires.setRowCount(len(data))
        for i, row in enumerate(data):
            item_id = QTableWidgetItem(str(row['id_partenaire']))
            item_id.setData(Qt.UserRole, row['id_partenaire'])
            self.tbl_partenaires.setItem(i, 0, item_id)
            self.tbl_partenaires.setItem(i, 1, QTableWidgetItem(str(row['nom_partenaire'])))
            self.tbl_partenaires.setItem(i, 2, QTableWidgetItem(str(row['type_partenaire'])))
            self.tbl_partenaires.setItem(i, 3, QTableWidgetItem(f"{row['solde_initial']:.2f}"))
