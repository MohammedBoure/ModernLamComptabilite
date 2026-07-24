from PySide6.QtWidgets import (
    QWidget, QVBoxLayout,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt
from database import data_manager
from ui.table_helper import make_table_editable, _btn, _PATH_ADD
from ui.partenaires.dialogs import OperationPartenaireDialog


_sentinel = object()


class OperationsPartenairesTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.month = None
        self.year = None
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(4)

        self.tbl_operations = QTableWidget()
        self.tbl_operations.setColumnCount(7)
        self.tbl_operations.setHorizontalHeaderLabels(
            ["Date", "Partenaire", "Type Doc", "Montant", "Date Réception", "État", "Observation"]
        )
        self.tbl_operations.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl_operations.setEditTriggers(QTableWidget.NoEditTriggers)

        toolbar = make_table_editable(
            self.tbl_operations, "Operations_Partenaires", "id_operation",
            lambda r: self.tbl_operations.item(r, 0).data(Qt.UserRole)
                      if self.tbl_operations.item(r, 0) else None,
            OperationPartenaireDialog, self.load_data, self,
            add_callback=self.add_operation,
            add_label="Nouvelle Opération",
        )
        # Extra "Nouveau Paiement" button
        btn_pay = _btn("Nouveau Paiement", _PATH_ADD, "#37474f", "#263238")
        btn_pay.clicked.connect(self.add_paiement)
        toolbar.layout().insertWidget(1, btn_pay)

        layout.addWidget(toolbar)
        layout.addWidget(self.tbl_operations)

    def add_operation(self):
        dlg = OperationPartenaireDialog(self)
        if dlg.exec():
            self.load_data(getattr(self, "month", None), getattr(self, "year", None))

    def add_paiement(self):
        from ui.partenaires.dialogs import PaiementPartenaireDialog
        dlg = PaiementPartenaireDialog(self)
        if dlg.exec():
            self.load_data(getattr(self, "month", None), getattr(self, "year", None))

    def load_data(self, month=_sentinel, year=_sentinel):
        if month is not _sentinel:
            self.month = month
        if year is not _sentinel:
            self.year = year
            
        m = self.month
        y = self.year

        data = data_manager.partenaires.get_operations(m, y)
        self.tbl_operations.setRowCount(len(data))
        for i, row in enumerate(data):
            item_date = QTableWidgetItem(str(row['date_operation']))
            item_date.setData(Qt.UserRole, row['id_operation'])
            self.tbl_operations.setItem(i, 0, item_date)
            self.tbl_operations.setItem(i, 1, QTableWidgetItem(str(row['nom_partenaire'])))
            self.tbl_operations.setItem(i, 2, QTableWidgetItem(str(row['type_document'])))
            self.tbl_operations.setItem(i, 3, QTableWidgetItem(f"{row['montant_total']:.2f}"))
            self.tbl_operations.setItem(i, 4, QTableWidgetItem(str(row['date_reception'] or '-')))
            self.tbl_operations.setItem(i, 5, QTableWidgetItem(str(row['etat_paiement'] or '-')))
            self.tbl_operations.setItem(i, 6, QTableWidgetItem(str(row['observation'] or '-')))
