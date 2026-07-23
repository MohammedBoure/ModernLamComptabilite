from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, 
    QTableWidget, QTableWidgetItem, QHeaderView, QPushButton,
    QLabel, QComboBox, QGroupBox, QTabWidget, QFormLayout, QAbstractItemView
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont, QColor
from database import data_manager
from ui.table_helper import make_table_editable
from ui.caisse.dialogs import MouvementCaisseDialog, MouvementCoffreDialog

class CaisseCoffreTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        
        # --- Top Bar Section ---
        top_bar_layout = QHBoxLayout()
        
        lbl_month = QLabel("Mois:")
        self.cb_month = QComboBox()
        self.cb_month.addItems(["Tous", "Janvier", "Février", "Mars", "Avril", "Mai", "Juin", 
                               "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"])
        
        lbl_year = QLabel("Année:")
        self.cb_year = QComboBox()
        current_year = QDate.currentDate().year()
        self.cb_year.addItems(["Tous"] + [str(y) for y in range(current_year - 2, current_year + 5)])
        
        # Set defaults
        self.cb_month.setCurrentIndex(QDate.currentDate().month())
        self.cb_year.setCurrentText(str(current_year))
        
        self.cb_month.currentIndexChanged.connect(self.load_data)
        self.cb_year.currentTextChanged.connect(self.load_data)
        
        top_bar_layout.addWidget(lbl_month)
        top_bar_layout.addWidget(self.cb_month)
        top_bar_layout.addWidget(lbl_year)
        top_bar_layout.addWidget(self.cb_year)
        top_bar_layout.addStretch()
        
        main_layout.addLayout(top_bar_layout)
        
        # --- Sub Tabs ---
        self.sub_tabs = QTabWidget()
        
        # 1. Tab: MOUVEMENT CAISSE
        tab_caisse = QWidget()
        caisse_layout = QVBoxLayout(tab_caisse)
        
        self.tbl_caisse = QTableWidget()
        self.tbl_caisse.setColumnCount(9)
        self.tbl_caisse.setHorizontalHeaderLabels(["DATE", "Caisse CV", "Caisse C", "TPE", "Dépenses", "Remboursement", "Convention Mutuelle", "Sous-Traitants", "Total"])
        self.tbl_caisse.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl_caisse.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tbl_caisse.setSelectionBehavior(QAbstractItemView.SelectRows)
        
        # Setup toolbar
        self.toolbar_caisse = make_table_editable(
            self.tbl_caisse, "Mouvement_Caisse", "date_mouvement",
            lambda r: self.tbl_caisse.item(r, 0).text() if self.tbl_caisse.item(r, 0) else None,
            MouvementCaisseDialog, self.load_data, self,
            add_callback=self.add_caisse_mvt,
            add_label="Ajouter"
        )
        caisse_layout.addWidget(self.toolbar_caisse)
        caisse_layout.addWidget(self.tbl_caisse)
        
        self.tbl_caisse_summary = QTableWidget()
        self.tbl_caisse_summary.setColumnCount(9)
        self.tbl_caisse_summary.horizontalHeader().setVisible(False)
        self.tbl_caisse_summary.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl_caisse_summary.verticalHeader().setVisible(False)
        self.tbl_caisse_summary.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tbl_caisse_summary.setRowCount(4)
        self.tbl_caisse_summary.setFixedHeight(120)
        self.tbl_caisse_summary.setStyleSheet("QTableWidget { background-color: #e3f2fd; border: 1px solid #cfd8dc; border-bottom: none; border-top-left-radius: 8px; border-top-right-radius: 8px; border-bottom-left-radius: 0px; border-bottom-right-radius: 0px; }")
        self.tbl_caisse_summary.setSelectionMode(QAbstractItemView.NoSelection)
        caisse_layout.addWidget(self.tbl_caisse_summary)
        
        self.sub_tabs.addTab(tab_caisse, "MOUVEMENT CAISSE")
        
        # 2. Tab: RÉSUMÉ COFFRE
        tab_resume = QWidget()
        resume_layout = QVBoxLayout(tab_resume)
        
        form_group = QGroupBox("MOUVEMENT COFFRE (RÉSUMÉ)")
        form_group.setStyleSheet(
            "QGroupBox { font-weight: bold; font-size: 14px; border: 1px solid #cfd8dc; border-bottom: none; border-top-left-radius: 8px; border-top-right-radius: 8px; border-bottom-left-radius: 0px; border-bottom-right-radius: 0px; }"
        )
        form_layout = QFormLayout(form_group)
        form_layout.setLabelAlignment(Qt.AlignRight)
        
        self.lbl_coffre_total_tous_mois = QLabel("0.00")
        self.lbl_coffre_total_tous_mois.setFont(QFont("Arial", 18, QFont.Bold))
        self.lbl_coffre_total_tous_mois.setStyleSheet("color: #2e7d32; background-color: #e8f5e9; padding: 5px; border-radius: 5px;")
        
        self.lbl_coffre_net = QLabel("0.00")
        self.lbl_coffre_net.setFont(QFont("Arial", 16, QFont.Bold))
        self.lbl_coffre_net.setStyleSheet("color: #d32f2f;")
        
        self.lbl_ca_lam = QLabel("0.00")
        self.lbl_ca_conv = QLabel("0.00")
        self.lbl_ca_st = QLabel("0.00")
        self.lbl_ca_supp = QLabel("0.00")
        self.lbl_ca_globale = QLabel("0.00")
        self.lbl_ca_globale.setFont(QFont("Arial", 14, QFont.Bold))
        self.lbl_ca_globale.setStyleSheet("color: #1976d2;")
        
        form_layout.addRow(QLabel("<h3 style='margin:0; color:#2e7d32;'>Coffre Stratégique<br><small style='font-size:12px;font-weight:normal;color:#000;'>(Mois sélectionné)</small>:</h3>"), self.lbl_coffre_total_tous_mois)
        form_layout.addRow(QLabel("<b>Coffre Net Réel (Filtre):</b>"), self.lbl_coffre_net)
        form_layout.addRow(QLabel(""), QLabel("")) # Spacer
        form_layout.addRow("Chiffre d'affaire LAM:", self.lbl_ca_lam)
        form_layout.addRow("Chiffre d'affaire Convention:", self.lbl_ca_conv)
        form_layout.addRow("Chiffre d'affaire ST:", self.lbl_ca_st)
        form_layout.addRow("Chiffre d'Affaire Entrées Supplémentaires:", self.lbl_ca_supp)
        form_layout.addRow(QLabel("<b>Chiffre D'affaire Globale:</b>"), self.lbl_ca_globale)
        
        self.lbl_prof_paie = QLabel("0.00")
        self.lbl_prof_dep = QLabel("0.00")
        
        self.lbl_prof_costs = QLabel("0.00")
        self.lbl_prof_costs.setFont(QFont("Arial", 12, QFont.Bold))
        self.lbl_prof_costs.setStyleSheet("color: #c62828;")
        
        self.lbl_prof_val = QLabel("0.00")
        self.lbl_prof_val.setFont(QFont("Arial", 14, QFont.Bold))
        
        self.lbl_prof_pct = QLabel("0.00 %")
        self.lbl_prof_pct.setFont(QFont("Arial", 14, QFont.Bold))

        form_layout.addRow(QLabel(""), QLabel("")) # Spacer
        form_layout.addRow(QLabel("<h3 style='margin:0; color:#37474f;'>--- PROFITABILITÉ ---</h3>"), QLabel(""))
        form_layout.addRow("Paie (Estimation):", self.lbl_prof_paie)
        form_layout.addRow("Dépenses Interne:", self.lbl_prof_dep)
        form_layout.addRow(QLabel("<b>Total (Fournisseurs + Dépenses + Paie):</b>"), self.lbl_prof_costs)
        form_layout.addRow(QLabel("<b>Profitabilité Nette:</b>"), self.lbl_prof_val)
        form_layout.addRow(QLabel("<b>Marge (%):</b>"), self.lbl_prof_pct)
        
        resume_layout.addWidget(form_group)
        
        resume_layout.addStretch()
        
        self.sub_tabs.addTab(tab_resume, "RÉSUMÉ COFFRE")
        
        # 3. Tab: ENTRÉES COFFRE
        tab_entrees = QWidget()
        entrees_layout = QVBoxLayout(tab_entrees)
        
        self.tbl_entrees = QTableWidget()
        self.tbl_entrees.setColumnCount(3)
        self.tbl_entrees.setHorizontalHeaderLabels(["Date", "Montant", "Détail"])
        self.tbl_entrees.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl_entrees.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tbl_entrees.setSelectionBehavior(QAbstractItemView.SelectRows)
        
        self.toolbar_entrees = make_table_editable(
            self.tbl_entrees, "Mouvement_Coffre", "id_transaction",
            lambda r: self.tbl_entrees.item(r, 0).data(Qt.UserRole) if self.tbl_entrees.item(r, 0) else None,
            MouvementCoffreDialog, self.load_data, self,
            add_callback=self.add_coffre_mvt_entree,
            add_label="Ajouter"
        )
        entrees_layout.addWidget(self.toolbar_entrees)
        entrees_layout.addWidget(self.tbl_entrees)
        
        self.sub_tabs.addTab(tab_entrees, "ENTRÉES COFFRE")
        
        # 4. Tab: SORTIES COFFRE
        tab_sorties = QWidget()
        sorties_layout = QVBoxLayout(tab_sorties)
        
        self.tbl_sorties = QTableWidget()
        self.tbl_sorties.setColumnCount(3)
        self.tbl_sorties.setHorizontalHeaderLabels(["Date", "Désignation", "Montant"])
        self.tbl_sorties.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl_sorties.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tbl_sorties.setSelectionBehavior(QAbstractItemView.SelectRows)
        
        self.toolbar_sorties = make_table_editable(
            self.tbl_sorties, "Mouvement_Coffre", "id_transaction",
            lambda r: self.tbl_sorties.item(r, 0).data(Qt.UserRole) if self.tbl_sorties.item(r, 0) else None,
            MouvementCoffreDialog, self.load_data, self,
            add_callback=self.add_coffre_mvt_sortie,
            add_label="Ajouter"
        )
        sorties_layout.addWidget(self.toolbar_sorties)
        sorties_layout.addWidget(self.tbl_sorties)
        
        self.sub_tabs.addTab(tab_sorties, "SORTIES COFFRE")
        
        # 5. Tab: DÉPENSES ACHATS
        from ui.fournisseurs.tabs.achats_tab import AchatsTab
        self.tab_achats = AchatsTab(self)
        self.sub_tabs.addTab(self.tab_achats, "Dépenses Achats")
        
        main_layout.addWidget(self.sub_tabs)

    def set_permissions(self, allowed_tabs):
        if allowed_tabs is None:
            return
            
        for i in range(self.sub_tabs.count() - 1, -1, -1):
            tab_text = self.sub_tabs.tabText(i)
            if tab_text not in allowed_tabs:
                self.sub_tabs.removeTab(i)

    def get_filter_dates(self):
        month = self.cb_month.currentIndex()
        year = self.cb_year.currentText()
        if month == 0 or year == "Tous":
            return None, None
        return month, int(year)

    def add_caisse_mvt(self):
        from ui.caisse.dialogs import MouvementCaisseDialog
        dlg = MouvementCaisseDialog(self)
        if dlg.exec():
            self.load_data()

    def add_coffre_mvt_entree(self):
        from ui.caisse.dialogs import MouvementCoffreDialog
        dlg = MouvementCoffreDialog(self, default_type="ENTREE")
        if dlg.exec():
            self.load_data()

    def add_coffre_mvt_sortie(self):
        from ui.caisse.dialogs import MouvementCoffreDialog
        dlg = MouvementCoffreDialog(self, default_type="SORTIE")
        if dlg.exec():
            self.load_data()

    def load_data(self):
        month, year = self.get_filter_dates()
        
        # 1. Load Mouvement Caisse
        data_caisse = data_manager.caisse.get_caisse_movements(month, year)
        self.tbl_caisse.setRowCount(len(data_caisse))
        
        totals = [0.0] * 8
        mins = [float('inf')] * 8
        maxs = [float('-inf')] * 8
        counts = [0] * 8
        moyenne_sums = [0.0] * 8
        
        for i, row in enumerate(data_caisse):
            date_obj = row['date_mouvement']
            
            def safe_float(val):
                return float(val) if val is not None and str(val).strip() != "" else None
                
            c_cv = safe_float(row['caisse_cv'])
            c_c = safe_float(row['caisse_c'])
            tpe = safe_float(row['tpe'])
            dep = safe_float(row['depenses'])
            remb = safe_float(row['remboursement'])
            conv = safe_float(row['convention'])
            st = safe_float(row['sous_traitants'])
            
            row_vals = [c_cv, c_c, tpe, dep, remb, conv, st]
            total = sum([v for v in row_vals if v is not None])
            
            self.tbl_caisse.setItem(i, 0, QTableWidgetItem(str(date_obj)))
            for col_idx, val in enumerate(row_vals):
                item = QTableWidgetItem(f"{val:.2f}" if val is not None else "0.00")
                self.tbl_caisse.setItem(i, col_idx + 1, item)
            
            item_total = QTableWidgetItem(f"{total:.2f}")
            font = item_total.font()
            font.setBold(True)
            item_total.setFont(font)
            self.tbl_caisse.setItem(i, 8, item_total)
            
            # Statistics calculation (ignoring Fridays, None, and 0.0 values)
            if isinstance(date_obj, str):
                from datetime import datetime
                try:
                    date_obj = datetime.strptime(date_obj, "%Y-%m-%d").date()
                except ValueError:
                    pass
            is_friday = getattr(date_obj, "weekday", lambda: 0)() == 4
            
            stat_vals = row_vals + [total]
            for col_idx, val in enumerate(stat_vals):
                if val is not None:
                    totals[col_idx] += val
                    # Statistics exclude Friday and 0.0 / empty values
                    if not is_friday and val != 0.0:
                        if val < mins[col_idx]: 
                            mins[col_idx] = val
                        if val > maxs[col_idx]: 
                            maxs[col_idx] = val
                        moyenne_sums[col_idx] += val
                        counts[col_idx] += 1
                    
        # Populate summary table
        labels = ["Total", "Min (-Ven)", "Max (-Ven)", "Moyenne (-Ven)"]
        for r, label in enumerate(labels):
            item = QTableWidgetItem(label)
            font = item.font()
            font.setBold(True)
            if r == 0: item.setForeground(QColor("#d32f2f"))
            item.setFont(font)
            self.tbl_caisse_summary.setItem(r, 0, item)
            
            for c in range(8):
                if r == 0:
                    val = totals[c]
                elif r == 1:
                    val = mins[c] if counts[c] > 0 and mins[c] != float('inf') else 0.0
                elif r == 2:
                    val = maxs[c] if counts[c] > 0 and maxs[c] != float('-inf') else 0.0
                elif r == 3:
                    val = moyenne_sums[c] / counts[c] if counts[c] > 0 else 0.0
                
                val_item = QTableWidgetItem(f"{val:.2f}")
                if r == 0:
                    val_item.setFont(font)
                    val_item.setForeground(QColor("#d32f2f"))
                self.tbl_caisse_summary.setItem(r, c + 1, val_item)
                
        # 2. Load Résumé Coffre
        summary_selected = data_manager.caisse.get_coffre_summary(month, year)
        self.lbl_coffre_total_tous_mois.setText(f"{summary_selected['coffre_net']:,.2f} DZD")

        summary = data_manager.caisse.get_coffre_summary(month, year)
        self.lbl_coffre_net.setText(f"{summary['coffre_net']:,.2f} DZD")
        self.lbl_ca_lam.setText(f"{summary['ca_lam']:,.2f}")
        self.lbl_ca_conv.setText(f"{summary['ca_convention']:,.2f}")
        self.lbl_ca_st.setText(f"{summary['ca_st']:,.2f}")
        self.lbl_ca_supp.setText(f"{summary['ca_supp']:,.2f}")
        self.lbl_ca_globale.setText(f"{summary['global']:,.2f}")

        # 3. Load Entrées & Sorties (Mouvement Coffre)
        data_coffre = data_manager.caisse.get_coffre_movements(month, year)
        
        entrees = [d for d in data_coffre if d['type_operation'] == 'ENTREE']
        sorties = [d for d in data_coffre if d['type_operation'] == 'SORTIE']
        
        # Entrées (now showing all ENTREE instead of only ENTREES_SUPP)
        self.tbl_entrees.setRowCount(len(entrees))
        for i, row in enumerate(entrees):
            item_date = QTableWidgetItem(str(row['date_transaction']))
            item_date.setData(Qt.UserRole, row['id_transaction'])
            self.tbl_entrees.setItem(i, 0, item_date)
            self.tbl_entrees.setItem(i, 1, QTableWidgetItem(f"{row['montant']:.2f}"))
            self.tbl_entrees.setItem(i, 2, QTableWidgetItem(str(row['designation'])))
            
        # Sorties
        self.tbl_sorties.setRowCount(len(sorties))
        for i, row in enumerate(sorties):
            item_date = QTableWidgetItem(str(row['date_transaction']))
            item_date.setData(Qt.UserRole, row['id_transaction'])
            self.tbl_sorties.setItem(i, 0, item_date)
            self.tbl_sorties.setItem(i, 1, QTableWidgetItem(str(row['designation'])))
            self.tbl_sorties.setItem(i, 2, QTableWidgetItem(f"{row['montant']:.2f}"))

        # 4. Load Achats
        self.tab_achats.load_data(month, year)
        
        # 5. Load Profitabilite in Resume tab
        prof_summary = data_manager.fournisseurs.get_profitability_summary(month, year)
        self.lbl_prof_paie.setText(f"{prof_summary['total_paie']:,.2f}")
        self.lbl_prof_dep.setText(f"{prof_summary['total_dep_int']:,.2f}")
        self.lbl_prof_costs.setText(f"{prof_summary['total_costs']:,.2f}")
        
        prof_color = "#2e7d32" if prof_summary['profitability'] >= 0 else "#c62828"
        self.lbl_prof_val.setText(f"{prof_summary['profitability']:,.2f}")
        self.lbl_prof_val.setStyleSheet(f"color: {prof_color};")
        
        self.lbl_prof_pct.setText(f"{prof_summary['profitability_pct']:.2f} %")
        self.lbl_prof_pct.setStyleSheet(f"color: {prof_color};")
