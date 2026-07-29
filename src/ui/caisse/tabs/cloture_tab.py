from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, 
    QTableWidget, QTableWidgetItem, QHeaderView, QPushButton,
    QLabel, QComboBox, QGroupBox, QTabWidget, QInputDialog, QMessageBox
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont, QColor
from database import data_manager
from ui.table_helper import make_table_editable
from ui.caisse.dialogs import ClotureCaisseDialog

class ClotureCaisseTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        
        # --- Filter Section ---
        filter_layout = QHBoxLayout()
        
        lbl_month = QLabel("Mois:")
        self.cb_month = QComboBox()
        self.cb_month.addItems(["Tous", "Janvier", "Février", "Mars", "Avril", "Mai", "Juin", 
                               "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"])
        
        lbl_year = QLabel("Année:")
        self.cb_year = QComboBox()
        current_year = QDate.currentDate().year()
        self.cb_year.addItems(["Tous"] + [str(y) for y in range(current_year - 2, current_year + 5)])
        
        # Set defaults to current month/year
        self.cb_month.setCurrentIndex(QDate.currentDate().month())
        self.cb_year.setCurrentText(str(current_year))
        
        self.cb_month.currentIndexChanged.connect(self.load_data)
        self.cb_year.currentTextChanged.connect(self.load_data)
        
        btn_refresh = QPushButton("Rafraîchir")
        btn_refresh.clicked.connect(self.load_data)
        
        filter_layout.addWidget(lbl_month)
        filter_layout.addWidget(self.cb_month)
        filter_layout.addWidget(lbl_year)
        filter_layout.addWidget(self.cb_year)
        filter_layout.addWidget(btn_refresh)
        filter_layout.addStretch()
        
        main_layout.addLayout(filter_layout)
        
        # --- Sub Tabs ---
        self.sub_tabs = QTabWidget()
        
        # 1. Tab: DIFFERENCES
        tab_diff = QWidget()
        diff_layout = QVBoxLayout(tab_diff)
        
        self.tbl_diff = QTableWidget()
        self.tbl_diff.setColumnCount(7)
        self.tbl_diff.setHorizontalHeaderLabels(["Date", "Utilisateur", "Montant Réel", "Montant Virtuelle", "Différence", "Net", "Remarques"])
        self.tbl_diff.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl_diff.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # Financial closures are append-only; corrections are separate audited reversals.
        self.toolbar_diff = QWidget()
        closure_toolbar = QHBoxLayout(self.toolbar_diff)
        closure_toolbar.setContentsMargins(0, 0, 0, 0)
        btn_add = QPushButton("Ajouter une cloture")
        btn_add.clicked.connect(self.add_cloture)
        btn_close_period = QPushButton("Cloturer le mois")
        btn_close_period.clicked.connect(self.close_selected_period)
        btn_reopen_period = QPushButton("Reouvrir le mois")
        btn_reopen_period.clicked.connect(self.reopen_selected_period)
        closure_toolbar.addWidget(btn_add)
        closure_toolbar.addWidget(btn_close_period)
        closure_toolbar.addWidget(btn_reopen_period)
        closure_toolbar.addWidget(QLabel("Les clotures sont tracees et ne se modifient pas directement."))
        closure_toolbar.addStretch()
        diff_layout.addWidget(self.toolbar_diff)
        diff_layout.addWidget(self.tbl_diff)
        
        self.sub_tabs.addTab(tab_diff, "DIFFÉRENCES")
        

        
        # 3. Tab: ÉTAT DIFFÉRENCES
        tab_etat = QWidget()
        etat_layout = QVBoxLayout(tab_etat)
        
        self.tbl_etat = QTableWidget()
        self.tbl_etat.setColumnCount(2)
        self.tbl_etat.setHorizontalHeaderLabels(["Utilisateur", "Montant Total"])
        self.tbl_etat.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl_etat.setEditTriggers(QTableWidget.NoEditTriggers)
        etat_layout.addWidget(self.tbl_etat)
        
        self.sub_tabs.addTab(tab_etat, "ÉTAT DIFFÉRENCES")
        
        main_layout.addWidget(self.sub_tabs)

    def get_filter_dates(self):
        month = self.cb_month.currentIndex()
        year = self.cb_year.currentText()
        
        if month == 0 or year == "Tous":
            return None, None
        return month, int(year)



    def add_cloture(self):
        from ui.caisse.dialogs import ClotureCaisseDialog
        dlg = ClotureCaisseDialog(self)
        if dlg.exec():
            self.load_data()

    def _selected_period(self):
        month, year = self.get_filter_dates()
        if not month or not year:
            QMessageBox.warning(self, "Periode requise", "Selectionnez un mois et une annee.")
            return None
        return data_manager.governance.get_or_create_period(f"{year}-{month:02d}-01")

    def close_selected_period(self):
        period = self._selected_period()
        if not period:
            return
        note, accepted = QInputDialog.getMultiLineText(self, "Cloture mensuelle", "Note de cloture :")
        if not accepted:
            return
        try:
            data_manager.governance.close_period(period["id_period"], None, note)
            QMessageBox.information(self, "Periode cloturee", "La periode est maintenant verrouillee.")
        except (ValueError, PermissionError) as error:
            QMessageBox.warning(self, "Cloture refusee", str(error))

    def reopen_selected_period(self):
        period = self._selected_period()
        if not period:
            return
        reason, accepted = QInputDialog.getMultiLineText(self, "Reouverture", "Motif obligatoire :")
        if not accepted:
            return
        try:
            data_manager.governance.reopen_period(period["id_period"], None, reason)
            QMessageBox.information(self, "Periode rouverte", "La reouverture a ete enregistree dans le journal d'audit.")
        except (ValueError, PermissionError) as error:
            QMessageBox.warning(self, "Reouverture refusee", str(error))
    def load_data(self):
        month, year = self.get_filter_dates()
        

        
        # 2. Load Différences (Clôtures)
        data_clotures = data_manager.caisse.get_clotures(month, year)
        self.tbl_diff.setRowCount(len(data_clotures))
        for i, row in enumerate(data_clotures):
            item_date = QTableWidgetItem(str(row['date_cloture']))
            item_date.setData(Qt.UserRole, row['id_cloture'])
            self.tbl_diff.setItem(i, 0, item_date)
            self.tbl_diff.setItem(i, 1, QTableWidgetItem(str(row['utilisateur'])))
            self.tbl_diff.setItem(i, 2, QTableWidgetItem(f"{row['montant_reel']:.2f}"))
            self.tbl_diff.setItem(i, 3, QTableWidgetItem(f"{row['montant_virtuel']:.2f}"))
            
            difference = float(row['montant_reel'] or 0) - float(row['montant_virtuel'] or 0)
            item_diff = QTableWidgetItem(f"{difference:.2f}")
            if difference < 0:
                item_diff.setForeground(QColor("red"))
            elif difference > 0:
                item_diff.setForeground(QColor("darkgreen"))
            font = item_diff.font()
            font.setBold(True)
            item_diff.setFont(font)
            self.tbl_diff.setItem(i, 4, item_diff)
            
            # Net is set to Montant Réel based on previous assumptions
            net = float(row['montant_reel'] or 0)
            self.tbl_diff.setItem(i, 5, QTableWidgetItem(f"{net:.2f}"))
            
            self.tbl_diff.setItem(i, 6, QTableWidgetItem(str(row['remarques'] or '')))

        # 3. Load Etat Différences
        data_etat = data_manager.caisse.get_etat_differences(month, year)
        self.tbl_etat.setRowCount(len(data_etat))
        for i, row in enumerate(data_etat):
            self.tbl_etat.setItem(i, 0, QTableWidgetItem(str(row['utilisateur'])))
            
            montant_total = float(row['montant_total'] or 0)
            item_total = QTableWidgetItem(f"{montant_total:.2f}")
            if montant_total < 0:
                item_total.setForeground(QColor("red"))
            elif montant_total > 0:
                item_total.setForeground(QColor("darkgreen"))
            
            self.tbl_etat.setItem(i, 1, item_total)
