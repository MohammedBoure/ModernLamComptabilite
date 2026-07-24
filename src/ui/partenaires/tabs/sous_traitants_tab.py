from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QPushButton, QMessageBox, QLineEdit,
    QListWidget, QListWidgetItem, QStackedWidget, QButtonGroup
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor, QIcon
from database import data_manager
from ui.table_helper import (
    make_table_editable, get_svg_icon,
    PATH_EDIT, PATH_DELETE, PATH_PARTNER, PATH_LIST, PATH_SEARCH, PATH_DOCUMENT
)
from ui.partenaires.dialogs import PartenaireDialog, OperationPartenaireDialog, PaiementPartenaireDialog


_sentinel = object()


class PartnerDetailTab(QWidget):
    def __init__(self, id_partenaire, nom_partenaire, type_partenaire, parent_tab):
        super().__init__()
        self.id_partenaire = id_partenaire
        self.nom_partenaire = nom_partenaire
        self.type_partenaire = type_partenaire
        self.parent_tab = parent_tab
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        # Title & Toolbar layout
        header_lay = QHBoxLayout()
        lbl_title = QLabel(f"Détails : {self.nom_partenaire} ({self.type_partenaire})")
        font_title = QFont("Arial", 12, QFont.Bold)
        lbl_title.setFont(font_title)
        lbl_title.setStyleSheet("color: #007572;")
        
        self.btn_add_op = QPushButton(" + Nouvelle Opération")
        self.btn_add_op.setStyleSheet("background-color: #007572; color: white; padding: 5px 10px; border-radius: 4px; font-weight: bold;")
        self.btn_pay = QPushButton(" + Nouveau Paiement")
        self.btn_pay.setStyleSheet("background-color: #37474f; color: white; padding: 5px 10px; border-radius: 4px; font-weight: bold;")
        self.btn_edit = QPushButton(" Modifier")
        self.btn_edit.setIcon(get_svg_icon(PATH_EDIT, "#ffffff", 14))
        self.btn_edit.setStyleSheet("background-color: #f57c00; color: white; padding: 5px 10px; border-radius: 4px; font-weight: bold;")
        self.btn_delete = QPushButton(" Supprimer")
        self.btn_delete.setIcon(get_svg_icon(PATH_DELETE, "#ffffff", 14))
        self.btn_delete.setStyleSheet("background-color: #d32f2f; color: white; padding: 5px 10px; border-radius: 4px; font-weight: bold;")
        
        header_lay.addWidget(lbl_title)
        header_lay.addStretch()
        header_lay.addWidget(self.btn_add_op)
        header_lay.addWidget(self.btn_pay)
        header_lay.addWidget(self.btn_edit)
        header_lay.addWidget(self.btn_delete)
        layout.addLayout(header_lay)
        
        self.tbl_ledger = QTableWidget()
        self.tbl_ledger.setColumnCount(7)
        self.tbl_ledger.setHorizontalHeaderLabels([
            "Date Opération", "Document", "Montant", "Versement", "Paiement", "Date Réception", "Observation"
        ])
        self.tbl_ledger.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl_ledger.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.tbl_ledger)
        
        self.tbl_total = QTableWidget()
        self.tbl_total.setColumnCount(7)
        self.tbl_total.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl_total.horizontalHeader().setVisible(False)
        self.tbl_total.verticalHeader().setVisible(False)
        self.tbl_total.setRowCount(1)
        self.tbl_total.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tbl_total.setFixedHeight(30)
        self.tbl_total.setFocusPolicy(Qt.NoFocus)
        self.tbl_total.setStyleSheet("QTableWidget { border-top: none; }")
        layout.addWidget(self.tbl_total)
        
        self.btn_add_op.clicked.connect(self.add_operation)
        self.btn_pay.clicked.connect(self.add_payment)
        self.btn_edit.clicked.connect(self.edit_row)
        self.btn_delete.clicked.connect(self.delete_row)
        
        self.tbl_ledger.doubleClicked.connect(self.edit_row)

    def load_data(self, month=None, year=None):
        ledger_data = data_manager.partenaires.get_partner_ledger(self.id_partenaire, month, year)
        
        info = data_manager.partenaires.get_partner_info(self.id_partenaire)
        solde_initial = float(info['solde_initial'] or 0.0) if info else 0.0
        
        display_data = []
        if solde_initial > 0 and not month:
            init_row = {
                'id_operation': -1,
                'date_operation': '2025-12-31',
                'type_document': 'SOLDE INITIAL',
                'montant_total': solde_initial,
                'date_reception': '-',
                'observation': 'Solde initial (Année précédente)',
                'total_verse': 0.0,
                'reste': solde_initial,
                'statut': '-',
                'mois_paiement': 'Etat 2025'
            }
            display_data.append(init_row)
            
        display_data.extend(ledger_data)
        self.populate_table(display_data)

    def populate_table(self, data):
        self.tbl_ledger.setRowCount(len(data))
        
        total_montant = 0.0
        total_versement = 0.0
        total_reste = 0.0
        
        for i, row in enumerate(data):
            date_val = str(row['date_operation'])
            doc_type = str(row['type_document'])
            montant = float(row['montant_total'])
            verse = float(row['total_verse'])
            reste = float(row['reste'])
            status = str(row['statut'])
            date_rec = str(row['date_reception'] or '-')
            obs = str(row['observation'] or '')
            
            total_montant += montant
            total_versement += verse
            total_reste += reste
            
            item_date = QTableWidgetItem(date_val)
            item_date.setData(Qt.UserRole, row['id_operation'])
            
            item_doc = QTableWidgetItem(doc_type)
            item_montant = QTableWidgetItem(f"{montant:,.2f}")
            item_verse = QTableWidgetItem(f"{verse:,.2f}")
            item_status = QTableWidgetItem(status)
            item_rec = QTableWidgetItem(date_rec)
            item_obs = QTableWidgetItem(obs)
            
            self.tbl_ledger.setItem(i, 0, item_date)
            self.tbl_ledger.setItem(i, 1, item_doc)
            self.tbl_ledger.setItem(i, 2, item_montant)
            self.tbl_ledger.setItem(i, 3, item_verse)
            self.tbl_ledger.setItem(i, 4, item_status)
            self.tbl_ledger.setItem(i, 5, item_rec)
            self.tbl_ledger.setItem(i, 6, item_obs)
            
        self.tbl_total.clear()
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
        
        self.tbl_total.setItem(0, 1, item_tot_lbl)
        self.tbl_total.setItem(0, 2, item_tot_montant)
        self.tbl_total.setItem(0, 3, item_tot_verse)
        self.tbl_total.setItem(0, 4, item_tot_reste_lbl)
        self.tbl_total.setItem(0, 5, item_tot_reste_val)

    def add_operation(self):
        from ui.partenaires.dialogs import OperationPartenaireDialog
        dlg = OperationPartenaireDialog(self, id_partenaire=self.id_partenaire)
        if dlg.exec():
            self.load_data(self.parent_tab.month, self.parent_tab.year)
            self.parent_tab.load_data()

    def add_payment(self):
        row = self.tbl_ledger.currentRow()
        id_operation = None
        if row >= 0:
            item = self.tbl_ledger.item(row, 0)
            if item:
                id_operation = item.data(Qt.UserRole)
                
        if id_operation == -1:
            QMessageBox.warning(self, "Attention", "Pour payer le solde initial de l'année précédente, veuillez ajouter une opération spécifique.")
            return
            
        from ui.partenaires.dialogs import PaiementPartenaireDialog
        dlg = PaiementPartenaireDialog(self, id_partenaire=self.id_partenaire, id_operation=id_operation)
        if dlg.exec():
            self.load_data(self.parent_tab.month, self.parent_tab.year)
            self.parent_tab.load_data()

    def edit_row(self):
        row = self.tbl_ledger.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner une ligne à modifier.")
            return
            
        item = self.tbl_ledger.item(row, 0)
        if not item:
            return
        id_operation = item.data(Qt.UserRole)
        
        if id_operation == -1:
            QMessageBox.warning(self, "Attention", "Le solde initial est géré via la fiche du partenaire et ne peut pas être modifié d'ici.")
            return
            
        record = data_manager.db.fetch_one("SELECT * FROM Operations_Partenaires WHERE id_operation = %s", (id_operation,))
        if not record:
            return
            
        from ui.partenaires.dialogs import OperationPartenaireDialog
        dlg = OperationPartenaireDialog(self, record=record)
        if dlg.exec():
            self.load_data(self.parent_tab.month, self.parent_tab.year)
            self.parent_tab.load_data()

    def delete_row(self):
        row = self.tbl_ledger.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner une ligne à supprimer.")
            return
            
        item = self.tbl_ledger.item(row, 0)
        if not item:
            return
        id_operation = item.data(Qt.UserRole)
        
        if id_operation == -1:
            QMessageBox.warning(self, "Attention", "Le solde initial ne peut pas être supprimé.")
            return

        ans = QMessageBox.question(self, "Confirmation", "Voulez-vous vraiment supprimer cette opération ? Cela supprimera également tous ses paiements associés.", QMessageBox.Yes | QMessageBox.No)
        if ans == QMessageBox.Yes:
            success, _ = data_manager.db.delete_record("Operations_Partenaires", "id_operation", id_operation)
            if success:
                self.load_data(self.parent_tab.month, self.parent_tab.year)
                self.parent_tab.load_data()


class SousTraitantsTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.month = None
        self.year = None
        self.partner_ledgers = {}
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 1. Create sub-pages
        self.tab_tous, self.tbl_tous, self.tbl_total_tous = self.create_overview_tab(has_toolbar=True)
        self.tab_st, self.tbl_st, self.tbl_total_st = self.create_overview_tab(has_toolbar=False)
        self.tab_conv, self.tbl_conv, self.tbl_total_conv = self.create_overview_tab(has_toolbar=False)
        
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
        self.list_partners = QListWidget()
        self.list_partners.setStyleSheet(
            "QListWidget { border: 1px solid #cfd8dc; border-radius: 4px; background-color: white; }"
            "QListWidget::item { padding: 8px 12px; border-bottom: 1px solid #eceff1; }"
            "QListWidget::item:selected { background-color: #007572; color: white; }"
            "QListWidget::item:hover:!selected { background-color: #f5f6fa; }"
        )
        self.list_partners.currentItemChanged.connect(self.on_detail_partner_changed)
        lay_sidebar.addWidget(self.list_partners)

        # Right side Stacked Widget for ledger views
        self.stack_ledgers = QStackedWidget()
        # Empty placeholder widget for when no partner is selected
        placeholder = QWidget()
        lay_placeholder = QVBoxLayout(placeholder)
        lbl_placeholder = QLabel("Veuillez sélectionner un partenaire dans la liste pour afficher sa fiche.")
        lbl_placeholder.setAlignment(Qt.AlignCenter)
        lbl_placeholder.setStyleSheet("color: #7f8c8d; font-size: 13px; font-style: italic;")
        lay_placeholder.addWidget(lbl_placeholder)
        self.stack_ledgers.addWidget(placeholder)

        lay_details.addWidget(sidebar)
        lay_details.addWidget(self.stack_ledgers, stretch=1)
        
        # 3. Create central Stacked Widget
        self.stack_pages = QStackedWidget()
        self.stack_pages.addWidget(self.tab_tous)
        self.stack_pages.addWidget(self.tab_st)
        self.stack_pages.addWidget(self.tab_conv)
        self.stack_pages.addWidget(self.tab_details)
        
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
            
        self.btn_page_tous = QPushButton(" Tous (Partenaires)")
        self.btn_page_tous.setIcon(get_dynamic_pill_icon(PATH_LIST, 14))
        
        self.btn_page_st = QPushButton(" Sous-Traitants")
        self.btn_page_st.setIcon(get_dynamic_pill_icon(PATH_PARTNER, 14))
        
        self.btn_page_conv = QPushButton(" Conventions")
        self.btn_page_conv.setIcon(get_dynamic_pill_icon(PATH_DOCUMENT, 14))
        
        self.btn_page_details = QPushButton(" Fiches Individuelles")
        self.btn_page_details.setIcon(get_dynamic_pill_icon(PATH_PARTNER, 14))
        
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
        
        for i, btn in enumerate([self.btn_page_tous, self.btn_page_st, self.btn_page_conv, self.btn_page_details]):
            btn.setCheckable(True)
            btn.setStyleSheet(btn_style)
            btn.setCursor(Qt.PointingHandCursor)
            self.btn_group.addButton(btn, i)
            nav_layout.addWidget(btn)
            
        self.btn_page_tous.setChecked(True)
        nav_layout.addStretch()
        
        # Search bar
        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("Rechercher...")
        self.txt_search.setFixedWidth(220)
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
        
        layout.addWidget(nav_widget)
        layout.addWidget(self.stack_pages)
        
        # Wire up signals
        self.btn_group.idClicked.connect(self.on_nav_changed)
        
        self.tbl_tous.doubleClicked.connect(lambda index: self.on_overview_row_double_clicked(self.tbl_tous, index))
        self.tbl_st.doubleClicked.connect(lambda index: self.on_overview_row_double_clicked(self.tbl_st, index))
        self.tbl_conv.doubleClicked.connect(lambda index: self.on_overview_row_double_clicked(self.tbl_conv, index))

    def on_nav_changed(self, page_id):
        self.stack_pages.setCurrentIndex(page_id)
        self.on_search_changed(self.txt_search.text())

    def on_search_changed(self, text):
        text = text.lower().strip()
        current_page = self.stack_pages.currentIndex()
        
        if current_page == 0:
            self.filter_table(self.tbl_tous, self.tbl_total_tous, text)
        elif current_page == 1:
            self.filter_table(self.tbl_st, self.tbl_total_st, text)
        elif current_page == 2:
            self.filter_table(self.tbl_conv, self.tbl_total_conv, text)
        elif current_page == 3:
            first_visible_item = None
            for i in range(self.list_partners.count()):
                item = self.list_partners.item(i)
                visible = text in item.text().lower()
                item.setHidden(not visible)
                if visible and not first_visible_item:
                    first_visible_item = item
            
            current = self.list_partners.currentItem()
            if current and current.isHidden() and first_visible_item:
                self.list_partners.setCurrentItem(first_visible_item)

    def filter_table(self, table, total_table, text):
        tot_montant = 0.0
        tot_versement = 0.0
        tot_reste = 0.0
        tot_precedants = 0.0
        tot_total = 0.0
        
        for row in range(table.rowCount()):
            item_name = table.item(row, 0)
            if item_name:
                match = text in item_name.text().lower()
                table.setRowHidden(row, not match)
                if match:
                    try:
                        tot_montant += float(table.item(row, 1).text().replace(',', ''))
                    except Exception:
                        pass
                    try:
                        tot_versement += float(table.item(row, 2).text().replace(',', ''))
                    except Exception:
                        pass
                    try:
                        tot_reste += float(table.item(row, 5).text().replace(',', ''))
                    except Exception:
                        pass
                    try:
                        tot_precedants += float(table.item(row, 6).text().replace(',', ''))
                    except Exception:
                        pass
                    try:
                        tot_total += float(table.item(row, 7).text().replace(',', ''))
                    except Exception:
                        pass
                        
        item_m = total_table.item(0, 1)
        if item_m:
            item_m.setText(f"{tot_montant:,.2f}")
        item_v = total_table.item(0, 2)
        if item_v:
            item_v.setText(f"{tot_versement:,.2f}")
        item_r = total_table.item(0, 5)
        if item_r:
            item_r.setText(f"{tot_reste:,.2f}")
        item_p = total_table.item(0, 6)
        if item_p:
            item_p.setText(f"{tot_precedants:,.2f}")
        item_t = total_table.item(0, 7)
        if item_t:
            item_t.setText(f"{tot_total:,.2f}")

    def on_overview_row_double_clicked(self, table, index):
        row = index.row()
        item = table.item(row, 0)
        if not item:
            return
        pid = item.data(Qt.UserRole)
        if pid is None:
            return
            
        self.btn_page_details.setChecked(True)
        self.stack_pages.setCurrentIndex(3)
        for i in range(self.list_partners.count()):
            list_item = self.list_partners.item(i)
            if list_item.data(Qt.UserRole) == pid:
                self.list_partners.setCurrentItem(list_item)
                break

    def on_detail_partner_changed(self, current, previous):
        if not current:
            self.stack_ledgers.setCurrentIndex(0)
            return
            
        pid = current.data(Qt.UserRole)
        if pid in self.partner_ledgers:
            widget = self.partner_ledgers[pid]
            self.stack_ledgers.setCurrentWidget(widget)
        else:
            self.stack_ledgers.setCurrentIndex(0)

    def create_overview_tab(self, has_toolbar=False):
        tab_widget = QWidget()
        lay = QVBoxLayout(tab_widget)
        lay.setSpacing(4)
        lay.setContentsMargins(5, 5, 5, 5)
        
        tbl = QTableWidget()
        tbl.setColumnCount(9)
        tbl.setHorizontalHeaderLabels([
            "PARTENAIRE", "MONTANT", "VERSEMENT", "DATE DE RECEPTION", "MODE PAIEMENT", "RESTE", "RESTE MOIS PRECEDANTS", "RESTE TOTAL", "REMARQUES"
        ])
        tbl.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        tbl.setEditTriggers(QTableWidget.NoEditTriggers)
        
        if has_toolbar:
            toolbar = make_table_editable(
                tbl, "Partenaires", "id_partenaire",
                lambda r: tbl.item(r, 0).data(Qt.UserRole) if tbl.item(r, 0) else None,
                PartenaireDialog, self.load_data, self,
                add_callback=self.add_partenaire,
                add_label="Nouveau Partenaire",
            )
            btn_op = QPushButton(" + Opération")
            btn_op.setStyleSheet("background-color: #007572; color: white; border-radius: 4px; padding: 4px 8px; font-weight: bold;")
            btn_op.clicked.connect(self.add_operation)
            
            btn_pay = QPushButton(" + Paiement")
            btn_pay.setStyleSheet("background-color: #37474f; color: white; border-radius: 4px; padding: 4px 8px; font-weight: bold;")
            btn_pay.clicked.connect(self.add_paiement)
            
            toolbar.layout().insertWidget(2, btn_op)
            toolbar.layout().insertWidget(3, btn_pay)
            
            lay.addWidget(toolbar)
            self.tbl_state = tbl
        
        lay.addWidget(tbl)
        
        tbl_total = QTableWidget()
        tbl_total.setColumnCount(9)
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

    def add_partenaire(self):
        dlg = PartenaireDialog(self)
        if dlg.exec():
            self.load_data(getattr(self, "month", None), getattr(self, "year", None))

    def add_operation(self):
        dlg = OperationPartenaireDialog(self)
        row = self.tbl_tous.currentRow()
        if row >= 0 and self.tbl_tous.item(row, 0):
            pid = self.tbl_tous.item(row, 0).data(Qt.UserRole)
            if pid is not None:
                idx = dlg.cb_part.findData(pid)
                if idx >= 0:
                    dlg.cb_part.setCurrentIndex(idx)
        if dlg.exec():
            self.load_data(getattr(self, "month", None), getattr(self, "year", None))

    def add_paiement(self):
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

        prev_selected_id = None
        current_item = self.list_partners.currentItem()
        if current_item:
            prev_selected_id = current_item.data(Qt.UserRole)

        active_index = self.stack_pages.currentIndex()

        partners = data_manager.partenaires.get_partenaires()
        
        # Clear list and stacked widget
        self.list_partners.clear()
        while self.stack_ledgers.count() > 1:
            widget = self.stack_ledgers.widget(1)
            self.stack_ledgers.removeWidget(widget)
            widget.deleteLater()
            
        self.partner_ledgers = {}
        for partner in partners:
            pid = partner['id_partenaire']
            name = partner['nom_partenaire']
            ptype = partner['type_partenaire']
            
            item = QListWidgetItem(name)
            item.setData(Qt.UserRole, pid)
            self.list_partners.addItem(item)
            
            ledger_tab = PartnerDetailTab(pid, name, ptype, self)
            self.stack_ledgers.addWidget(ledger_tab)
            self.partner_ledgers[pid] = ledger_tab

        # 1. Populate TOUS
        data_tous = data_manager.partenaires.get_partenaires_state("TOUS", m, y)
        self.populate_overview_table(self.tbl_tous, self.tbl_total_tous, data_tous)
        
        # 2. Populate SOUS TRAITANTS
        data_st = data_manager.partenaires.get_partenaires_state("SOUS_TRAITANT", m, y)
        self.populate_overview_table(self.tbl_st, self.tbl_total_st, data_st)
        
        # 3. Populate CONVENTIONS
        data_conv = data_manager.partenaires.get_partenaires_state("CONVENTION", m, y)
        self.populate_overview_table(self.tbl_conv, self.tbl_total_conv, data_conv)
        
        # 4. Load detailed data for each partner ledger
        for pid, ledger in self.partner_ledgers.items():
            ledger.load_data(m, y)

        # Restore selection
        if prev_selected_id is not None:
            for i in range(self.list_partners.count()):
                item = self.list_partners.item(i)
                if item.data(Qt.UserRole) == prev_selected_id:
                    self.list_partners.setCurrentItem(item)
                    break
        else:
            if self.list_partners.count() > 0:
                self.list_partners.setCurrentRow(0)
            
        # Restore active tab
        if active_index >= 0 and active_index < self.stack_pages.count():
            self.stack_pages.setCurrentIndex(active_index)
            btn = self.btn_group.button(active_index)
            if btn:
                btn.setChecked(True)
                    
        # Apply search filter if active
        if hasattr(self, 'txt_search'):
            self.on_search_changed(self.txt_search.text())

    def populate_overview_table(self, table, total_table, data):
        S = len(data)
        table.setRowCount(S)
        
        tot_montant = 0.0
        tot_versement = 0.0
        tot_reste = 0.0
        tot_precedants = 0.0
        tot_total = 0.0
        
        for i, row in enumerate(data):
            item_name = QTableWidgetItem(str(row['nom_partenaire']))
            item_name.setData(Qt.UserRole, row['id_partenaire'])
            
            val_montant = float(row['montant'])
            val_versement = float(row['versement'])
            val_reste = float(row['reste'])
            val_precedants = float(row['reste_mois_precedants'])
            val_total = float(row['reste_total'])
            
            tot_montant += val_montant
            tot_versement += val_versement
            tot_reste += val_reste
            tot_precedants += val_precedants
            tot_total += val_total
            
            item_montant = QTableWidgetItem(f"{val_montant:,.2f}")
            item_versement = QTableWidgetItem(f"{val_versement:,.2f}")
            item_reception = QTableWidgetItem(str(row['date_reception'] or '-'))
            item_mode = QTableWidgetItem(str(row['mode_paiement'] or '-'))
            item_reste = QTableWidgetItem(f"{val_reste:,.2f}")
            item_precedants = QTableWidgetItem(f"{val_precedants:,.2f}")
            item_total = QTableWidgetItem(f"{val_total:,.2f}")
            item_remarques = QTableWidgetItem(str(row['remarques'] or ''))
            
            table.setItem(i, 0, item_name)
            table.setItem(i, 1, item_montant)
            table.setItem(i, 2, item_versement)
            table.setItem(i, 3, item_reception)
            table.setItem(i, 4, item_mode)
            table.setItem(i, 5, item_reste)
            table.setItem(i, 6, item_precedants)
            table.setItem(i, 7, item_total)
            table.setItem(i, 8, item_remarques)
            
        total_table.clear()
        
        item_tot_lbl = QTableWidgetItem("Total")
        font = item_tot_lbl.font()
        font.setBold(True)
        item_tot_lbl.setFont(font)
        
        item_tot_montant = QTableWidgetItem(f"{tot_montant:,.2f}")
        item_tot_montant.setFont(font)
        item_tot_verse = QTableWidgetItem(f"{tot_versement:,.2f}")
        item_tot_verse.setFont(font)
        
        item_tot_reste = QTableWidgetItem(f"{tot_reste:,.2f}")
        item_tot_reste.setFont(font)
        item_tot_precedants = QTableWidgetItem(f"{tot_precedants:,.2f}")
        item_tot_precedants.setFont(font)
        item_tot_total = QTableWidgetItem(f"{tot_total:,.2f}")
        item_tot_total.setFont(font)
        
        total_table.setItem(0, 0, item_tot_lbl)
        total_table.setItem(0, 1, item_tot_montant)
        total_table.setItem(0, 2, item_tot_verse)
        total_table.setItem(0, 3, QTableWidgetItem(""))
        total_table.setItem(0, 4, QTableWidgetItem(""))
        total_table.setItem(0, 5, item_tot_reste)
        total_table.setItem(0, 6, item_tot_precedants)
        total_table.setItem(0, 7, item_tot_total)
        total_table.setItem(0, 8, QTableWidgetItem(""))
