from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QColor, QFont
from database import data_manager

_sentinel = object()

class ProfitabiliteTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.month = None
        self.year = None
        self.current_summary = None
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        # Toolbar for action buttons
        toolbar_layout = QHBoxLayout()
        self.btn_export_pdf = QPushButton("🖨️ Exporter PDF (Mouvement Profitabilité)")
        self.btn_export_pdf.setCursor(Qt.PointingHandCursor)
        self.btn_export_pdf.setStyleSheet("""
            QPushButton {
                background-color: #007572;
                color: white;
                font-weight: bold;
                padding: 6px 15px;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #005a58;
            }
        """)
        self.btn_export_pdf.clicked.connect(self.export_pdf)
        toolbar_layout.addWidget(self.btn_export_pdf)
        toolbar_layout.addStretch()

        layout.addLayout(toolbar_layout)

        # Table for financial indicators
        self.tbl_profitabilite = QTableWidget()
        self.tbl_profitabilite.setColumnCount(2)
        self.tbl_profitabilite.setHorizontalHeaderLabels(["INDICATEUR FINANCIER", "VALEUR (DA / %)"])
        self.tbl_profitabilite.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl_profitabilite.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.tbl_profitabilite)

    def load_data(self, month=_sentinel, year=_sentinel):
        if month is not _sentinel:
            self.month = month
        if year is not _sentinel:
            self.year = year
            
        m = self.month
        y = self.year
        if not m or not y:
            m = QDate.currentDate().month() if not m else m
            y = QDate.currentDate().year() if not y else y
            
        summary = data_manager.fournisseurs.get_profitability_summary(m, y)
        self.current_summary = summary
        
        self.tbl_profitabilite.setRowCount(14)
        
        def set_metric_row(row_idx, label, val_num, is_bold=False, color_hex=None):
            lbl_item = QTableWidgetItem(label)
            val_str = f"{val_num:,.2f}" if isinstance(val_num, (int, float)) else str(val_num)
            val_item = QTableWidgetItem(val_str)
            
            if is_bold:
                f = lbl_item.font()
                f.setBold(True)
                lbl_item.setFont(f)
                val_item.setFont(f)
                
            if color_hex:
                lbl_item.setForeground(QColor(color_hex))
                val_item.setForeground(QColor(color_hex))
                
            self.tbl_profitabilite.setItem(row_idx, 0, lbl_item)
            self.tbl_profitabilite.setItem(row_idx, 1, val_item)

        set_metric_row(0, "PAIE ESTIMATION (Salaires)", summary['total_paie'])
        set_metric_row(1, "DEPENSES INTERNE (Caisse)", summary['total_dep_int'])
        
        for col in range(2):
            self.tbl_profitabilite.setItem(2, col, QTableWidgetItem(""))
            
        set_metric_row(3, "FOURNISSEURS + DEPENSES + PAIE (Total Charges)", summary['total_costs'], is_bold=True, color_hex="#c62828")
        
        for col in range(2):
            self.tbl_profitabilite.setItem(4, col, QTableWidgetItem(""))
            self.tbl_profitabilite.setItem(5, col, QTableWidgetItem(""))
            
        set_metric_row(6, "CA LAM (Caisse Ville & TPE)", summary['ca_lam'])
        set_metric_row(7, "CA C (Convention / Mutuelle)", summary['ca_c'])
        set_metric_row(8, "CA ST (Sous-Traitants)", summary['ca_st'])
        set_metric_row(9, "ENTREES SUPP (Coffre)", summary['entrees_supp'])
        set_metric_row(10, "Chiffre d'Affaires Total", summary['chiffre_affaire'], is_bold=True, color_hex="#1565c0")
        
        for col in range(2):
            self.tbl_profitabilite.setItem(11, col, QTableWidgetItem(""))
            
        prof_color = "#2e7d32" if summary['profitability'] >= 0 else "#c62828"
        set_metric_row(12, "Profitabilité Nette : (CA+ST)-(FR+DEP+PAIE)", summary['profitability'], is_bold=True, color_hex=prof_color)
        set_metric_row(13, "% Profitabilité / Chiffre d'Affaires", f"{summary['profitability_pct']:.2f} %", is_bold=True, color_hex=prof_color)

    def export_pdf(self):
        if not self.current_summary:
            QMessageBox.warning(self, "Attention", "Veuillez charger les données avant l'exportation.")
            return

        m = self.month or QDate.currentDate().month()
        y = self.year or QDate.currentDate().year()
        months = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
        m_name = months[m - 1] if 1 <= m <= 12 else str(m)

        path, _ = QFileDialog.getSaveFileName(self, "Enregistrer Mouvement Profitabilité PDF", f"Mouvement_Profitabilite_{m:02d}_{y}.pdf", "PDF (*.pdf)")
        if not path:
            return

        from utils.pdf_generator import PdfGenerator
        gen = PdfGenerator()
        if gen.generate_profitabilite_pdf(path, m_name, y, self.current_summary):
            QMessageBox.information(self, "Succès", "Rapport Mouvement Profitabilité généré avec succès!")
        else:
            QMessageBox.critical(self, "Erreur", "Erreur lors de la génération du PDF.")
