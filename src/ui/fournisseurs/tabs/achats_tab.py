from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QHeaderView, QPushButton
)
from PySide6.QtCore import Qt
from database import data_manager
from ui.table_helper import make_table_editable, _btn, _vsep, _PATH_ADD, _svg_icon
from ui.fournisseurs.dialogs import DepenseFournisseurDialog


_sentinel = object()


class AchatsTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.month = None
        self.year = None
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(4)

        self.tbl_achats = QTableWidget()
        self.tbl_achats.setColumnCount(6)
        self.tbl_achats.setHorizontalHeaderLabels(
            ["Date", "Fournisseur", "Document", "Montant", "Paiement", "Observation"]
        )
        self.tbl_achats.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl_achats.setEditTriggers(QTableWidget.NoEditTriggers)

        # Main toolbar: Add Dépense + Edit + Delete + Refresh
        toolbar = make_table_editable(
            self.tbl_achats, "Depenses_Achats", "id_depense",
            lambda r: self.tbl_achats.item(r, 0).data(Qt.UserRole)
                      if self.tbl_achats.item(r, 0) else None,
            DepenseFournisseurDialog, self.load_data, self,
            add_callback=self.add_depense,
            add_label="Nouvelle Dépense",
        )
        # Extra "Nouveau Paiement" button inserted into the toolbar layout
        btn_pay = _btn("Nouveau Paiement", _PATH_ADD, "#37474f", "#263238")
        btn_pay.clicked.connect(self.add_paiement)
        toolbar.layout().insertWidget(1, btn_pay)  # after Ajouter, before separator

        layout.addWidget(toolbar)
        layout.addWidget(self.tbl_achats)

    def add_depense(self):
        dlg = DepenseFournisseurDialog(self)
        if dlg.exec():
            self.load_data(getattr(self, "month", None), getattr(self, "year", None))

    def add_paiement(self):
        from ui.fournisseurs.dialogs import PaiementFournisseurDialog
        dlg = PaiementFournisseurDialog(self)
        if dlg.exec():
            self.load_data(getattr(self, "month", None), getattr(self, "year", None))

    def load_data(self, month=_sentinel, year=_sentinel):
        if month is not _sentinel:
            self.month = month
        if year is not _sentinel:
            self.year = year
            
        m = self.month
        y = self.year

        data = data_manager.fournisseurs.get_achats(m, y)
        self.tbl_achats.setRowCount(len(data))
        for i, row in enumerate(data):
            item_date = QTableWidgetItem(str(row['date_facture']))
            item_date.setData(Qt.UserRole, row['id_depense'])
            self.tbl_achats.setItem(i, 0, item_date)
            self.tbl_achats.setItem(i, 1, QTableWidgetItem(str(row['nom_fournisseur'])))
            self.tbl_achats.setItem(i, 2, QTableWidgetItem(str(row['type_document'])))
            self.tbl_achats.setItem(i, 3, QTableWidgetItem(f"{row['montant_total']:.2f}"))
            self.tbl_achats.setItem(i, 4, QTableWidgetItem(str(row['mode_paiement'])))
            self.tbl_achats.setItem(i, 5, QTableWidgetItem(str(row['observation'])))
