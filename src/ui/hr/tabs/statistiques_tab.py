import datetime
import calendar
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QDateEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
    QLineEdit, QMessageBox, QFileDialog
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont, QColor, QIcon

from database import data_manager
from utils.pdf_generator import PdfGenerator


def calc_worked_hours(heure_entree, heure_sortie, etat_jour, heures_sup=0.0, default_day_hours=8.0):
    """
    Calculates total worked hours for a day:
    - If entry and exit times exist, computes time difference + heures_sup.
    - If entry/exit times are missing, uses default_day_hours for PRESENT/GARDE + heures_sup.
    - Returns float rounded to 2 decimal places.
    """
    h_sup = float(heures_sup or 0.0)
    
    if heure_entree and heure_sortie:
        def to_seconds(t):
            if isinstance(t, datetime.timedelta):
                return t.total_seconds()
            elif isinstance(t, datetime.time):
                return t.hour * 3600 + t.minute * 60 + t.second
            elif isinstance(t, str):
                parts = [int(p) for p in t.split(':')]
                return parts[0] * 3600 + parts[1] * 60 + (parts[2] if len(parts) > 2 else 0)
            return 0

        sec_in = to_seconds(heure_entree)
        sec_out = to_seconds(heure_sortie)
        if sec_out >= sec_in:
            diff_hours = (sec_out - sec_in) / 3600.0
        else:
            diff_hours = (86400 - sec_in + sec_out) / 3600.0
        return round(diff_hours + h_sup, 2)

    if etat_jour in ('PRESENT', 'P+'):
        return round(float(default_day_hours or 8.0) + h_sup, 2)
    elif etat_jour in ('GARDE_NUIT', 'GARDE_VENDREDI_JOUR', 'GARDE_VENDREDI_NUIT'):
        return round(float(default_day_hours or 8.0) + h_sup, 2)
    else:
        return 0.0


def format_time_str(t):
    if not t:
        return "--:--"
    if isinstance(t, datetime.timedelta):
        tot_sec = int(t.total_seconds())
        h = (tot_sec // 3600) % 24
        m = (tot_sec % 3600) // 60
        return f"{h:02d}:{m:02d}"
    if isinstance(t, datetime.time):
        return t.strftime("%H:%M")
    if isinstance(t, str):
        return t[:5]
    return str(t)


class StatistiquesTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.apply_preset("Ce mois-ci")
        self.load_data()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(12)

        # ----------------------------------------------------
        # 1. Header Toolbar / Filter Controls
        # ----------------------------------------------------
        filter_card = QFrame()
        filter_card.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
            }
        """)
        filter_layout = QHBoxLayout(filter_card)
        filter_layout.setContentsMargins(12, 10, 12, 10)
        filter_layout.setSpacing(12)

        # Employee Selector
        lbl_emp = QLabel("Employé:")
        lbl_emp.setFont(QFont("Arial", 10, QFont.Bold))
        self.cb_employee = QComboBox()
        self.cb_employee.setMinimumWidth(200)
        self.cb_employee.currentIndexChanged.connect(self.on_employee_changed)
        
        filter_layout.addWidget(lbl_emp)
        filter_layout.addWidget(self.cb_employee)

        filter_layout.addSpacing(10)

        # Quick Presets
        lbl_preset = QLabel("Période:")
        lbl_preset.setFont(QFont("Arial", 10, QFont.Bold))
        self.cb_presets = QComboBox()
        self.cb_presets.addItems([
            "Ce mois-ci",
            "Mois dernier",
            "30 derniers jours",
            "Année en cours",
            "Personnalisé"
        ])
        self.cb_presets.currentTextChanged.connect(self.on_preset_changed)

        filter_layout.addWidget(lbl_preset)
        filter_layout.addWidget(self.cb_presets)

        # Date Pickers
        lbl_du = QLabel("Du:")
        self.dt_start = QDateEdit()
        self.dt_start.setCalendarPopup(True)
        self.dt_start.setDisplayFormat("yyyy-MM-dd")

        lbl_au = QLabel("Au:")
        self.dt_end = QDateEdit()
        self.dt_end.setCalendarPopup(True)
        self.dt_end.setDisplayFormat("yyyy-MM-dd")

        filter_layout.addWidget(lbl_du)
        filter_layout.addWidget(self.dt_start)
        filter_layout.addWidget(lbl_au)
        filter_layout.addWidget(self.dt_end)

        # Action Buttons
        self.btn_refresh = QPushButton("Actualiser")
        self.btn_refresh.setStyleSheet("""
            QPushButton {
                background-color: #1976d2;
                color: white;
                font-weight: bold;
                padding: 6px 16px;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #1565c0; }
        """)
        self.btn_refresh.clicked.connect(self.load_data)

        self.btn_pdf = QPushButton("Exporter PDF")
        self.btn_pdf.setStyleSheet("""
            QPushButton {
                background-color: #388e3c;
                color: white;
                font-weight: bold;
                padding: 6px 16px;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #2e7d32; }
        """)
        self.btn_pdf.clicked.connect(self.export_pdf)

        filter_layout.addWidget(self.btn_refresh)
        filter_layout.addWidget(self.btn_pdf)

        main_layout.addWidget(filter_card)

        # ----------------------------------------------------
        # 2. KPI Summary Cards Grid
        # ----------------------------------------------------
        self.cards_layout = QHBoxLayout()
        self.cards_layout.setSpacing(10)

        self.card_hours = self._create_kpi_card("🕒 Total Heures Travaillées", "0.0 h", "#007572")
        self.card_presents = self._create_kpi_card("📅 Jours Présents", "0 j", "#2e7d32")
        self.card_absences = self._create_kpi_card("⚠️ Jours Absents", "0 j", "#c62828")
        self.card_conges = self._create_kpi_card("🏖️ Congés / C.M", "0 j", "#0277bd")
        self.card_gardes = self._create_kpi_card("🌙 Gardes & Récup", "0 j", "#6a1b9a")
        self.card_hs = self._create_kpi_card("⏰ Heures Sup", "0.0 h", "#f57c00")
        self.card_rate = self._create_kpi_card("📊 Taux de Présence", "0.0 %", "#4527a0")

        self.cards_layout.addWidget(self.card_hours)
        self.cards_layout.addWidget(self.card_presents)
        self.cards_layout.addWidget(self.card_absences)
        self.cards_layout.addWidget(self.card_conges)
        self.cards_layout.addWidget(self.card_gardes)
        self.cards_layout.addWidget(self.card_hs)
        self.cards_layout.addWidget(self.card_rate)

        main_layout.addLayout(self.cards_layout)

        # ----------------------------------------------------
        # 3. Main Views Area (Overview Table vs Detail View)
        # ----------------------------------------------------
        # Search & Mode header
        sub_bar = QHBoxLayout()
        self.lbl_view_title = QLabel("Résumé Global de Tous les Employés")
        self.lbl_view_title.setFont(QFont("Arial", 11, QFont.Bold))
        self.lbl_view_title.setStyleSheet("color: #2c3e50;")

        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("🔍 Rechercher par nom ou fonction...")
        self.txt_search.setMaximumWidth(300)
        self.txt_search.textChanged.connect(self.filter_table_search)

        sub_bar.addWidget(self.lbl_view_title)
        sub_bar.addStretch()
        sub_bar.addWidget(self.txt_search)
        main_layout.addLayout(sub_bar)

        # Table for All Employees (Overview Mode)
        self.tbl_overview = QTableWidget()
        self.tbl_overview.setColumnCount(10)
        self.tbl_overview.setHorizontalHeaderLabels([
            "N°", "NOM / PRÉNOM", "FONCTION", "JOURS PRÉSENTS", 
            "JOURS ABSENTS", "CONGÉS / C.M", "GARDES / RÉCUP", 
            "HEURES TRAVAILLÉES", "HEURES SUP", "TAUX PRÉSENCE (%)"
        ])
        self.tbl_overview.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl_overview.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.tbl_overview.setSelectionBehavior(QTableWidget.SelectRows)
        self.tbl_overview.setSelectionMode(QTableWidget.SingleSelection)
        self.tbl_overview.setAlternatingRowColors(True)
        self.tbl_overview.cellDoubleClicked.connect(self.on_overview_double_click)

        # Table for Single Employee Daily Log (Detail Mode)
        self.tbl_detail = QTableWidget()
        self.tbl_detail.setColumnCount(8)
        self.tbl_detail.setHorizontalHeaderLabels([
            "DATE", "JOUR", "STATUT / ÉTAT", "HEURE ENTRÉE", 
            "HEURE SORTIE", "HEURES TRAVAILLÉES", "HEURES SUP", "REMARQUE / DÉTAILS"
        ])
        self.tbl_detail.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl_detail.setSelectionBehavior(QTableWidget.SelectRows)
        self.tbl_detail.setAlternatingRowColors(True)
        self.tbl_detail.hide()

        main_layout.addWidget(self.tbl_overview)
        main_layout.addWidget(self.tbl_detail)

        self.populate_employee_combo()

    def _create_kpi_card(self, title, default_val, color_hex):
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: #ffffff;
                border-left: 5px solid {color_hex};
                border-top: 1px solid #e0e0e0;
                border-right: 1px solid #e0e0e0;
                border-bottom: 1px solid #e0e0e0;
                border-radius: 6px;
            }}
        """)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(2)

        lbl_t = QLabel(title)
        lbl_t.setFont(QFont("Arial", 8, QFont.Bold))
        lbl_t.setStyleSheet("color: #616161;")

        lbl_v = QLabel(default_val)
        lbl_v.setFont(QFont("Arial", 14, QFont.Bold))
        lbl_v.setStyleSheet(f"color: {color_hex};")
        frame.val_label = lbl_v

        layout.addWidget(lbl_t)
        layout.addWidget(lbl_v)
        return frame

    def populate_employee_combo(self):
        self.cb_employee.blockSignals(True)
        self.cb_employee.clear()
        self.cb_employee.addItem("Tous les employés", None)
        
        employes = data_manager.hr.get_employes_list()
        for emp in employes:
            self.cb_employee.addItem(f"{emp['nom_prenom']}", emp['id_employe'])
        self.cb_employee.blockSignals(False)

    def on_preset_changed(self, text):
        self.apply_preset(text)
        self.load_data()

    def apply_preset(self, preset_name):
        today = QDate.currentDate()

        if preset_name == "Ce mois-ci":
            start_date = QDate(today.year(), today.month(), 1)
            _, days_in_m = calendar.monthrange(today.year(), today.month())
            end_date = QDate(today.year(), today.month(), days_in_m)
        elif preset_name == "Mois dernier":
            first_of_curr = QDate(today.year(), today.month(), 1)
            prev_month = first_of_curr.addDays(-1)
            start_date = QDate(prev_month.year(), prev_month.month(), 1)
            _, days_in_m = calendar.monthrange(prev_month.year(), prev_month.month())
            end_date = QDate(prev_month.year(), prev_month.month(), days_in_m)
        elif preset_name == "30 derniers jours":
            end_date = today
            start_date = today.addDays(-30)
        elif preset_name == "Année en cours":
            start_date = QDate(today.year(), 1, 1)
            end_date = QDate(today.year(), 12, 31)
        else: # Personnalisé
            return

        self.dt_start.blockSignals(True)
        self.dt_end.blockSignals(True)
        self.dt_start.setDate(start_date)
        self.dt_end.setDate(end_date)
        self.dt_start.blockSignals(False)
        self.dt_end.blockSignals(False)

    def on_employee_changed(self, index):
        self.load_data()

    def filter_table_search(self, text):
        text = text.lower().strip()
        target_table = self.tbl_overview if self.tbl_overview.isVisible() else self.tbl_detail
        for r in range(target_table.rowCount()):
            match = False
            for c in range(target_table.columnCount()):
                item = target_table.item(r, c)
                if item and text in item.text().lower():
                    match = True
                    break
            target_table.setRowHidden(r, not match)

    def on_overview_double_click(self, row, col):
        id_item = self.tbl_overview.item(row, 0)
        if not id_item:
            return
        eid = id_item.data(Qt.UserRole)
        if eid:
            idx = self.cb_employee.findData(eid)
            if idx >= 0:
                self.cb_employee.setCurrentIndex(idx)

    def load_data(self, month=None, year=None):
        # Support optional month/year filter passed from parent HRView
        if month and year:
            start_date = QDate(year, month, 1)
            _, days_in_m = calendar.monthrange(year, month)
            end_date = QDate(year, month, days_in_m)
            self.dt_start.blockSignals(True)
            self.dt_end.blockSignals(True)
            self.dt_start.setDate(start_date)
            self.dt_end.setDate(end_date)
            self.dt_start.blockSignals(False)
            self.dt_end.blockSignals(False)

        start_str = self.dt_start.date().toString("yyyy-MM-dd")
        end_str = self.dt_end.date().toString("yyyy-MM-dd")
        selected_emp_id = self.cb_employee.currentData()

        # Fetch records
        records = data_manager.hr.get_presences_stats_by_period(start_str, end_str, selected_emp_id)

        if selected_emp_id is None:
            # Mode: All Employees Overview
            self.lbl_view_title.setText(f"Résumé Global - Période du {start_str} au {end_str}")
            self.tbl_overview.show()
            self.tbl_detail.hide()
            self._render_overview_mode(records, start_str, end_str)
        else:
            # Mode: Single Employee Detail View
            emp_name = self.cb_employee.currentText()
            self.lbl_view_title.setText(f"SJournal التفصيلي للموظف: {emp_name} ({start_str} au {end_str})")
            self.tbl_overview.hide()
            self.tbl_detail.show()
            self._render_detail_mode(records, selected_emp_id)

    def _render_overview_mode(self, records, start_str, end_str):
        employes = data_manager.hr.get_drh_master_list()
        
        # Aggregate records by employee
        emp_stats = {}
        for emp in employes:
            eid = emp['id_employe']
            emp_stats[eid] = {
                'id_employe': eid,
                'nom_prenom': emp['nom_prenom'],
                'fonction': emp.get('fonction') or '---',
                'heures_base': float(emp.get('heures_travail_jour') or 8.0),
                'presents': 0,
                'absents': 0,
                'conges': 0,
                'gardes': 0,
                'heures_travaillees': 0.0,
                'heures_sup': 0.0,
                'total_records': 0
            }

        for r in records:
            eid = r['id_employe']
            if eid not in emp_stats:
                emp_stats[eid] = {
                    'id_employe': eid,
                    'nom_prenom': r['nom_prenom'],
                    'fonction': r.get('fonction') or '---',
                    'heures_base': float(r.get('heures_travail_jour') or 8.0),
                    'presents': 0,
                    'absents': 0,
                    'conges': 0,
                    'gardes': 0,
                    'heures_travaillees': 0.0,
                    'heures_sup': 0.0,
                    'total_records': 0
                }
            
            st = emp_stats[eid]
            st['total_records'] += 1
            etat = r['etat_jour']
            h_sup = float(r.get('heures_sup') or 0.0)
            st['heures_sup'] += h_sup

            w_hours = calc_worked_hours(
                r.get('heure_entree'), r.get('heure_sortie'),
                etat, h_sup, st['heures_base']
            )
            st['heures_travaillees'] += w_hours

            if etat in ('PRESENT', 'P+'):
                st['presents'] += 1
            elif etat == 'ABSENCE':
                st['absents'] += 1
            elif etat in ('CONGE', 'CONGE_MALADIE'):
                st['conges'] += 1
            elif etat in ('GARDE_NUIT', 'GARDE_VENDREDI_JOUR', 'GARDE_VENDREDI_NUIT', 'RECUPERATION'):
                st['gardes'] += 1

        # Populate KPI totals across all employees
        tot_hours = sum(s['heures_travaillees'] for s in emp_stats.values())
        tot_pres = sum(s['presents'] for s in emp_stats.values())
        tot_abs = sum(s['absents'] for s in emp_stats.values())
        tot_cong = sum(s['conges'] for s in emp_stats.values())
        tot_gard = sum(s['gardes'] for s in emp_stats.values())
        tot_hs = sum(s['heures_sup'] for s in emp_stats.values())

        grand_total_days = tot_pres + tot_abs + tot_cong + tot_gard
        attendance_rate = ((tot_pres + tot_gard) / grand_total_days * 100.0) if grand_total_days > 0 else 0.0

        self.card_hours.val_label.setText(f"{tot_hours:.1f} h")
        self.card_presents.val_label.setText(f"{tot_pres} j")
        self.card_absences.val_label.setText(f"{tot_abs} j")
        self.card_conges.val_label.setText(f"{tot_cong} j")
        self.card_gardes.val_label.setText(f"{tot_gard} j")
        self.card_hs.val_label.setText(f"{tot_hs:.1f} h")
        self.card_rate.val_label.setText(f"{attendance_rate:.1f} %")

        # Fill table
        self.tbl_overview.setRowCount(len(emp_stats))
        for row_idx, (eid, st) in enumerate(emp_stats.items()):
            item_id = QTableWidgetItem(str(eid))
            item_id.setData(Qt.UserRole, eid)
            item_id.setTextAlignment(Qt.AlignCenter)

            item_nom = QTableWidgetItem(st['nom_prenom'])
            item_func = QTableWidgetItem(st['fonction'])
            
            item_pres = QTableWidgetItem(f"{st['presents']} j")
            item_pres.setTextAlignment(Qt.AlignCenter)
            item_pres.setForeground(QColor("#2e7d32"))

            item_abs = QTableWidgetItem(f"{st['absents']} j")
            item_abs.setTextAlignment(Qt.AlignCenter)
            if st['absents'] > 0:
                item_abs.setForeground(QColor("#c62828"))
                item_abs.setFont(QFont("Arial", -1, QFont.Bold))

            item_cong = QTableWidgetItem(f"{st['conges']} j")
            item_cong.setTextAlignment(Qt.AlignCenter)

            item_gard = QTableWidgetItem(f"{st['gardes']} j")
            item_gard.setTextAlignment(Qt.AlignCenter)

            item_hrs = QTableWidgetItem(f"{st['heures_travaillees']:.1f} h")
            item_hrs.setTextAlignment(Qt.AlignCenter)
            item_hrs.setFont(QFont("Arial", -1, QFont.Bold))

            item_hs = QTableWidgetItem(f"{st['heures_sup']:.1f} h")
            item_hs.setTextAlignment(Qt.AlignCenter)

            tot_emp_days = st['presents'] + st['absents'] + st['conges'] + st['gardes']
            rate = ((st['presents'] + st['gardes']) / tot_emp_days * 100.0) if tot_emp_days > 0 else 0.0
            item_rate = QTableWidgetItem(f"{rate:.1f} %")
            item_rate.setTextAlignment(Qt.AlignCenter)
            item_rate.setFont(QFont("Arial", -1, QFont.Bold))
            if rate >= 90:
                item_rate.setForeground(QColor("#2e7d32"))
            elif rate >= 75:
                item_rate.setForeground(QColor("#f57c00"))
            else:
                item_rate.setForeground(QColor("#c62828"))

            self.tbl_overview.setItem(row_idx, 0, item_id)
            self.tbl_overview.setItem(row_idx, 1, item_nom)
            self.tbl_overview.setItem(row_idx, 2, item_func)
            self.tbl_overview.setItem(row_idx, 3, item_pres)
            self.tbl_overview.setItem(row_idx, 4, item_abs)
            self.tbl_overview.setItem(row_idx, 5, item_cong)
            self.tbl_overview.setItem(row_idx, 6, item_gard)
            self.tbl_overview.setItem(row_idx, 7, item_hrs)
            self.tbl_overview.setItem(row_idx, 8, item_hs)
            self.tbl_overview.setItem(row_idx, 9, item_rate)

        if self.txt_search.text():
            self.filter_table_search(self.txt_search.text())

    def _render_detail_mode(self, records, id_employe):
        fr_days = {0: "Lundi", 1: "Mardi", 2: "Mercredi", 3: "Jeudi", 4: "Vendredi", 5: "Samedi", 6: "Dimanche"}
        
        etat_labels = {
            'PRESENT': 'Présent',
            'P+': 'Présent + HS',
            'RECUPERATION': 'Récupération',
            'ABSENCE': 'Absence',
            'CONGE_MALADIE': 'Congé Maladie',
            'CONGE': 'Congé Payé',
            'GARDE_NUIT': 'Garde Nuit',
            'GARDE_VENDREDI_JOUR': 'Garde Ven-Jour',
            'GARDE_VENDREDI_NUIT': 'Garde Ven-Nuit',
            'NON_CONSIDERE': 'Non Considéré'
        }

        tot_hours = 0.0
        tot_pres = 0
        tot_abs = 0
        tot_cong = 0
        tot_gard = 0
        tot_hs = 0.0

        self.tbl_detail.setRowCount(len(records))

        for r_idx, r in enumerate(records):
            dt_presence = r['date_presence']
            if isinstance(dt_presence, (datetime.date, datetime.datetime)):
                date_str = dt_presence.strftime("%Y-%m-%d")
                weekday_str = fr_days[dt_presence.weekday()]
            else:
                date_str = str(dt_presence)
                weekday_str = ""

            etat = r['etat_jour']
            h_sup = float(r.get('heures_sup') or 0.0)
            h_base = float(r.get('heures_travail_jour') or 8.0)
            
            entree_str = format_time_str(r.get('heure_entree'))
            sortie_str = format_time_str(r.get('heure_sortie'))

            w_hours = calc_worked_hours(r.get('heure_entree'), r.get('heure_sortie'), etat, h_sup, h_base)
            tot_hours += w_hours
            tot_hs += h_sup

            if etat in ('PRESENT', 'P+'): tot_pres += 1
            elif etat == 'ABSENCE': tot_abs += 1
            elif etat in ('CONGE', 'CONGE_MALADIE'): tot_cong += 1
            elif etat in ('GARDE_NUIT', 'GARDE_VENDREDI_JOUR', 'GARDE_VENDREDI_NUIT', 'RECUPERATION'): tot_gard += 1

            # Populate table row
            item_date = QTableWidgetItem(date_str)
            item_date.setTextAlignment(Qt.AlignCenter)
            
            item_jour = QTableWidgetItem(weekday_str)
            item_jour.setTextAlignment(Qt.AlignCenter)

            etat_text = etat_labels.get(etat, etat)
            item_etat = QTableWidgetItem(etat_text)
            item_etat.setTextAlignment(Qt.AlignCenter)
            item_etat.setFont(QFont("Arial", -1, QFont.Bold))

            # Apply color to etat
            if etat in ('PRESENT', 'P+'):
                item_etat.setForeground(QColor("#2e7d32"))
            elif etat == 'ABSENCE':
                item_etat.setForeground(QColor("#c62828"))
                item_etat.setBackground(QColor("#ffebee"))
            elif etat in ('CONGE', 'CONGE_MALADIE'):
                item_etat.setForeground(QColor("#0277bd"))
            elif 'GARDE' in etat or etat == 'RECUPERATION':
                item_etat.setForeground(QColor("#6a1b9a"))

            item_entree = QTableWidgetItem(entree_str)
            item_entree.setTextAlignment(Qt.AlignCenter)

            item_sortie = QTableWidgetItem(sortie_str)
            item_sortie.setTextAlignment(Qt.AlignCenter)

            item_wh = QTableWidgetItem(f"{w_hours:.1f} h")
            item_wh.setTextAlignment(Qt.AlignCenter)

            item_hs_col = QTableWidgetItem(f"{h_sup:.1f} h" if h_sup > 0 else "-")
            item_hs_col.setTextAlignment(Qt.AlignCenter)

            item_rem = QTableWidgetItem("")

            self.tbl_detail.setItem(r_idx, 0, item_date)
            self.tbl_detail.setItem(r_idx, 1, item_jour)
            self.tbl_detail.setItem(r_idx, 2, item_etat)
            self.tbl_detail.setItem(r_idx, 3, item_entree)
            self.tbl_detail.setItem(r_idx, 4, item_sortie)
            self.tbl_detail.setItem(r_idx, 5, item_wh)
            self.tbl_detail.setItem(r_idx, 6, item_hs_col)
            self.tbl_detail.setItem(r_idx, 7, item_rem)

        grand_total_days = tot_pres + tot_abs + tot_cong + tot_gard
        attendance_rate = ((tot_pres + tot_gard) / grand_total_days * 100.0) if grand_total_days > 0 else 0.0

        self.card_hours.val_label.setText(f"{tot_hours:.1f} h")
        self.card_presents.val_label.setText(f"{tot_pres} j")
        self.card_absences.val_label.setText(f"{tot_abs} j")
        self.card_conges.val_label.setText(f"{tot_cong} j")
        self.card_gardes.val_label.setText(f"{tot_gard} j")
        self.card_hs.val_label.setText(f"{tot_hs:.1f} h")
        self.card_rate.val_label.setText(f"{attendance_rate:.1f} %")

        if self.txt_search.text():
            self.filter_table_search(self.txt_search.text())

    def export_pdf(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Enregistrer le rapport PDF", "Rapport_Statistiques_RH.pdf", "Fichiers PDF (*.pdf)"
        )
        if not file_path:
            return

        start_str = self.dt_start.date().toString("yyyy-MM-dd")
        end_str = self.dt_end.date().toString("yyyy-MM-dd")
        emp_name = self.cb_employee.currentText()

        # Build HTML table for PDF
        table_html = f"""
        <h2 style="text-align: center; color: #007572;">Rapport Statistique des Présences & Heures de Travail</h2>
        <p style="text-align: center;"><b>Employé / Cible:</b> {emp_name} | <b>Période:</b> Du {start_str} Au {end_str}</p>
        
        <table border="1" cellspacing="0" cellpadding="5" style="width:100%; border-collapse: collapse; font-size: 11px;">
            <thead>
                <tr style="background-color: #007572; color: white;">
        """

        current_table = self.tbl_overview if self.tbl_overview.isVisible() else self.tbl_detail
        
        for c in range(current_table.columnCount()):
            header_text = current_table.horizontalHeaderItem(c).text()
            table_html += f"<th>{header_text}</th>"
        table_html += "</tr></thead><tbody>"

        for r in range(current_table.rowCount()):
            if current_table.isRowHidden(r):
                continue
            bg_color = "#f9f9f9" if r % 2 == 1 else "#ffffff"
            table_html += f"<tr style='background-color: {bg_color};'>"
            for c in range(current_table.columnCount()):
                item = current_table.item(r, c)
                val = item.text() if item else ""
                table_html += f"<td style='text-align:center;'>{val}</td>"
            table_html += "</tr>"

        table_html += "</tbody></table>"

        pdf_gen = PdfGenerator()
        pdf_gen.generate_pdf(file_path, f" - Statistiques RH ({emp_name})", table_html)

        QMessageBox.information(
            self, "Exportation Réussie", f"Le rapport PDF a été généré avec succès :\n{file_path}"
        )
