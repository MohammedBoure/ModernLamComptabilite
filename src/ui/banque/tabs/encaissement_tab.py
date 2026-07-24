from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, 
    QTableWidget, QTableWidgetItem, QHeaderView, QPushButton
)
from PySide6.QtCore import Qt, QDate
from database import data_manager
from ui.table_helper import make_table_editable
from ui.banque.dialogs import EtatEncaissementDialog

class EtatEncaissementTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        self.tbl_encaissement = QTableWidget()
        self.tbl_encaissement.setColumnCount(5)
        self.tbl_encaissement.setHorizontalHeaderLabels(["ID", "Date", "Désignation", "Montant", "Observations"])
        self.tbl_encaissement.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl_encaissement.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # Setup toolbar
        self.toolbar = make_table_editable(
            self.tbl_encaissement,
            "Etat_Encaissement",
            "id_encaissement",
            lambda row: self.tbl_encaissement.item(row, 0).data(Qt.UserRole),
            EtatEncaissementDialog,
            self.load_data,
            self,
            add_callback=self.add_encaissement,
            add_label="Ajouter"
        )
        
        self.btn_export = QPushButton("🖨️ Exporter PDF (Mois)")
        self.btn_export.setStyleSheet("background-color: #f57c00; color: white; padding: 6px 15px; font-weight: bold; border-radius: 4px;")
        self.btn_export.clicked.connect(self.export_pdf)
        self.toolbar.layout().insertWidget(1, self.btn_export)
        
        layout.addWidget(self.toolbar)
        layout.addWidget(self.tbl_encaissement)

    def add_encaissement(self):
        dlg = EtatEncaissementDialog(self)
        if dlg.exec():
            self.load_data()

    def load_data(self):
        data = data_manager.banque.get_encaissements()
        self.tbl_encaissement.setRowCount(len(data))
        for i, row in enumerate(data):
            item_id = QTableWidgetItem(str(row['id_encaissement']))
            item_id.setData(Qt.UserRole, row['id_encaissement'])
            self.tbl_encaissement.setItem(i, 0, item_id)
            self.tbl_encaissement.setItem(i, 1, QTableWidgetItem(str(row['date_encaissement'])))
            self.tbl_encaissement.setItem(i, 2, QTableWidgetItem(str(row['designation'])))
            self.tbl_encaissement.setItem(i, 3, QTableWidgetItem(f"{row['montant']:.2f}"))
            self.tbl_encaissement.setItem(i, 4, QTableWidgetItem(str(row['observations'] or '-')))

    def export_pdf(self):
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QFileDialog, QMessageBox
        
        dlg = QDialog(self)
        dlg.setWindowTitle("Exporter PDF - Etat d'Encaissement")
        dlg.setFixedSize(300, 150)
        ly = QVBoxLayout(dlg)
        
        form_ly = QHBoxLayout()
        cb_mois = QComboBox()
        cb_mois.addItems([str(m) for m in range(1, 13)])
        cb_mois.setCurrentText(str(QDate.currentDate().month()))
        
        cb_annee = QComboBox()
        current_year = QDate.currentDate().year()
        cb_annee.addItems([str(y) for y in range(current_year-2, current_year+3)])
        cb_annee.setCurrentText(str(current_year))
        
        form_ly.addWidget(QLabel("Mois:"))
        form_ly.addWidget(cb_mois)
        form_ly.addWidget(QLabel("Année:"))
        form_ly.addWidget(cb_annee)
        ly.addLayout(form_ly)
        
        btn_ok = QPushButton("Générer")
        btn_ok.clicked.connect(dlg.accept)
        ly.addWidget(btn_ok)
        
        if dlg.exec():
            m = int(cb_mois.currentText())
            y = int(cb_annee.currentText())
            
            # Fetch data for this month
            query = "SELECT * FROM Etat_Encaissement WHERE MONTH(date_encaissement)=%s AND YEAR(date_encaissement)=%s ORDER BY date_encaissement ASC"
            records = data_manager.db.fetch_all(query, (m, y))
            
            if not records:
                QMessageBox.information(self, "Info", "Aucun enregistrement pour ce mois.")
                return
                
            path, _ = QFileDialog.getSaveFileName(self, "Enregistrer PDF", f"Etat_Encaissement_{m:02d}_{y}.pdf", "PDF (*.pdf)")
            if not path:
                return
                
            # Build HTML table with explicit widths to force 100% distribution
            html = "<table><tr><th width='5%'>N°</th><th width='15%'>DATE</th><th width='40%'>DÉSIGNATION</th><th width='25%'>OBSERVATIONS</th><th width='15%' class='right'>MONTANTS</th></tr>"
            total = 0.0
            for i, r in enumerate(records, 1):
                obs = r['observations'] or ''
                des = r['designation'] or ''
                mnt = float(r['montant'] or 0)
                total += mnt
                html += f"<tr><td>{i}</td><td>{r['date_encaissement']}</td><td>{des}</td><td>{obs}</td><td class='right'>{mnt:,.2f}</td></tr>"
            
            html += f"<tr><td colspan='4' class='right'><b>TOTAL</b></td><td class='right'><b>{total:,.2f} DA</b></td></tr>"
            html += "</table>"
            
            from utils.pdf_generator import PdfGenerator
            gen = PdfGenerator()
            title_suffix = f" - {m:02d}/{y}"
            if gen.generate_pdf(path, title_suffix, html):
                QMessageBox.information(self, "Succès", "PDF généré avec succès!")
            else:
                QMessageBox.critical(self, "Erreur", "Erreur lors de la génération du PDF.")
