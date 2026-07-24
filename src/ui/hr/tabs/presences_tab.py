from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QMenu,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QScroller
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QColor, QFont, QAction
from database import data_manager
import calendar
import datetime

class PresencesTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.month = None
        self.year = None
        self.zoom_factor = 1.0
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(4)

        # Legend
        legend_layout = QHBoxLayout()
        legend_text = (
            "<b>Légende:</b> "
            "<span style='color:#2e7d32'>P</span>: Présent | "
            "<span style='color:#1565c0'>P+</span>: Présent + HS | "
            "<span style='color:#f57f17'>REC</span>: Récupération | "
            "<span style='color:#c62828'>ABS</span>: Absence | "
            "<span style='color:#0277bd'>C.M</span>: Congé Maladie | "
            "<span style='color:#00838f'>C</span>: Congé | "
            "<span style='color:#4527a0'>G</span>: Garde Nuit | "
            "<span style='color:#6a1b9a'>GV-J</span>: Garde Ven-Jour | "
            "<span style='color:#ad1457'>GV-N</span>: Garde Ven-Nuit"
        )
        lbl_legend = QLabel(legend_text)
        legend_layout.addWidget(lbl_legend)
        legend_layout.addStretch()
        
        lbl_info = QLabel("<i>(Utilisez Ctrl + Molette pour Zoomer)</i>")
        lbl_info.setStyleSheet("color: #757575;")
        legend_layout.addWidget(lbl_info)
        
        layout.addLayout(legend_layout)

        self.tbl_presences = QTableWidget()
        self.tbl_presences.setAlternatingRowColors(True)
        self.tbl_presences.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # Enable zoom event
        self.tbl_presences.wheelEvent = self.custom_wheel_event
        
        # Enable Drag to Scroll (Pan)
        QScroller.grabGesture(self.tbl_presences.viewport(), QScroller.LeftMouseButtonGesture)
        
        # Enable Context Menu
        self.tbl_presences.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tbl_presences.customContextMenuRequested.connect(self.show_context_menu)
        
        layout.addWidget(self.tbl_presences)
        
        self.tbl_presences.cellChanged.connect(self.on_cell_changed)
        self.tbl_presences.cellDoubleClicked.connect(self.on_cell_double_clicked)

    def show_context_menu(self, pos):
        item = self.tbl_presences.itemAt(pos)
        if not item:
            return
            
        row = item.row()
        col = item.column()
        
        # If right clicked on Remarques column
        if col == self.tbl_presences.columnCount() - 1:
            menu = QMenu(self)
            action_edit = menu.addAction("Éditer la remarque")
            selected = menu.exec(self.tbl_presences.viewport().mapToGlobal(pos))
            if selected == action_edit:
                self.on_cell_double_clicked(row, col)
            return
            
        # Only day columns
        if col < 3 or col >= self.tbl_presences.columnCount() - 1:
            return
            
        type_row = self.tbl_presences.item(row, 2).text()
        
        menu = QMenu(self.tbl_presences)
        menu.setStyleSheet("QMenu { font-size: 14px; font-weight: bold; } QMenu::item { padding: 5px 20px; }")
        
        actions = []
        if type_row == 'JOUR':
            actions = [
                ("EFFACER", ""),
                ("Présent (P)", "P"),
                ("Présent + HS (P+)", "P+"),
                ("Récupération (REC)", "REC"),
                ("Absence (ABS)", "ABS"),
                ("Congé Maladie (C.M)", "C.M"),
                ("Congé (C)", "C")
            ]
        elif type_row == 'GARDE':
            actions = [
                ("EFFACER", ""),
                ("Garde Nuit (G)", "G"),
                ("Garde Ven-Jour (GV-J)", "GV-J"),
                ("Garde Ven-Nuit (GV-N)", "GV-N")
            ]
            
        for text, val in actions:
            action = QAction(text, self)
            action.setData(val)
            menu.addAction(action)
            
        selected_action = menu.exec(self.tbl_presences.viewport().mapToGlobal(pos))
        if selected_action:
            val = selected_action.data()
            item.setText(val) # This automatically triggers cellChanged and saves to DB

    def custom_wheel_event(self, event):
        if event.modifiers() == Qt.ControlModifier:
            delta = event.angleDelta().y()
            if delta > 0:
                self.zoom_factor += 0.1
            else:
                self.zoom_factor -= 0.1
                
            self.zoom_factor = max(0.5, min(self.zoom_factor, 3.0))
            self.apply_zoom()
            event.accept()
        else:
            QTableWidget.wheelEvent(self.tbl_presences, event)

    def apply_zoom(self):
        # Update fonts
        font_size = max(6, int(10 * self.zoom_factor))
        f = self.tbl_presences.font()
        f.setPointSize(font_size)
        self.tbl_presences.setFont(f)
        
        # Update row heights
        self.tbl_presences.verticalHeader().setDefaultSectionSize(int(25 * self.zoom_factor))
        
        # Update column widths
        if self.tbl_presences.columnCount() > 0:
            self.tbl_presences.setColumnWidth(0, int(45 * self.zoom_factor))  # N°
            self.tbl_presences.setColumnWidth(1, int(200 * self.zoom_factor)) # Employe
            self.tbl_presences.setColumnWidth(2, int(70 * self.zoom_factor))  # Type
            
            for c in range(3, self.tbl_presences.columnCount() - 1):
                self.tbl_presences.setColumnWidth(c, int(55 * self.zoom_factor)) # Days
                
            self.tbl_presences.setColumnWidth(self.tbl_presences.columnCount() - 1, int(200 * self.zoom_factor)) # Remarques

    def load_data(self, month=None, year=None):
        if month is not None:
            self.month = month
        if year is not None:
            self.year = year
            
        m = getattr(self, "month", None)
        y = getattr(self, "year", None)
        if not m or not y:
            m = QDate.currentDate().month() if not m else m
            y = QDate.currentDate().year() if not y else y
            
        self.tbl_presences.blockSignals(True)
        
        try:
            _, days_in_month = calendar.monthrange(y, m)
        except Exception:
            days_in_month = 31

        # French day abbreviations mapping
        fr_days = {0: "Lun", 1: "Mar", 2: "Mer", 3: "Jeu", 4: "Ven", 5: "Sam", 6: "Dim"}

        headers = ["N°\n", "Employé\n", "TYPE\n"]
        for d in range(1, days_in_month + 1):
            dt = datetime.date(y, m, d)
            day_str = fr_days[dt.weekday()]
            headers.append(f"{d:02d}\n{day_str}")
        headers.append("Remarques\n")
        
        self.tbl_presences.clear()
        self.tbl_presences.setColumnCount(len(headers))
        self.tbl_presences.setHorizontalHeaderLabels(headers)
        
        employes = data_manager.hr.get_employes_list()
        matrix = data_manager.hr.get_monthly_presences_matrix(m, y)
        remarques_dict = data_manager.hr.get_monthly_remarques(m, y)
        
        self.tbl_presences.setRowCount(len(employes) * 2)
        
        row_idx = 0
        for emp in employes:
            eid = emp['id_employe']
            nom = emp['nom_prenom']
            
            emp_matrix = matrix.get(eid, {})
            
            # We only populate the ID and Name on the first row (JOUR), and then merge.
            
            # --- JOUR ROW ---
            start_row = row_idx
            item_n1 = QTableWidgetItem(str(eid))
            item_n1.setData(Qt.UserRole, eid) # Store emp ID
            item_n1.setFlags(item_n1.flags() & ~Qt.ItemIsEditable)
            item_n1.setTextAlignment(Qt.AlignCenter)
            
            item_nom1 = QTableWidgetItem(nom)
            item_nom1.setFlags(item_nom1.flags() & ~Qt.ItemIsEditable)
            item_nom1.setTextAlignment(Qt.AlignCenter)
            
            item_type1 = QTableWidgetItem("JOUR")
            item_type1.setFlags(item_type1.flags() & ~Qt.ItemIsEditable)
            item_type1.setBackground(QColor("#e3f2fd"))
            item_type1.setFont(QFont("Arial", -1, QFont.Bold))
            
            self.tbl_presences.setItem(row_idx, 0, item_n1)
            self.tbl_presences.setItem(row_idx, 1, item_nom1)
            self.tbl_presences.setItem(row_idx, 2, item_type1)
            
            for d in range(1, days_in_month + 1):
                val = emp_matrix.get(d, {}).get('JOUR', '')
                item_day = QTableWidgetItem(val)
                item_day.setTextAlignment(Qt.AlignCenter)
                
                # Setup weekend background color
                dt = datetime.date(y, m, d)
                if dt.weekday() in (4, 5): # Vendredi = 4, Samedi = 5
                    item_day.setBackground(QColor("#f5f5f5"))
                    item_day.setData(Qt.UserRole + 1, "#f5f5f5") # save default color
                else:
                    item_day.setData(Qt.UserRole + 1, "#ffffff")
                    
                heure_entree = emp_matrix.get(d, {}).get('heure_entree')
                heure_sortie = emp_matrix.get(d, {}).get('heure_sortie')
                    
                self._apply_color_to_item(item_day, val, heure_entree, heure_sortie)
                self.tbl_presences.setItem(row_idx, 2 + d, item_day)
                
            remarque_txt = remarques_dict.get(eid, "")
            item_rem1 = QTableWidgetItem(remarque_txt)
            item_rem1.setFlags(item_rem1.flags() & ~Qt.ItemIsEditable)
            self.tbl_presences.setItem(row_idx, 3 + days_in_month, item_rem1)
            
            # --- GARDE ROW ---
            row_idx += 1
            
            # We don't populate column 0 and 1 for the GARDE row, we just leave them empty because we will merge
            
            item_type2 = QTableWidgetItem("GARDE")
            item_type2.setFlags(item_type2.flags() & ~Qt.ItemIsEditable)
            item_type2.setBackground(QColor("#fff3e0"))
            item_type2.setFont(QFont("Arial", -1, QFont.Bold))
            
            self.tbl_presences.setItem(row_idx, 2, item_type2)
            
            for d in range(1, days_in_month + 1):
                val = emp_matrix.get(d, {}).get('GARDE', '')
                item_day = QTableWidgetItem(val)
                item_day.setTextAlignment(Qt.AlignCenter)
                
                dt = datetime.date(y, m, d)
                if dt.weekday() in (4, 5):
                    item_day.setBackground(QColor("#f5f5f5"))
                    item_day.setData(Qt.UserRole + 1, "#f5f5f5")
                else:
                    item_day.setData(Qt.UserRole + 1, "#ffffff")
                    
                self._apply_color_to_item(item_day, val)
                self.tbl_presences.setItem(row_idx, 2 + d, item_day)
                
            item_rem2 = QTableWidgetItem("")
            item_rem2.setFlags(item_rem2.flags() & ~Qt.ItemIsEditable)
            self.tbl_presences.setItem(row_idx, 3 + days_in_month, item_rem2)
            
            # Merge Employee ID and Name cells vertically across the 2 rows
            self.tbl_presences.setSpan(start_row, 0, 2, 1)
            self.tbl_presences.setSpan(start_row, 1, 2, 1)
            self.tbl_presences.setSpan(start_row, 3 + days_in_month, 2, 1)
            
            row_idx += 1

        self.apply_zoom()
        self.tbl_presences.blockSignals(False)

    def on_cell_changed(self, row, col):
        # Only day columns are editable
        if col < 3 or col >= self.tbl_presences.columnCount() - 1:
            return
            
        item = self.tbl_presences.item(row, col)
        if not item:
            return
            
        val = item.text().strip().upper()
        # Enforce valid value or empty
        valid_jour = ['', 'P', 'P+', 'REC', 'ABS', 'C.M', 'CM', 'C']
        valid_garde = ['', 'G', 'GV-J', 'GV-N']
        
        type_row = self.tbl_presences.item(row, 2).text()
        
        if type_row == 'JOUR' and val not in valid_jour:
            self.tbl_presences.blockSignals(True)
            item.setText("")
            self.tbl_presences.blockSignals(False)
            val = ""
            
        if type_row == 'GARDE' and val not in valid_garde:
            self.tbl_presences.blockSignals(True)
            item.setText("")
            self.tbl_presences.blockSignals(False)
            val = ""
            
        # Re-set text to formatted upper case
        self.tbl_presences.blockSignals(True)
        item.setText(val)
        
        # Save to DB first to ensure row exists
        # For GARDE rows, column 0 is None because it's merged from the row above
        id_item = self.tbl_presences.item(row, 0)
        if not id_item:
            id_item = self.tbl_presences.item(row - 1, 0)
            
        eid = id_item.data(Qt.UserRole)
        day = col - 2
        m = getattr(self, "month", QDate.currentDate().month())
        y = getattr(self, "year", QDate.currentDate().year())
        date_str = f"{y}-{m:02d}-{day:02d}"
        
        data_manager.hr.upsert_presence(eid, date_str, type_row, val)
        
        # Fetch times from DB if it's P
        h_entree, h_sortie = None, None
        if val in ('P', 'P+'):
            record = data_manager.hr.get_presence_hours(eid, date_str)
            if record:
                h_entree = record.get('heure_entree')
                h_sortie = record.get('heure_sortie')
        
        # Apply color based on DB state
        self._apply_color_to_item(item, val, h_entree, h_sortie)
        
        self.tbl_presences.blockSignals(False)
        self.tbl_presences.clearSelection()
        
    def _apply_color_to_item(self, item, val, heure_entree=None, heure_sortie=None):
        default_color = item.data(Qt.UserRole + 1) or "#ffffff"
        color = default_color
        
        if val in ('P', 'P+'):
            if not heure_entree and not heure_sortie:
                color = "#ff9999" # Stronger Red (No times)
            elif heure_entree and not heure_sortie:
                color = "#ffcc99" # Stronger Orange (Only entry time)
            else:
                color = default_color # Normal (Both times confirmed)
        elif val == 'ABS': color = "#ffebee" # Light red
        elif val in ('G', 'GV-J', 'GV-N'): color = "#f3e5f5" # Light purple
        elif val == 'REC': color = "#fff8e1" # Light yellow
        
        item.setBackground(QColor(color))
        
        # Bold font for filled values
        f = item.font()
        f.setBold(bool(val))
        item.setFont(f)

    def on_cell_double_clicked(self, row, col):
        if col < 3 or col >= self.tbl_presences.columnCount() - 1:
            if col == self.tbl_presences.columnCount() - 1:
                # Remarques column clicked
                id_item = self.tbl_presences.item(row, 0)
                if not id_item:
                    id_item = self.tbl_presences.item(row - 1, 0)
                eid = id_item.data(Qt.UserRole)
                nom_prenom = self.tbl_presences.item(id_item.row(), 1).text()
                current_rem = self.tbl_presences.item(id_item.row(), col).text()
                
                from ui.hr.dialogs import RemarquePresenceDialog
                dlg = RemarquePresenceDialog(eid, nom_prenom, current_rem, self)
                if dlg.exec():
                    new_rem = dlg.get_remarque()
                    m = getattr(self, "month", QDate.currentDate().month())
                    y = getattr(self, "year", QDate.currentDate().year())
                    data_manager.hr.upsert_monthly_remarque(eid, m, y, new_rem)
                    self.tbl_presences.item(id_item.row(), col).setText(new_rem)
                return
            return
            
        item = self.tbl_presences.item(row, col)
        if not item:
            return
            
        val = item.text().strip().upper()
        if val in ('P', 'P+'):
            eid = self.tbl_presences.item(row, 0).data(Qt.UserRole)
            nom_prenom = self.tbl_presences.item(row, 1).text()
            
            day = col - 2
            m = getattr(self, "month", QDate.currentDate().month())
            y = getattr(self, "year", QDate.currentDate().year())
            date_str = f"{y}-{m:02d}-{day:02d}"
            
            from ui.hr.dialogs import HeuresPresenceDialog
            dlg = HeuresPresenceDialog(eid, nom_prenom, date_str, self)
            if dlg.exec():
                # Refresh data to get the new times and apply colors
                self.load_data()
                self.tbl_presences.clearSelection()
