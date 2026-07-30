"""Read-only Activity Log page for administration and direction."""

from __future__ import annotations

import html
import json

from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QDateEdit, QDialog, QFileDialog, QGridLayout,
    QHBoxLayout, QLabel, QLineEdit, QMessageBox, QPushButton, QTableWidget,
    QTableWidgetItem, QTextEdit, QVBoxLayout, QWidget,
)

from database import data_manager
from services.activity_log_service import ActivityAccessError
from utils.pdf_generator import PdfGenerator


class ActivityView(QWidget):
    PAGE_SIZE = 100

    def __init__(self, parent=None):
        super().__init__(parent)
        self.page = 1
        self.total = 0
        self.current_items = []
        self._access_allowed = self._check_access()
        self.setup_ui()
        if self._access_allowed:
            self.load_events()

    def _check_access(self):
        try:
            data_manager.activity.require_view_access()
            return True
        except ActivityAccessError:
            return False

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)
        layout.addWidget(QLabel("<h2>Journal des activites</h2>"))

        filters = QGridLayout()
        self.use_dates = QCheckBox("Filtrer par date")
        self.date_from = QDateEdit(QDate.currentDate().addMonths(-1))
        self.date_to = QDateEdit(QDate.currentDate())
        for widget in (self.date_from, self.date_to):
            widget.setCalendarPopup(True)
            widget.setDisplayFormat("yyyy-MM-dd")
        self.actor_filter = QLineEdit()
        self.actor_filter.setPlaceholderText("Utilisateur")
        self.search_filter = QLineEdit()
        self.search_filter.setPlaceholderText("Recherche: identifiant, motif ou message")
        self.section_filter = self._combo(["ALL", "DASHBOARD", "HR", "CAISSE", "CLOTURE", "FOURNISSEURS", "PARTENAIRES", "BANQUE", "RAPPORTS", "DONNEESBASE", "SETTINGS", "ACTIVITY"])
        self.outcome_filter = self._combo(["ALL", "SUCCESS", "DENIED", "FAILED"])
        self.category_filter = self._combo(["ALL", "BUSINESS", "AUTHORIZATION", "AUTHENTICATION", "EXPORT", "IMPORT"])
        self.tab_filter = QLineEdit()
        self.tab_filter.setPlaceholderText("Code tab")
        self.action_filter = QLineEdit()
        self.action_filter.setPlaceholderText("Code operation")
        self.period_filter = QLineEdit()
        self.period_filter.setPlaceholderText("ID periode")
        filters.addWidget(self.use_dates, 0, 0)
        filters.addWidget(self.date_from, 0, 1)
        filters.addWidget(self.date_to, 0, 2)
        filters.addWidget(QLabel("Section"), 0, 3)
        filters.addWidget(self.section_filter, 0, 4)
        filters.addWidget(QLabel("Resultat"), 0, 5)
        filters.addWidget(self.outcome_filter, 0, 6)
        filters.addWidget(QLabel("Utilisateur"), 1, 0)
        filters.addWidget(self.actor_filter, 1, 1)
        filters.addWidget(QLabel("Categorie"), 1, 2)
        filters.addWidget(self.category_filter, 1, 3)
        filters.addWidget(self.period_filter, 1, 4)
        filters.addWidget(self.search_filter, 1, 5, 1, 2)
        filters.addWidget(QLabel("Tab"), 2, 0)
        filters.addWidget(self.tab_filter, 2, 1)
        filters.addWidget(QLabel("Operation"), 2, 2)
        filters.addWidget(self.action_filter, 2, 3)
        layout.addLayout(filters)

        toolbar = QHBoxLayout()
        self.btn_search = QPushButton("Rechercher")
        self.btn_search.clicked.connect(self.refresh)
        self.btn_csv = QPushButton("Exporter CSV")
        self.btn_csv.clicked.connect(self.export_csv)
        self.btn_pdf = QPushButton("Exporter PDF")
        self.btn_pdf.clicked.connect(self.export_pdf)
        toolbar.addWidget(self.btn_search)
        toolbar.addWidget(self.btn_csv)
        toolbar.addWidget(self.btn_pdf)
        toolbar.addStretch()
        layout.addLayout(toolbar)

        self.table = QTableWidget(0, 10)
        self.table.setHorizontalHeaderLabels([
            "Date", "Utilisateur", "Role", "Section", "Tab", "Operation", "Entite", "ID", "Resultat", "Motif",
        ])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.doubleClicked.connect(self.show_details)
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

        pagination = QHBoxLayout()
        self.btn_previous = QPushButton("Precedent")
        self.btn_next = QPushButton("Suivant")
        self.page_label = QLabel("Page 1")
        self.btn_previous.clicked.connect(self.previous_page)
        self.btn_next.clicked.connect(self.next_page)
        pagination.addWidget(self.btn_previous)
        pagination.addWidget(self.btn_next)
        pagination.addWidget(self.page_label)
        pagination.addStretch()
        layout.addLayout(pagination)

        if not self._access_allowed:
            for widget in (self.btn_search, self.btn_csv, self.btn_pdf, self.btn_previous, self.btn_next, self.table):
                widget.setEnabled(False)
            layout.addWidget(QLabel("Acces reserve a l'administration et a la direction."))

    @staticmethod
    def _combo(values):
        combo = QComboBox()
        combo.addItems(values)
        return combo

    def filters(self):
        values = {
            "actor_username": self.actor_filter.text().strip(),
            "section_code": self.section_filter.currentText(),
            "outcome": self.outcome_filter.currentText(),
            "event_category": self.category_filter.currentText(),
            "tab_code": self.tab_filter.text().strip(),
            "action_code": self.action_filter.text().strip(),
            "search": self.search_filter.text().strip(),
        }
        if self.use_dates.isChecked():
            values["date_from"] = self.date_from.date().toString("yyyy-MM-dd")
            values["date_to"] = self.date_to.date().toString("yyyy-MM-dd")
        if self.period_filter.text().strip().isdigit():
            values["period_id"] = int(self.period_filter.text().strip())
        return values

    def refresh(self):
        self.page = 1
        self.load_events()

    def load_events(self):
        try:
            result = data_manager.activity.list_events(filters=self.filters(), page=self.page, page_size=self.PAGE_SIZE)
        except ActivityAccessError as error:
            QMessageBox.warning(self, "Acces refuse", str(error))
            return
        self.current_items = result["items"]
        self.total = result["total"]
        self.table.setRowCount(len(self.current_items))
        fields = ["created_at", "actor_username", "actor_role", "section_code", "tab_code", "action_code", "entity_type", "entity_id", "outcome", "reason"]
        for row_index, event in enumerate(self.current_items):
            for column, field in enumerate(fields):
                item = QTableWidgetItem(str(event.get(field) or ""))
                if column == 0:
                    item.setData(Qt.UserRole, event.get("id_event"))
                self.table.setItem(row_index, column, item)
        self.table.resizeColumnsToContents()
        last_page = max(1, (self.total + self.PAGE_SIZE - 1) // self.PAGE_SIZE)
        self.page_label.setText(f"Page {self.page}/{last_page} - {self.total} evenement(s)")
        self.btn_previous.setEnabled(self.page > 1)
        self.btn_next.setEnabled(self.page < last_page)

    def previous_page(self):
        if self.page > 1:
            self.page -= 1
            self.load_events()

    def next_page(self):
        if self.page * self.PAGE_SIZE < self.total:
            self.page += 1
            self.load_events()

    def show_details(self):
        selected = self.table.selectedItems()
        if not selected:
            return
        event_id = self.table.item(selected[0].row(), 0).data(Qt.UserRole)
        event = data_manager.activity.get_event(event_id)
        if not event:
            return
        dialog = QDialog(self)
        dialog.setWindowTitle("Details de l'activite")
        dialog.resize(720, 520)
        layout = QVBoxLayout(dialog)
        details = QTextEdit()
        details.setReadOnly(True)
        details.setPlainText(json.dumps(event, ensure_ascii=False, indent=2, default=str))
        layout.addWidget(details)
        dialog.exec()

    def export_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Exporter le journal", "Journal_Activites.csv", "CSV (*.csv)")
        if not path:
            return
        try:
            data_manager.activity.export_csv(path, filters=self.filters())
            QMessageBox.information(self, "Succes", "Export CSV enregistre dans le journal.")
        except (ActivityAccessError, OSError) as error:
            QMessageBox.warning(self, "Export refuse", str(error))

    def export_pdf(self):
        path, _ = QFileDialog.getSaveFileName(self, "Exporter le journal", "Journal_Activites.pdf", "PDF (*.pdf)")
        if not path:
            return
        rows = self.current_items
        html_rows = "".join(
            "<tr>" + "".join(
                f"<td>{html.escape(str(event.get(field) or ''))}</td>"
                for field in ("created_at", "actor_username", "section_code", "action_code", "entity_type", "entity_id", "outcome", "reason")
            ) + "</tr>" for event in rows
        )
        table_html = "<table><tr><th>Date</th><th>Utilisateur</th><th>Section</th><th>Operation</th><th>Entite</th><th>ID</th><th>Resultat</th><th>Motif</th></tr>" + html_rows + "</table>"
        if PdfGenerator().generate_pdf(path, " - Journal des activites", table_html):
            data_manager.activity.record(None, "ACTIVITY_LOG_EXPORTED", "Audit_Events", event_category="EXPORT", message=str(path))
            QMessageBox.information(self, "Succes", "Export PDF enregistre dans le journal.")
        else:
            QMessageBox.warning(self, "Erreur", "Le PDF n'a pas pu etre genere.")
