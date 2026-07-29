from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QPushButton, QSplitter, QMessageBox, QLineEdit,
    QListWidget, QListWidgetItem, QStackedWidget, QButtonGroup, QComboBox
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont, QColor, QIcon
from database import data_manager
from ui.table_helper import (
    make_table_editable, get_svg_icon,
    PATH_EDIT, PATH_DELETE, PATH_SUPPLIER, PATH_WRENCH, PATH_BOX, PATH_LIST, PATH_SEARCH
)
from ui.fournisseurs.dialogs import FournisseurDialog
from .profitabilite_tab import ProfitabiliteTab


_sentinel = object()


class SupplierDetailTab(QWidget):
    def __init__(self, id_fournisseur, nom_fournisseur, parent_tab):
        super().__init__()
        self.id_fournisseur = id_fournisseur
        self.nom_fournisseur = nom_fournisseur
        self.parent_tab = parent_tab
        self.setup_ui()

    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        splitter = QSplitter(Qt.Horizontal)
        
        # --- 1. EQUIPEMENTS Section ---
        self.widget_equip = QWidget()
        lay_equip = QVBoxLayout(self.widget_equip)
        lay_equip.setContentsMargins(0, 0, 0, 0)
        lay_equip.setSpacing(5)
        
        lbl_title_equip = QLabel("ÉQUIPEMENTS")
        font_title = QFont("Arial", 12, QFont.Bold)
        lbl_title_equip.setFont(font_title)
        lbl_title_equip.setStyleSheet("color: #007572;")
        
        actions_equip = QHBoxLayout()
        self.btn_add_equip = QPushButton("+ Achat/BL")
        self.btn_add_equip.setStyleSheet("background-color: #007572; color: white; padding: 4px 8px; border-radius: 4px;")
        self.btn_pay_equip = QPushButton("+ Paiement")
        self.btn_pay_equip.setStyleSheet("background-color: #37474f; color: white; padding: 4px 8px; border-radius: 4px;")
        self.btn_edit_equip = QPushButton()
        self.btn_edit_equip.setIcon(get_svg_icon(PATH_EDIT, "#1565c0", 14))
        self.btn_edit_equip.setCursor(Qt.PointingHandCursor)
        self.btn_edit_equip.setToolTip("Modifier")
        self.btn_edit_equip.setStyleSheet("QPushButton { border: 1px solid #cfd8dc; border-radius: 4px; padding: 4px; } QPushButton:hover { background-color: #e3f2fd; border-color: #1565c0; }")
        
        self.btn_delete_equip = QPushButton()
        self.btn_delete_equip.setIcon(get_svg_icon(PATH_DELETE, "#c62828", 14))
        self.btn_delete_equip.setCursor(Qt.PointingHandCursor)
        self.btn_delete_equip.setToolTip("Supprimer")
        self.btn_delete_equip.setStyleSheet("QPushButton { border: 1px solid #cfd8dc; border-radius: 4px; padding: 4px; } QPushButton:hover { background-color: #ffebee; border-color: #c62828; }")
        
        actions_equip.addWidget(lbl_title_equip)
        actions_equip.addStretch()
        actions_equip.addWidget(self.btn_add_equip)
        actions_equip.addWidget(self.btn_pay_equip)
        actions_equip.addWidget(self.btn_edit_equip)
        actions_equip.addWidget(self.btn_delete_equip)
        lay_equip.addLayout(actions_equip)
        
        self.tbl_equip = QTableWidget()
        self.tbl_equip.setColumnCount(5)
        self.tbl_equip.setHorizontalHeaderLabels(["Date", "Montant BL/Achat", "Versement", "Paiement", "Observation"])
        self.tbl_equip.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl_equip.setEditTriggers(QTableWidget.NoEditTriggers)
        lay_equip.addWidget(self.tbl_equip)
        
        self.tbl_equip_total = QTableWidget()
        self.tbl_equip_total.setColumnCount(5)
        self.tbl_equip_total.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl_equip_total.horizontalHeader().setVisible(False)
        self.tbl_equip_total.verticalHeader().setVisible(False)
        self.tbl_equip_total.setRowCount(1)
        self.tbl_equip_total.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tbl_equip_total.setFixedHeight(30)
        self.tbl_equip_total.setFocusPolicy(Qt.NoFocus)
        self.tbl_equip_total.setStyleSheet("QTableWidget { border-top: none; }")
        lay_equip.addWidget(self.tbl_equip_total)
        
        # --- 2. CONSOMMABLES Section ---
        self.widget_cons = QWidget()
        lay_cons = QVBoxLayout(self.widget_cons)
        lay_cons.setContentsMargins(0, 0, 0, 0)
        lay_cons.setSpacing(5)
        
        lbl_title_cons = QLabel("CONSOMMABLES")
        lbl_title_cons.setFont(font_title)
        lbl_title_cons.setStyleSheet("color: #007572;")
        
        actions_cons = QHBoxLayout()
        self.btn_add_cons = QPushButton("+ Achat/BL")
        self.btn_add_cons.setStyleSheet("background-color: #007572; color: white; padding: 4px 8px; border-radius: 4px;")
        self.btn_pay_cons = QPushButton("+ Paiement")
        self.btn_pay_cons.setStyleSheet("background-color: #37474f; color: white; padding: 4px 8px; border-radius: 4px;")
        self.btn_edit_cons = QPushButton()
        self.btn_edit_cons.setIcon(get_svg_icon(PATH_EDIT, "#1565c0", 14))
        self.btn_edit_cons.setCursor(Qt.PointingHandCursor)
        self.btn_edit_cons.setToolTip("Modifier")
        self.btn_edit_cons.setStyleSheet("QPushButton { border: 1px solid #cfd8dc; border-radius: 4px; padding: 4px; } QPushButton:hover { background-color: #e3f2fd; border-color: #1565c0; }")
        
        self.btn_delete_cons = QPushButton()
        self.btn_delete_cons.setIcon(get_svg_icon(PATH_DELETE, "#c62828", 14))
        self.btn_delete_cons.setCursor(Qt.PointingHandCursor)
        self.btn_delete_cons.setToolTip("Supprimer")
        self.btn_delete_cons.setStyleSheet("QPushButton { border: 1px solid #cfd8dc; border-radius: 4px; padding: 4px; } QPushButton:hover { background-color: #ffebee; border-color: #c62828; }")
        
        actions_cons.addWidget(lbl_title_cons)
        actions_cons.addStretch()
        actions_cons.addWidget(self.btn_add_cons)
        actions_cons.addWidget(self.btn_pay_cons)
        actions_cons.addWidget(self.btn_edit_cons)
        actions_cons.addWidget(self.btn_delete_cons)
        lay_cons.addLayout(actions_cons)
        
        self.tbl_cons = QTableWidget()
        self.tbl_cons.setColumnCount(6)
        self.tbl_cons.setHorizontalHeaderLabels(["Mois Paiement", "Date", "Montant BL/Achat", "Versement", "Paiement", "Observation"])
        self.tbl_cons.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl_cons.setEditTriggers(QTableWidget.NoEditTriggers)
        lay_cons.addWidget(self.tbl_cons)
        
        self.tbl_cons_total = QTableWidget()
        self.tbl_cons_total.setColumnCount(6)
        self.tbl_cons_total.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl_cons_total.horizontalHeader().setVisible(False)
        self.tbl_cons_total.verticalHeader().setVisible(False)
        self.tbl_cons_total.setRowCount(1)
        self.tbl_cons_total.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tbl_cons_total.setFixedHeight(30)
        self.tbl_cons_total.setFocusPolicy(Qt.NoFocus)
        self.tbl_cons_total.setStyleSheet("QTableWidget { border-top: none; }")
        lay_cons.addWidget(self.tbl_cons_total)
        
        splitter.addWidget(self.widget_equip)
        splitter.addWidget(self.widget_cons)
        splitter.setSizes([500, 600])
        
        layout.addWidget(splitter)
        
        # Connect buttons
        self.btn_add_equip.clicked.connect(lambda: self.add_purchase("EQUIPEMENTS"))
        self.btn_add_cons.clicked.connect(lambda: self.add_purchase("CONSOMMABLES"))
        
        self.btn_pay_equip.clicked.connect(lambda: self.add_payment(self.tbl_equip))
        self.btn_pay_cons.clicked.connect(lambda: self.add_payment(self.tbl_cons))
        
        self.btn_edit_equip.clicked.connect(lambda: self.edit_row(self.tbl_equip))
        self.btn_edit_cons.clicked.connect(lambda: self.edit_row(self.tbl_cons))
        
        self.btn_delete_equip.clicked.connect(lambda: self.delete_row(self.tbl_equip))
        self.btn_delete_cons.clicked.connect(lambda: self.delete_row(self.tbl_cons))
        
        self.tbl_equip.doubleClicked.connect(lambda: self.edit_row(self.tbl_equip))
        self.tbl_cons.doubleClicked.connect(lambda: self.edit_row(self.tbl_cons))

    def load_data(self, month=None, year=None):
        # 1. Load Equipements
        equip_data = data_manager.fournisseurs.get_supplier_ledger(self.id_fournisseur, "EQUIPEMENTS", month, year)
        self.populate_table(self.tbl_equip, self.tbl_equip_total, equip_data, is_consommables=False)
        
        # 2. Load Consommables (and check for previous balance / solde_initial)
        cons_data = data_manager.fournisseurs.get_supplier_ledger(self.id_fournisseur, "CONSOMMABLES", month, year)
        
        info = data_manager.fournisseurs.get_supplier_info(self.id_fournisseur)
        solde_initial = float(info['solde_initial'] or 0.0) if info else 0.0
        
        display_cons_data = []
        if solde_initial > 0:
            init_row = {
                'id_depense': -1,
                'date_facture': '2025-12-31',
                'type_document': 'SOLDE INITIAL',
                'montant_total': solde_initial,
                'observation': 'Solde initial (Année précédente)',
                'total_verse': 0.0,
                'reste': solde_initial,
                'statut': '-',
                'mois_paiement': 'Etat 2025'
            }
            if not month:
                display_cons_data.append(init_row)
                
        display_cons_data.extend(cons_data)
        self.populate_table(self.tbl_cons, self.tbl_cons_total, display_cons_data, is_consommables=True)

    def populate_table(self, table, total_table, data, is_consommables=False):
        table.setRowCount(len(data))
        
        total_montant = 0.0
        total_versement = 0.0
        total_reste = 0.0
        
        for i, row in enumerate(data):
            date_val = str(row['date_facture'])
            montant = float(row['montant_total'])
            verse = float(row['total_verse'])
            reste = float(row['reste'])
            status = str(row['statut'])
            obs = str(row['observation'] or '')
            mois_pay = str(row['mois_paiement'])
            
            total_montant += montant
            total_versement += verse
            total_reste += reste
            
            item_date = QTableWidgetItem(date_val)
            item_date.setData(Qt.UserRole, row['id_depense'])
            
            item_montant = QTableWidgetItem(f"{montant:,.2f}")
            item_verse = QTableWidgetItem(f"{verse:,.2f}")
            item_status = QTableWidgetItem(status)
            item_obs = QTableWidgetItem(obs)
            
            if is_consommables:
                item_mois = QTableWidgetItem(mois_pay)
                table.setItem(i, 0, item_mois)
                table.setItem(i, 1, item_date)
                table.setItem(i, 2, item_montant)
                table.setItem(i, 3, item_verse)
                table.setItem(i, 4, item_status)
                table.setItem(i, 5, item_obs)
            else:
                table.setItem(i, 0, item_date)
                table.setItem(i, 1, item_montant)
                table.setItem(i, 2, item_verse)
                table.setItem(i, 3, item_status)
                table.setItem(i, 4, item_obs)
                
        total_table.clear()
        
        item_tot_lbl = QTableWidgetItem("TOTAL")
        font_tot = item_tot_lbl.font()
        font_tot.setBold(True)
        item_tot_lbl.setFont(font_tot)
        
        item_tot_montant = QTableWidgetItem(f"{total_montant:,.2f}")
        item_tot_montant.setFont(font_tot)
        item_tot_verse = QTableWidgetItem(f"{total_versement:,.2f}")
        item_tot_verse.setFont(font_tot)
        
        item_tot_reste_lbl = QTableWidgetItem("RESTE À PAYER")
        item_tot_reste_lbl.setFont(font_tot)
        item_tot_reste_val = QTableWidgetItem(f"{total_reste:,.2f}")
        item_tot_reste_val.setFont(font_tot)
        
        if is_consommables:
            total_table.setItem(0, 1, item_tot_lbl)
            total_table.setItem(0, 2, item_tot_montant)
            total_table.setItem(0, 3, item_tot_verse)
            total_table.setItem(0, 4, item_tot_reste_lbl)
            total_table.setItem(0, 5, item_tot_reste_val)
        else:
            total_table.setItem(0, 0, item_tot_lbl)
            total_table.setItem(0, 1, item_tot_montant)
            total_table.setItem(0, 2, item_tot_verse)
            total_table.setItem(0, 3, item_tot_reste_lbl)
            total_table.setItem(0, 4, item_tot_reste_val)

    def add_purchase(self, category_name):
        from ui.fournisseurs.dialogs import DepenseFournisseurDialog
        dlg = DepenseFournisseurDialog(self, id_fournisseur=self.id_fournisseur, category_name=category_name)
        if dlg.exec():
            self.load_data(self.parent_tab.month, self.parent_tab.year)
            self.parent_tab.load_data()

    def add_payment(self, table):
        row = table.currentRow()
        id_depense = None
        if row >= 0:
            item = table.item(row, 1 if table.columnCount() == 6 else 0)
            if item:
                id_depense = item.data(Qt.UserRole)
                
        if id_depense == -1:
            QMessageBox.warning(self, "Attention", "Pour payer la dette de l'année précédente, veuillez ajouter une dépense spécifique 'Solde Initial 2025' ou similaire.")
            return

        from ui.fournisseurs.dialogs import PaiementFournisseurDialog
        dlg = PaiementFournisseurDialog(
            self, 
            id_fournisseur=self.id_fournisseur, 
            id_depense=id_depense,
            month=self.parent_tab.month,
            year=self.parent_tab.year
        )
        if dlg.exec():
            self.load_data(self.parent_tab.month, self.parent_tab.year)
            self.parent_tab.load_data()

    def edit_row(self, table):
        row = table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner une ligne à modifier.")
            return
            
        col_idx = 1 if table.columnCount() == 6 else 0
        item = table.item(row, col_idx)
        if not item:
            return
        id_depense = item.data(Qt.UserRole)
        
        if id_depense == -1:
            QMessageBox.warning(self, "Attention", "Le solde initial est géré via la fiche du fournisseur et ne peut pas être modifié d'ici.")
            return
            
        record = data_manager.db.fetch_one("SELECT * FROM Depenses_Achats WHERE id_depense = %s", (id_depense,))
        if not record:
            return
            
        from ui.fournisseurs.dialogs import DepenseFournisseurDialog
        dlg = DepenseFournisseurDialog(self, record=record)
        if dlg.exec():
            self.load_data(self.parent_tab.month, self.parent_tab.year)
            self.parent_tab.load_data()

    def delete_row(self, table):
        row = table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner une ligne à supprimer.")
            return
            
        col_idx = 1 if table.columnCount() == 6 else 0
        item = table.item(row, col_idx)
        if not item:
            return
        id_depense = item.data(Qt.UserRole)
        
        if id_depense == -1:
            QMessageBox.warning(self, "Attention", "Le solde initial ne peut pas être supprimé d'ici.")
            return

        ans = QMessageBox.question(self, "Confirmation", "Voulez-vous vraiment supprimer cette facture/achat ? Cela supprimera aussi tous ses paiements associés.", QMessageBox.Yes | QMessageBox.No)
        if ans == QMessageBox.Yes:
            success, _ = data_manager.db.delete_record("Depenses_Achats", "id_depense", id_depense)
            if success:
                self.load_data(self.parent_tab.month, self.parent_tab.year)
                self.parent_tab.load_data()


class EtatFournisseursTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.month = None
        self.year = None
        self.supplier_ledgers = {}
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 1. Create sub-pages
        self.tab_general, self.tbl_fournisseurs_gen, self.tbl_total_gen = self.create_total_tab(has_toolbar=True)
        self.tab_equip, self.tbl_fournisseurs_equip, self.tbl_total_equip = self.create_total_tab(has_toolbar=False)
        self.tab_cons, self.tbl_fournisseurs_cons, self.tbl_total_cons = self.create_total_tab(has_toolbar=False)
        
        # 2. Fiches Individuelles (Master-Detail)
        self.tab_details = QWidget()
        lay_details = QHBoxLayout(self.tab_details)
        lay_details.setContentsMargins(10, 10, 10, 10)
        lay_details.setSpacing(15)

        # Left sidebar for list and search
        sidebar = QWidget()
        sidebar.setFixedWidth(240)
        lay_sidebar = QVBoxLayout(sidebar)
        lay_sidebar.setContentsMargins(0, 0, 0, 0)
        lay_sidebar.setSpacing(10)

        # List Widget
        self.list_suppliers = QListWidget()
        self.list_suppliers.setStyleSheet(
            "QListWidget { border: 1px solid #cfd8dc; border-radius: 4px; background-color: white; }"
            "QListWidget::item { padding: 8px 12px; border-bottom: 1px solid #eceff1; }"
            "QListWidget::item:selected { background-color: #007572; color: white; }"
            "QListWidget::item:hover:!selected { background-color: #f5f6fa; }"
        )
        self.list_suppliers.currentItemChanged.connect(self.on_detail_supplier_changed)
        lay_sidebar.addWidget(self.list_suppliers)

        # Right side Stacked Widget for ledger views
        self.stack_ledgers = QStackedWidget()
        # Empty placeholder widget for when no supplier is selected
        placeholder = QWidget()
        lay_placeholder = QVBoxLayout(placeholder)
        lbl_placeholder = QLabel("Veuillez sélectionner un fournisseur dans la liste pour afficher sa fiche.")
        lbl_placeholder.setAlignment(Qt.AlignCenter)
        lbl_placeholder.setStyleSheet("color: #7f8c8d; font-size: 13px; font-style: italic;")
        lay_placeholder.addWidget(lbl_placeholder)
        self.stack_ledgers.addWidget(placeholder)

        lay_details.addWidget(sidebar)
        lay_details.addWidget(self.stack_ledgers, stretch=1)
        
        # 3. Create central Stacked Widget
        self.tab_prof = ProfitabiliteTab(self)
        self.stack_pages = QStackedWidget()
        self.stack_pages.addWidget(self.tab_general)
        self.stack_pages.addWidget(self.tab_equip)
        self.stack_pages.addWidget(self.tab_cons)
        self.stack_pages.addWidget(self.tab_details)
        self.stack_pages.addWidget(self.tab_prof)
        
        # 4. Top Navigation Bar (Pill buttons + Search)
        nav_widget = QWidget()
        nav_widget.setObjectName("sub_nav_widget")
        nav_widget.setStyleSheet("QWidget#sub_nav_widget { background-color: #ffffff; border-bottom: 1px solid #e2e8f0; }")
        
        nav_layout = QHBoxLayout(nav_widget)
        nav_layout.setContentsMargins(15, 8, 15, 8)
        nav_layout.setSpacing(8)
        
        self.btn_group = QButtonGroup(self)
        self.btn_group.setExclusive(True)
        
        # Helper to define pill icon
        def get_dynamic_pill_icon(path_data, size=14):
            icon = QIcon()
            px_off = get_svg_icon(path_data, "#607d8b", size).pixmap(size, size)
            px_on = get_svg_icon(path_data, "#ffffff", size).pixmap(size, size)
            icon.addPixmap(px_off, QIcon.Normal, QIcon.Off)
            icon.addPixmap(px_on, QIcon.Normal, QIcon.On)
            icon.addPixmap(px_off, QIcon.Active, QIcon.Off)
            icon.addPixmap(px_on, QIcon.Active, QIcon.On)
            return icon
            
        self.btn_page_gen = QPushButton(" État Général")
        self.btn_page_gen.setIcon(get_dynamic_pill_icon(PATH_LIST, 14))
        
        self.btn_page_equip = QPushButton(" Équipements")
        self.btn_page_equip.setIcon(get_dynamic_pill_icon(PATH_WRENCH, 14))
        
        self.btn_page_cons = QPushButton(" Consommables")
        self.btn_page_cons.setIcon(get_dynamic_pill_icon(PATH_BOX, 14))
        
        self.btn_page_details = QPushButton(" Fiches Individuelles")
        self.btn_page_details.setIcon(get_dynamic_pill_icon(PATH_SUPPLIER, 14))

        self.btn_page_prof = QPushButton(" 📈 Profitabilité")
        self.btn_page_prof.setIcon(get_dynamic_pill_icon(PATH_LIST, 14))
        
        btn_style = """
            QPushButton {
                background-color: #ffffff;
                color: #607d8b;
                border: 1px solid #cfd8dc;
                border-radius: 15px;
                padding: 6px 16px;
                font-weight: 600;
                font-size: 13px;
                min-height: 18px;
            }
            QPushButton:hover {
                background-color: #f1f5f9;
                color: #007572;
                border-color: #b0bec5;
            }
            QPushButton:checked {
                background-color: #007572;
                color: #ffffff;
                border-color: #007572;
            }
        """
        
        for i, btn in enumerate([self.btn_page_gen, self.btn_page_equip, self.btn_page_cons, self.btn_page_details, self.btn_page_prof]):
            btn.setCheckable(True)
            btn.setStyleSheet(btn_style)
            btn.setCursor(Qt.PointingHandCursor)
            self.btn_group.addButton(btn, i)
            nav_layout.addWidget(btn)
            
        self.btn_page_gen.setChecked(True)
        nav_layout.addStretch()
        
        # Month & Year Filters
        lbl_month = QLabel("Mois:")
        lbl_month.setStyleSheet("font-size: 13px; color: #475569; font-weight: 500;")
        self.cb_month = QComboBox()
        self.cb_month.addItems(["Tous", "Janvier", "Février", "Mars", "Avril", "Mai", "Juin", 
                               "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"])
        self.cb_month.setStyleSheet("""
            QComboBox {
                padding: 4px 8px;
                border-radius: 6px;
                border: 1px solid #cfd8dc;
                background-color: white;
                font-size: 13px;
                color: #2c3e50;
            }
            QComboBox:focus { border: 1.5px solid #007572; }
        """)
        
        lbl_year = QLabel("Année:")
        lbl_year.setStyleSheet("font-size: 13px; color: #475569; font-weight: 500;")
        self.cb_year = QComboBox()
        current_year = QDate.currentDate().year()
        self.cb_year.addItems(["Tous"] + [str(y) for y in range(current_year - 2, current_year + 5)])
        self.cb_year.setStyleSheet("""
            QComboBox {
                padding: 4px 8px;
                border-radius: 6px;
                border: 1px solid #cfd8dc;
                background-color: white;
                font-size: 13px;
                color: #2c3e50;
            }
            QComboBox:focus { border: 1.5px solid #007572; }
        """)
        
        self.cb_month.setCurrentIndex(QDate.currentDate().month())
        self.cb_year.setCurrentText(str(current_year))
        
        self.cb_month.currentIndexChanged.connect(self.on_filter_changed)
        self.cb_year.currentTextChanged.connect(self.on_filter_changed)
        
        nav_layout.addWidget(lbl_month)
        nav_layout.addWidget(self.cb_month)
        nav_layout.addWidget(lbl_year)
        nav_layout.addWidget(self.cb_year)

        # Search bar
        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("Rechercher...")
        self.txt_search.setFixedWidth(160)
        self.txt_search.setStyleSheet("""
            QLineEdit {
                padding: 5px 12px;
                border-radius: 14px;
                border: 1px solid #cfd8dc;
                background-color: white;
                font-size: 13px;
                color: #2c3e50;
            }
            QLineEdit:focus {
                border: 1.5px solid #007572;
            }
        """)
        self.txt_search.textChanged.connect(self.on_search_changed)
        nav_layout.addWidget(self.txt_search)

        # Export Rapport Analytique Achats button
        self.btn_export_analytique = QPushButton("📊 Rapport Analytique")
        self.btn_export_analytique.setCursor(Qt.PointingHandCursor)
        self.btn_export_analytique.setStyleSheet("""
            QPushButton {
                background-color: #f57c00;
                color: white;
                font-weight: bold;
                padding: 6px 12px;
                border-radius: 14px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #e65100;
            }
        """)
        self.btn_export_analytique.clicked.connect(self.export_analytique_pdf)
        nav_layout.addWidget(self.btn_export_analytique)
        
        layout.addWidget(nav_widget)
        layout.addWidget(self.stack_pages)
        
        # Wire up signals
        self.btn_group.idClicked.connect(self.on_nav_changed)
        
        self.tbl_fournisseurs_gen.doubleClicked.connect(lambda index: self.on_overview_row_double_clicked(self.tbl_fournisseurs_gen, index))
        self.tbl_fournisseurs_equip.doubleClicked.connect(lambda index: self.on_overview_row_double_clicked(self.tbl_fournisseurs_equip, index))
        self.tbl_fournisseurs_cons.doubleClicked.connect(lambda index: self.on_overview_row_double_clicked(self.tbl_fournisseurs_cons, index))

    def on_filter_changed(self):
        month = self.cb_month.currentIndex()
        year = self.cb_year.currentText()
        
        filter_month = None if month == 0 else month
        filter_year = None if year == "Tous" else int(year)
        
        self.load_data(filter_month, filter_year)

    def on_nav_changed(self, page_id):
        self.stack_pages.setCurrentIndex(page_id)
        self.on_search_changed(self.txt_search.text())

    def on_search_changed(self, text):
        text = text.lower().strip()
        current_page = self.stack_pages.currentIndex()
        
        if current_page == 0:
            self.filter_table(self.tbl_fournisseurs_gen, self.tbl_total_gen, text)
        elif current_page == 1:
            self.filter_table(self.tbl_fournisseurs_equip, self.tbl_total_equip, text)
        elif current_page == 2:
            self.filter_table(self.tbl_fournisseurs_cons, self.tbl_total_cons, text)
        elif current_page == 3:
            first_visible_item = None
            for i in range(self.list_suppliers.count()):
                item = self.list_suppliers.item(i)
                visible = text in item.text().lower()
                item.setHidden(not visible)
                if visible and not first_visible_item:
                    first_visible_item = item
            
            current = self.list_suppliers.currentItem()
            if current and current.isHidden() and first_visible_item:
                self.list_suppliers.setCurrentItem(first_visible_item)

    def filter_table(self, table, total_table, text):
        total_cmd = 0.0
        total_pay = 0.0
        total_reste = 0.0
        
        for row in range(table.rowCount()):
            item_name = table.item(row, 0)
            if item_name:
                match = text in item_name.text().lower()
                table.setRowHidden(row, not match)
                if match:
                    try:
                        cmd_val = float(table.item(row, 1).text().replace(',', ''))
                    except Exception:
                        cmd_val = 0.0
                    try:
                        pay_val = float(table.item(row, 2).text().replace(',', ''))
                    except Exception:
                        pay_val = 0.0
                    try:
                        reste_val = float(table.item(row, 3).text().replace(',', ''))
                    except Exception:
                        reste_val = 0.0
                        
                    total_cmd += cmd_val
                    total_pay += pay_val
                    total_reste += reste_val
                    
        item_cmd = total_table.item(0, 1)
        if item_cmd:
            item_cmd.setText(f"{total_cmd:,.2f}")
        item_pay = total_table.item(0, 2)
        if item_pay:
            item_pay.setText(f"{total_pay:,.2f}")
        item_reste = total_table.item(0, 3)
        if item_reste:
            item_reste.setText(f"{total_reste:,.2f}")

    def on_overview_row_double_clicked(self, table, index):
        row = index.row()
        item = table.item(row, 0)
        if not item:
            return
        id_f = item.data(Qt.UserRole)
        if id_f is None:
            return
            
        self.btn_page_details.setChecked(True)
        self.stack_pages.setCurrentIndex(3)
        for i in range(self.list_suppliers.count()):
            list_item = self.list_suppliers.item(i)
            if list_item.data(Qt.UserRole) == id_f:
                self.list_suppliers.setCurrentItem(list_item)
                break

    def on_detail_supplier_changed(self, current, previous):
        if not current:
            self.stack_ledgers.setCurrentIndex(0)
            return
            
        id_f = current.data(Qt.UserRole)
        if id_f in self.supplier_ledgers:
            widget = self.supplier_ledgers[id_f]
            self.stack_ledgers.setCurrentWidget(widget)
        else:
            self.stack_ledgers.setCurrentIndex(0)

    def create_total_tab(self, has_toolbar=False):
        tab_widget = QWidget()
        lay = QVBoxLayout(tab_widget)
        lay.setSpacing(4)
        lay.setContentsMargins(5, 5, 5, 5)
        
        tbl = QTableWidget()
        tbl.setColumnCount(4)
        tbl.setHorizontalHeaderLabels(["FOURNISSEUR LAM", "TOTAL DES COMMANDES", "PAYER", "RESTE"])
        tbl.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        tbl.setEditTriggers(QTableWidget.NoEditTriggers)
        
        if has_toolbar:
            self.tbl_fournisseurs = tbl
        
        lay.addWidget(tbl)
        
        tbl_total = QTableWidget()
        tbl_total.setColumnCount(4)
        tbl_total.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        tbl_total.horizontalHeader().setVisible(False)
        tbl_total.verticalHeader().setVisible(False)
        tbl_total.setRowCount(1)
        tbl_total.setEditTriggers(QTableWidget.NoEditTriggers)
        tbl_total.setFixedHeight(30)
        tbl_total.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        tbl_total.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        tbl_total.setFocusPolicy(Qt.NoFocus)
        tbl_total.setSelectionMode(QTableWidget.NoSelection)
        tbl_total.setStyleSheet("QTableWidget { border-top: none; }")
        lay.addWidget(tbl_total)
        
        if has_toolbar:
            self.tbl_total = tbl_total
            
        return tab_widget, tbl, tbl_total

    def load_data(self, month=_sentinel, year=_sentinel):
        if month is not _sentinel:
            self.month = month
        if year is not _sentinel:
            self.year = year
            
        m = self.month
        y = self.year
            
        data_manager.fournisseurs.ensure_category_exists("EQUIPEMENTS")
        data_manager.fournisseurs.ensure_category_exists("CONSOMMABLES")

        prev_selected_id = None
        current_item = self.list_suppliers.currentItem()
        if current_item:
            prev_selected_id = current_item.data(Qt.UserRole)

        active_index = self.stack_pages.currentIndex()

        suppliers = data_manager.fournisseurs.get_fournisseurs_list()

        # Clear QListWidget and QStackedWidget
        self.list_suppliers.clear()
        while self.stack_ledgers.count() > 1:
            widget = self.stack_ledgers.widget(1)
            self.stack_ledgers.removeWidget(widget)
            widget.deleteLater()

        self.supplier_ledgers = {}

        for supplier in suppliers:
            id_f = supplier['id_fournisseur']
            name_f = supplier['nom_fournisseur']
            
            item = QListWidgetItem(name_f)
            item.setData(Qt.UserRole, id_f)
            self.list_suppliers.addItem(item)
            
            ledger_tab = SupplierDetailTab(id_f, name_f, self)
            self.stack_ledgers.addWidget(ledger_tab)
            self.supplier_ledgers[id_f] = ledger_tab

        # 1. Populate general totals
        data_gen = data_manager.fournisseurs.get_fournisseurs_state(None, m, y)
        self.populate_total_table(self.tbl_fournisseurs_gen, self.tbl_total_gen, data_gen)

        # 2. Populate EQUIPEMENTS totals
        data_equip = data_manager.fournisseurs.get_fournisseurs_state("EQUIPEMENTS", m, y)
        self.populate_total_table(self.tbl_fournisseurs_equip, self.tbl_total_equip, data_equip)

        # 3. Populate CONSOMMABLES totals
        data_cons = data_manager.fournisseurs.get_fournisseurs_state("CONSOMMABLES", m, y)
        self.populate_total_table(self.tbl_fournisseurs_cons, self.tbl_total_cons, data_cons)

        # 4. Load detailed data for each supplier
        for id_f, ledger in self.supplier_ledgers.items():
            ledger.load_data(m, y)

        # Restore selection
        if prev_selected_id is not None:
            for i in range(self.list_suppliers.count()):
                item = self.list_suppliers.item(i)
                if item.data(Qt.UserRole) == prev_selected_id:
                    self.list_suppliers.setCurrentItem(item)
                    break
        else:
            if self.list_suppliers.count() > 0:
                self.list_suppliers.setCurrentRow(0)

        # Restore active tab
        if active_index >= 0 and active_index < self.stack_pages.count():
            self.stack_pages.setCurrentIndex(active_index)
            btn = self.btn_group.button(active_index)
            if btn:
                btn.setChecked(True)

        # Apply search filter if active
        if hasattr(self, 'txt_search'):
            self.on_search_changed(self.txt_search.text())

    def populate_total_table(self, table, total_table, data):
        S = len(data)
        table.setRowCount(S)
        
        total_cmd_sum = 0.0
        total_pay_sum = 0.0
        total_reste_sum = 0.0
        
        for i, row in enumerate(data):
            item_name = QTableWidgetItem(str(row['nom_fournisseur']))
            item_name.setData(Qt.UserRole, row['id_fournisseur'])
            
            cmd_val = float(row['total_commandes'])
            pay_val = float(row['total_paye'])
            reste_val = float(row['reste_a_payer'])
            
            total_cmd_sum += cmd_val
            total_pay_sum += pay_val
            total_reste_sum += reste_val
            
            item_cmd = QTableWidgetItem(f"{cmd_val:,.2f}")
            item_pay = QTableWidgetItem(f"{pay_val:,.2f}")
            item_reste = QTableWidgetItem(f"{reste_val:,.2f}")
            
            table.setItem(i, 0, item_name)
            table.setItem(i, 1, item_cmd)
            table.setItem(i, 2, item_pay)
            table.setItem(i, 3, item_reste)
            
        total_table.clear()
        
        item_tot_lbl = QTableWidgetItem("TOTAL")
        font_tot = item_tot_lbl.font()
        font_tot.setBold(True)
        item_tot_lbl.setFont(font_tot)
        
        item_tot_cmd = QTableWidgetItem(f"{total_cmd_sum:,.2f}")
        item_tot_cmd.setFont(font_tot)
        item_tot_pay = QTableWidgetItem(f"{total_pay_sum:,.2f}")
        item_tot_pay.setFont(font_tot)
        item_tot_reste = QTableWidgetItem(f"{total_reste_sum:,.2f}")
        item_tot_reste.setFont(font_tot)
        total_table.setItem(0, 0, item_tot_lbl)
        total_table.setItem(0, 1, item_tot_cmd)
        total_table.setItem(0, 2, item_tot_pay)
        total_table.setItem(0, 3, item_tot_reste)

    def export_analytique_pdf(self):
        m_idx = self.cb_month.currentIndex()
        m_name = self.cb_month.currentText()
        y_str = self.cb_year.currentText()
        if m_idx == 0 or y_str == "Tous":
            m_idx = QDate.currentDate().month()
            months = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
            m_name = months[m_idx - 1]
            y_str = str(QDate.currentDate().year())
        
        y = int(y_str)
        data = data_manager.banque.get_analytique_achats(m_idx, y)
        if not data.get('categories'):
            QMessageBox.information(self, "Info", f"Aucune donnée d'achats/dépenses trouvée pour {m_name} {y}.")
            return

        from PySide6.QtWidgets import QFileDialog
        path, _ = QFileDialog.getSaveFileName(self, "Enregistrer Rapport Analytique Achats", f"Rapport_Analytique_Achats_{m_idx:02d}_{y}.pdf", "PDF (*.pdf)")
        if not path:
            return

        from utils.pdf_generator import PdfGenerator
        gen = PdfGenerator()
        if gen.generate_analytique_achats_pdf(path, m_name, y, data):
            QMessageBox.information(self, "Succès", "Rapport Analytique des Achats généré avec succès!")
        else:
            QMessageBox.critical(self, "Erreur", "Erreur lors de la génération du PDF.")

