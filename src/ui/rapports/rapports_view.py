import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QTabWidget,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
    QMessageBox, QFileDialog, QScrollArea, QProgressBar
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont, QColor

from database import data_manager
from utils.pdf_generator import PdfGenerator


def adjust_table_height(table_widget):
    """
    Expands a QTableWidget vertically so all rows are visible without internal scrollbars.
    """
    table_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    table_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    table_widget.resizeRowsToContents()
    
    header_h = table_widget.horizontalHeader().height() or 32
    rows_h = sum(table_widget.rowHeight(r) for r in range(table_widget.rowCount()))
    frame_h = table_widget.frameWidth() * 2
    
    total_h = header_h + rows_h + frame_h + 10
    table_widget.setFixedHeight(max(total_h, 60))


class RapportsView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.on_filter_changed()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(12)

        # ----------------------------------------------------
        # 1. Top Filter & Toolbar (Flat Layout without heavy containers)
        # ----------------------------------------------------
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 5)
        top_layout.setSpacing(12)

        lbl_title = QLabel("📊 Rapports Financiers & Comptabilité Mensuelle")
        lbl_title.setFont(QFont("Arial", 12, QFont.Bold))
        lbl_title.setStyleSheet("color: #007572;")

        top_layout.addWidget(lbl_title)
        top_layout.addStretch()

        lbl_month = QLabel("Mois:")
        lbl_month.setFont(QFont("Arial", 10, QFont.Bold))
        self.cb_month = QComboBox()
        self.cb_month.addItems([
            "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
            "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"
        ])

        lbl_year = QLabel("Année:")
        lbl_year.setFont(QFont("Arial", 10, QFont.Bold))
        self.cb_year = QComboBox()
        current_year = QDate.currentDate().year()
        self.cb_year.addItems([str(y) for y in range(current_year - 2, current_year + 5)])

        self.cb_month.setCurrentIndex(QDate.currentDate().month() - 1)
        self.cb_year.setCurrentText(str(current_year))

        self.cb_month.currentIndexChanged.connect(self.on_filter_changed)
        self.cb_year.currentTextChanged.connect(self.on_filter_changed)

        top_layout.addWidget(lbl_month)
        top_layout.addWidget(self.cb_month)
        top_layout.addWidget(lbl_year)
        top_layout.addWidget(self.cb_year)

        self.btn_refresh = QPushButton("Actualiser")
        self.btn_refresh.setStyleSheet("""
            QPushButton {
                background-color: #1976d2;
                color: white;
                font-weight: bold;
                padding: 6px 14px;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #1565c0; }
        """)
        self.btn_refresh.clicked.connect(self.on_filter_changed)

        self.btn_export_pdf = QPushButton("🖨️ Exporter PDF Rapport Comptabilité")
        self.btn_export_pdf.setStyleSheet("""
            QPushButton {
                background-color: #007572;
                color: white;
                font-weight: bold;
                padding: 6px 14px;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #005a58; }
        """)
        self.btn_export_pdf.clicked.connect(self.export_compta_pdf)

        top_layout.addWidget(self.btn_refresh)
        top_layout.addWidget(self.btn_export_pdf)

        main_layout.addLayout(top_layout)

        # ----------------------------------------------------
        # 2. Tab Widget
        # ----------------------------------------------------
        self.tabs = QTabWidget()

        # Tab 1: Rapport de Comptabilité Mensuel
        self.tab_compta = QWidget()
        self.setup_compta_tab()
        self.tabs.addTab(self.tab_compta, "📄 Rapport de Comptabilité Mensuel")

        # Tab 2: Rapport Analytique des Achats
        self.tab_analytic = QWidget()
        self.setup_analytic_tab()
        self.tabs.addTab(self.tab_analytic, "📈 Rapport Analytique des Achats")

        main_layout.addWidget(self.tabs)

    def setup_compta_tab(self):
        layout = QVBoxLayout(self.tab_compta)
        layout.setContentsMargins(0, 0, 0, 0)

        # Single Master Scroll Area for the whole page (No nested box containers!)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        container = QWidget()
        c_layout = QVBoxLayout(container)
        c_layout.setContentsMargins(10, 10, 10, 10)
        c_layout.setSpacing(18)

        # --- SECTION I: RAPPORT DES REVENUS ---
        lbl_rev = QLabel("I. RAPPORT DES REVENUS")
        lbl_rev.setStyleSheet("font-size: 14px; font-weight: bold; color: #007572; border-bottom: 2px solid #007572; padding-bottom: 4px;")
        c_layout.addWidget(lbl_rev)

        self.tbl_revenus = QTableWidget()
        self.tbl_revenus.setColumnCount(3)
        self.tbl_revenus.setHorizontalHeaderLabels(["N°", "CATÉGORIE / DÉTAILS", "MONTANT HORS TAXE (DA)"])
        self.tbl_revenus.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl_revenus.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tbl_revenus.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tbl_revenus.setAlternatingRowColors(True)
        c_layout.addWidget(self.tbl_revenus)

        # --- SECTION II: RAPPORT DES DÉPENSES ---
        lbl_dep = QLabel("II. RAPPORT DES DÉPENSES")
        lbl_dep.setStyleSheet("font-size: 14px; font-weight: bold; color: #b91c1c; border-bottom: 2px solid #b91c1c; padding-bottom: 4px;")
        c_layout.addWidget(lbl_dep)

        self.tbl_depenses = QTableWidget()
        self.tbl_depenses.setColumnCount(4)
        self.tbl_depenses.setHorizontalHeaderLabels(["N°", "CATÉGORIE & DÉTAILS", "MONTANT PAYÉ (DA)", "MONTANT DETTE (DA)"])
        self.tbl_depenses.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl_depenses.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tbl_depenses.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tbl_depenses.setAlternatingRowColors(True)
        c_layout.addWidget(self.tbl_depenses)

        # --- SECTION III: RÉSULTAT FINAL & PROFITABILITÉ ---
        lbl_res = QLabel("III. RÉSULTAT FINAL & PROFITABILITÉ")
        lbl_res.setStyleSheet("font-size: 14px; font-weight: bold; color: #1e293b; border-bottom: 2px solid #1e293b; padding-bottom: 4px;")
        c_layout.addWidget(lbl_res)

        self.tbl_resultat = QTableWidget()
        self.tbl_resultat.setColumnCount(4)
        self.tbl_resultat.setHorizontalHeaderLabels(["N°", "DÉSIGNATION", "CRÉDIT (DA)", "DÉBIT (DA)"])
        self.tbl_resultat.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl_resultat.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tbl_resultat.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tbl_resultat.setAlternatingRowColors(True)
        c_layout.addWidget(self.tbl_resultat)

        c_layout.addStretch()
        scroll.setWidget(container)
        layout.addWidget(scroll)

    def setup_analytic_tab(self):
        layout = QVBoxLayout(self.tab_analytic)
        layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")

        container = QWidget()
        c_layout = QVBoxLayout(container)
        c_layout.setContentsMargins(10, 10, 10, 10)
        c_layout.setSpacing(15)

        # Flat header bar without heavy container border
        c_ly = QHBoxLayout()
        self.lbl_tot_dep = QLabel("Charges Globales Mensuelles: 0.00 DA")
        self.lbl_tot_dep.setStyleSheet("font-size: 14px; font-weight: bold; color: #b91c1c; padding: 5px 0;")
        c_ly.addWidget(self.lbl_tot_dep)
        c_ly.addStretch()

        c_layout.addLayout(c_ly)

        self.tbl_analytic = QTableWidget()
        self.tbl_analytic.setColumnCount(4)
        self.tbl_analytic.setHorizontalHeaderLabels(["POSTE / CATÉGORIE DE DÉPENSE", "MONTANT (DA)", "PART (%)", "RÉPARTITION ANALYTIQUE"])
        self.tbl_analytic.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl_analytic.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.tbl_analytic.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tbl_analytic.setAlternatingRowColors(True)

        c_layout.addWidget(self.tbl_analytic)
        c_layout.addStretch()

        scroll.setWidget(container)
        layout.addWidget(scroll)

    def on_filter_changed(self):
        month = self.cb_month.currentIndex() + 1
        year = int(self.cb_year.currentText())

        report_data = data_manager.rapports.get_rapport_comptabilite(month, year)
        self.current_report = report_data

        self._render_compta_tab(report_data)
        self._render_analytic_tab(report_data)

    def _render_compta_tab(self, data):
        # 1. Revenus Table
        rev = data['revenus']
        st_items = rev['sous_traitance_items']
        supp_items = rev['supp_items']

        row_count = 1 + len(st_items) + len(supp_items) + 1
        self.tbl_revenus.setRowCount(row_count)

        r_idx = 0
        # Ville
        item01 = QTableWidgetItem("01")
        item01.setTextAlignment(Qt.AlignCenter)
        self.tbl_revenus.setItem(r_idx, 0, item01)
        self.tbl_revenus.setItem(r_idx, 1, QTableWidgetItem("Les Revenus de Clientèle Ville"))
        item_v = QTableWidgetItem(f"{rev['ville']:,.2f}")
        item_v.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.tbl_revenus.setItem(r_idx, 2, item_v)
        r_idx += 1

        # Sous-traitance
        for st in st_items:
            item_st = QTableWidgetItem("02")
            item_st.setTextAlignment(Qt.AlignCenter)
            self.tbl_revenus.setItem(r_idx, 0, item_st)
            self.tbl_revenus.setItem(r_idx, 1, QTableWidgetItem(f"Sous-Traitance: {st['nom_partenaire']}"))
            item_val = QTableWidgetItem(f"{float(st['total'] or 0):,.2f}")
            item_val.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.tbl_revenus.setItem(r_idx, 2, item_val)
            r_idx += 1

        # Supp
        for sp in supp_items:
            item_sp = QTableWidgetItem("03")
            item_sp.setTextAlignment(Qt.AlignCenter)
            self.tbl_revenus.setItem(r_idx, 0, item_sp)
            self.tbl_revenus.setItem(r_idx, 1, QTableWidgetItem(f"Revenus Supplémentaires: {sp['designation']}"))
            item_val = QTableWidgetItem(f"{float(sp['total'] or 0):,.2f}")
            item_val.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.tbl_revenus.setItem(r_idx, 2, item_val)
            r_idx += 1

        # Total CA
        item_lbl = QTableWidgetItem("04. Chiffre d'Affaires Mensuel Total")
        item_lbl.setFont(QFont("Arial", -1, QFont.Bold))
        item_val = QTableWidgetItem(f"{rev['chiffre_affaires']:,.2f}")
        item_val.setFont(QFont("Arial", -1, QFont.Bold))
        item_val.setForeground(QColor("#007572"))
        item_val.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

        item04 = QTableWidgetItem("04")
        item04.setTextAlignment(Qt.AlignCenter)
        self.tbl_revenus.setItem(r_idx, 0, item04)
        self.tbl_revenus.setItem(r_idx, 1, item_lbl)
        self.tbl_revenus.setItem(r_idx, 2, item_val)

        adjust_table_height(self.tbl_revenus)

        # 2. Dépenses Table
        dep = data['depenses']
        cats = dep['categories']
        
        self.tbl_depenses.setRowCount(len(cats) + 2)
        d_idx = 0
        for cat_name, cat_info in cats.items():
            item_c = QTableWidgetItem(cat_name)
            item_paye = QTableWidgetItem(f"{cat_info['paye']:,.2f}")
            item_paye.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            item_dette = QTableWidgetItem(f"{cat_info['dette']:,.2f}")
            item_dette.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

            item_num = QTableWidgetItem(f"{d_idx+1:02d}")
            item_num.setTextAlignment(Qt.AlignCenter)

            self.tbl_depenses.setItem(d_idx, 0, item_num)
            self.tbl_depenses.setItem(d_idx, 1, item_c)
            self.tbl_depenses.setItem(d_idx, 2, item_paye)
            self.tbl_depenses.setItem(d_idx, 3, item_dette)
            d_idx += 1

        # Totals
        item_t_lbl = QTableWidgetItem("Charges Totales Mensuelles")
        item_t_lbl.setFont(QFont("Arial", -1, QFont.Bold))
        item_t_paye = QTableWidgetItem(f"{dep['total_paye']:,.2f}")
        item_t_paye.setFont(QFont("Arial", -1, QFont.Bold))
        item_t_paye.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        item_t_dette = QTableWidgetItem(f"{dep['total_dette']:,.2f}")
        item_t_dette.setFont(QFont("Arial", -1, QFont.Bold))
        item_t_dette.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.tbl_depenses.setItem(d_idx, 1, item_t_lbl)
        self.tbl_depenses.setItem(d_idx, 2, item_t_paye)
        self.tbl_depenses.setItem(d_idx, 3, item_dette)
        d_idx += 1

        item_g_lbl = QTableWidgetItem("TOTAL DÉPENSES GLOBAL (Payé + Dette)")
        item_g_lbl.setFont(QFont("Arial", -1, QFont.Bold))
        item_g_val = QTableWidgetItem(f"{dep['total_global']:,.2f}")
        item_g_val.setFont(QFont("Arial", -1, QFont.Bold))
        item_g_val.setForeground(QColor("#b91c1c"))
        item_g_val.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.tbl_depenses.setItem(d_idx, 1, item_g_lbl)
        self.tbl_depenses.setItem(d_idx, 2, item_g_val)

        adjust_table_height(self.tbl_depenses)

        # 3. Résultat Final Table
        res = data['resultat']
        self.tbl_resultat.setRowCount(7)

        def set_res_row(row, num, title, credit=None, debit=None, bold=False, color=None):
            item_n = QTableWidgetItem(num)
            item_n.setTextAlignment(Qt.AlignCenter)
            self.tbl_resultat.setItem(row, 0, item_n)
            
            it_t = QTableWidgetItem(title)
            it_c = QTableWidgetItem(f"{credit:,.2f}" if credit is not None else "-")
            it_c.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            it_d = QTableWidgetItem(f"{debit:,.2f}" if debit is not None else "-")
            it_d.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            
            if bold:
                f = it_t.font()
                f.setBold(True)
                it_t.setFont(f)
                it_c.setFont(f)
                it_d.setFont(f)
            if color:
                it_t.setForeground(QColor(color))
                it_c.setForeground(QColor(color))
                it_d.setForeground(QColor(color))

            self.tbl_resultat.setItem(row, 1, it_t)
            self.tbl_resultat.setItem(row, 2, it_c)
            self.tbl_resultat.setItem(row, 3, it_d)

        set_res_row(0, "01", "Les Revenus de Clientèle Ville", credit=rev['ville'])
        set_res_row(1, "02", "Sous-Traitance", credit=rev['total_st'])
        set_res_row(2, "03", "Les Revenus Supplémentaires", credit=rev['total_supp'])
        set_res_row(3, "04", "Charges Totales Globales", debit=dep['total_global'], bold=True, color="#b91c1c")
        
        prof_c = "#15803d" if res['profitabilite_nette'] >= 0 else "#b91c1c"
        set_res_row(4, "05", "Profitabilité Nette Mensuelle", credit=res['profitabilite_nette'] if res['profitabilite_nette'] >= 0 else None, debit=abs(res['profitabilite_nette']) if res['profitabilite_nette'] < 0 else None, bold=True, color=prof_c)
        set_res_row(5, "06", "Les Investissements", debit=res['investissements'])
        set_res_row(6, "07", "Profitabilité Nette après Investissements", credit=res['profitabilite_apres_invest'] if res['profitabilite_apres_invest'] >= 0 else None, debit=abs(res['profitabilite_apres_invest']) if res['profitabilite_apres_invest'] < 0 else None, bold=True, color=prof_c)

        adjust_table_height(self.tbl_resultat)

    def _render_analytic_tab(self, data):
        dep = data['depenses']
        cats = dep['categories']
        tot_global = dep['total_global']

        self.lbl_tot_dep.setText(f"Charges Globales Mensuelles: {tot_global:,.2f} DA")

        self.tbl_analytic.setRowCount(len(cats))
        for row_idx, (cat_name, cat_info) in enumerate(cats.items()):
            montant = cat_info['total']
            pct = (montant / tot_global * 100.0) if tot_global > 0 else 0.0

            item_name = QTableWidgetItem(cat_name)
            item_montant = QTableWidgetItem(f"{montant:,.2f} DA")
            item_montant.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            item_montant.setFont(QFont("Arial", -1, QFont.Bold))
            item_pct = QTableWidgetItem(f"{pct:.2f} %")
            item_pct.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            item_pct.setFont(QFont("Arial", -1, QFont.Bold))

            # Progress bar for visual percentage
            pbar = QProgressBar()
            pbar.setRange(0, 100)
            pbar.setValue(int(pct))
            pbar.setTextVisible(True)
            pbar.setStyleSheet("QProgressBar { text-align: center; font-weight: bold; } QProgressBar::chunk { background-color: #007572; }")

            self.tbl_analytic.setItem(row_idx, 0, item_name)
            self.tbl_analytic.setItem(row_idx, 1, item_montant)
            self.tbl_analytic.setItem(row_idx, 2, item_pct)
            self.tbl_analytic.setCellWidget(row_idx, 3, pbar)

        adjust_table_height(self.tbl_analytic)

    def export_compta_pdf(self):
        if not hasattr(self, 'current_report'):
            return

        m = self.cb_month.currentIndex() + 1
        y = int(self.cb_year.currentText())
        m_name = self.cb_month.currentText()

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Enregistrer le Rapport de Comptabilité PDF", 
            f"Rapport_Comptabilite_{m_name}_{y}.pdf", "Fichiers PDF (*.pdf)"
        )
        if not file_path:
            return

        pdf_gen = PdfGenerator()
        pdf_gen.generate_rapport_comptabilite_pdf(file_path, m_name, y, self.current_report)

        QMessageBox.information(self, "Exportation Réussie", f"Le Rapport de Comptabilité a été généré avec succès :\n{file_path}")
