from PySide6.QtWidgets import (
    QWidget, QVBoxLayout,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont
from database import data_manager

_sentinel = object()


class ProfitabiliteTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.month = None
        self.year = None
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(4)

        self.tbl_profitabilite = QTableWidget()
        self.tbl_profitabilite.setColumnCount(2)
        self.tbl_profitabilite.setHorizontalHeaderLabels(
            ["INDICATEUR", "VALEUR"]
        )
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
            from PySide6.QtCore import QDate
            m = QDate.currentDate().month() if not m else m
            y = QDate.currentDate().year() if not y else y
            
        summary = data_manager.fournisseurs.get_profitability_summary(m, y)
        
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

        set_metric_row(0, "PAIE ESTIMATION", summary['total_paie'])
        set_metric_row(1, "DEPENSES INTERNE", summary['total_dep_int'])
        
        for col in range(2):
            self.tbl_profitabilite.setItem(2, col, QTableWidgetItem(""))
            
        set_metric_row(3, "FOURNISSEURS + DEPENCES + PAIE", summary['total_costs'], is_bold=True, color_hex="#c62828")
        
        for col in range(2):
            self.tbl_profitabilite.setItem(4, col, QTableWidgetItem(""))
            self.tbl_profitabilite.setItem(5, col, QTableWidgetItem(""))
            
        set_metric_row(6, "CA LAM", summary['ca_lam'])
        set_metric_row(7, "CA C", summary['ca_c'])
        set_metric_row(8, "CA ST", summary['ca_st'])
        set_metric_row(9, "ENTREES SUPP", summary['entrees_supp'])
        set_metric_row(10, "Chiffre d'Affaire", summary['chiffre_affaire'], is_bold=True, color_hex="#1565c0")
        
        for col in range(2):
            self.tbl_profitabilite.setItem(11, col, QTableWidgetItem(""))
            
        prof_color = "#2e7d32" if summary['profitability'] >= 0 else "#c62828"
        set_metric_row(12, "Profitabilité (CA+ST)-(FR+DEP+ PAIE)", summary['profitability'], is_bold=True, color_hex=prof_color)
        set_metric_row(13, "% Profitabilité / Chiffre d'Affaire", f"{summary['profitability_pct']:.2f} %", is_bold=True, color_hex=prof_color)
