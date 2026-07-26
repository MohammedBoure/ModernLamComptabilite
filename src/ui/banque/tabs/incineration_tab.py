from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QTableWidget, QTableWidgetItem, QHeaderView, QPushButton,
    QDialog, QComboBox, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt, QDate
from database import data_manager
from ui.table_helper import make_table_editable
from ui.banque.dialogs import StationIncinerationDialog

class StationIncinerationTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # 1. Summary Cards Frame
        self.cards_frame = QFrame()
        self.cards_frame.setObjectName("summary_cards_frame")
        self.cards_frame.setStyleSheet("""
            QFrame#summary_cards_frame {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                padding: 8px;
            }
        """)
        cards_layout = QHBoxLayout(self.cards_frame)
        cards_layout.setContentsMargins(5, 5, 5, 5)
        cards_layout.setSpacing(15)

        self.card_total_poids = self.create_card("Total Poids", "0.00 KG", "#007572")
        self.card_total_montant = self.create_card("Total Montant", "0.00 DA", "#1e293b")
        self.card_non_paye = self.create_card("Non Payé", "0.00 DA", "#dc2626")
        self.card_stats_poids = self.create_card("MAX / MIN / MOY", "Max: 0 | Min: 0 | Moy: 0", "#475569")

        cards_layout.addWidget(self.card_total_poids)
        cards_layout.addWidget(self.card_total_montant)
        cards_layout.addWidget(self.card_non_paye)
        cards_layout.addWidget(self.card_stats_poids)

        layout.addWidget(self.cards_frame)

        # 2. Table Widget
        self.tbl_incineration = QTableWidget()
        self.tbl_incineration.setColumnCount(7)
        self.tbl_incineration.setHorizontalHeaderLabels([
            "ID", "Date", "Date de Remise", "Poids (KG)", "Montant (DA)", "Paiement", "Observations"
        ])
        self.tbl_incineration.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl_incineration.setEditTriggers(QTableWidget.NoEditTriggers)

        # 3. Toolbar
        self.toolbar = make_table_editable(
            self.tbl_incineration,
            "Station_Incineration",
            "id_incineration",
            lambda row: self.tbl_incineration.item(row, 0).data(Qt.UserRole),
            StationIncinerationDialog,
            self.load_data,
            self,
            add_callback=self.add_incineration,
            add_label="Ajouter"
        )

        self.btn_export = QPushButton("🖨️ Exporter PDF (Station Incinération)")
        self.btn_export.setStyleSheet("background-color: #f57c00; color: white; padding: 6px 15px; font-weight: bold; border-radius: 4px;")
        self.btn_export.clicked.connect(self.export_pdf)
        self.toolbar.layout().insertWidget(1, self.btn_export)

        layout.addWidget(self.toolbar)
        layout.addWidget(self.tbl_incineration)

    def create_card(self, title, default_val, color_hex):
        box = QFrame()
        box.setStyleSheet(f"background-color: white; border: 1px solid #cbd5e1; border-radius: 5px; padding: 6px;")
        ly = QVBoxLayout(box)
        ly.setContentsMargins(5, 5, 5, 5)
        ly.setSpacing(2)

        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("font-size: 11px; color: #64748b; font-weight: bold;")
        lbl_val = QLabel(default_val)
        lbl_val.setStyleSheet(f"font-size: 13px; color: {color_hex}; font-weight: bold;")
        lbl_val.setObjectName("value_lbl")

        ly.addWidget(lbl_title)
        ly.addWidget(lbl_val)
        return box

    def update_card_val(self, card_widget, text_val):
        lbl = card_widget.findChild(QLabel, "value_lbl")
        if lbl:
            lbl.setText(text_val)

    def add_incineration(self):
        dlg = StationIncinerationDialog(self)
        if dlg.exec():
            self.load_data()

    def load_data(self):
        rows = data_manager.banque.get_incinerations()
        self.tbl_incineration.setRowCount(len(rows))

        for i, row in enumerate(rows):
            item_id = QTableWidgetItem(str(row['id_incineration']))
            item_id.setData(Qt.UserRole, row['id_incineration'])
            
            poids = float(row.get('poids_kg', 0.0))
            montant = float(row.get('montant_total', 0.0))
            etat = "Payé" if row.get('etat_paiement') == 'PAYE' else "Non payé"
            
            self.tbl_incineration.setItem(i, 0, item_id)
            self.tbl_incineration.setItem(i, 1, QTableWidgetItem(str(row['date_suivi'])))
            self.tbl_incineration.setItem(i, 2, QTableWidgetItem(str(row['date_remise'] or '-')))
            self.tbl_incineration.setItem(i, 3, QTableWidgetItem(f"{poids:.2f} kg"))
            self.tbl_incineration.setItem(i, 4, QTableWidgetItem(f"{montant:,.2f} DA"))

            item_etat = QTableWidgetItem(etat)
            item_etat.setForeground(Qt.green if etat == "Payé" else Qt.red)
            self.tbl_incineration.setItem(i, 5, item_etat)

            self.tbl_incineration.setItem(i, 6, QTableWidgetItem(str(row['observations'] or '-')))

        # Load Statistics
        stats = data_manager.banque.get_incineration_stats()
        tot_p = stats.get('total_poids_kg', 0.0) or 0.0
        tot_m = stats.get('total_montant', 0.0) or 0.0
        tot_np = stats.get('total_non_paye', 0.0) or 0.0
        max_p = stats.get('max_poids_kg', 0.0) or 0.0
        min_p = stats.get('min_poids_kg', 0.0) or 0.0
        avg_p = stats.get('moyenne_poids_kg', 0.0) or 0.0

        self.update_card_val(self.card_total_poids, f"{tot_p:.2f} KG")
        self.update_card_val(self.card_total_montant, f"{tot_m:,.2f} DA")
        self.update_card_val(self.card_non_paye, f"{tot_np:,.2f} DA")
        self.update_card_val(self.card_stats_poids, f"Max: {max_p:.1f} | Min: {min_p:.1f} | Moy: {avg_p:.1f} kg")

    def export_pdf(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Exporter PDF - Station d'Incinération Benniou")
        dlg.setFixedSize(320, 160)
        ly = QVBoxLayout(dlg)

        form_ly = QHBoxLayout()
        cb_mois = QComboBox()
        cb_mois.addItem("Tous les mois", 0)
        months_fr = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
        for idx, m_name in enumerate(months_fr, start=1):
            cb_mois.addItem(m_name, idx)
        
        cb_annee = QComboBox()
        current_year = QDate.currentDate().year()
        cb_annee.addItems([str(y) for y in range(current_year-2, current_year+3)])
        cb_annee.setCurrentText(str(current_year))

        form_ly.addWidget(QLabel("Mois:"))
        form_ly.addWidget(cb_mois)
        form_ly.addWidget(QLabel("Année:"))
        form_ly.addWidget(cb_annee)
        ly.addLayout(form_ly)

        btn_ok = QPushButton("Générer PDF")
        btn_ok.clicked.connect(dlg.accept)
        ly.addWidget(btn_ok)

        if dlg.exec():
            m_idx = cb_mois.currentData()
            m_name = cb_mois.currentText()
            y = int(cb_annee.currentText())

            rows = data_manager.banque.get_incinerations(m_idx, y)
            if not rows:
                QMessageBox.information(self, "Info", "Aucun enregistrement trouvé pour cette période.")
                return

            stats = data_manager.banque.get_incineration_stats(m_idx, y)

            path, _ = QFileDialog.getSaveFileName(self, "Enregistrer PDF", f"Etat_Incineration_Benniou_{y}.pdf", "PDF (*.pdf)")
            if not path:
                return

            from utils.pdf_generator import PdfGenerator
            gen = PdfGenerator()
            if gen.generate_incineration_pdf(path, m_name, y, rows, stats):
                QMessageBox.information(self, "Succès", "PDF Station Incinération généré avec succès!")
            else:
                QMessageBox.critical(self, "Erreur", "Erreur lors de la génération du PDF.")
