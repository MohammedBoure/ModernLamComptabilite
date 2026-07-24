"""
table_helper.py
───────────────
Professional toolbar builder + table edit/delete helper.

Usage:
    toolbar = make_table_editable(
        table_widget, "TableName", "pk_col",
        lambda r: ...,          # get PK from row
        SomeDialog,
        self.load_data,
        self,
        add_callback=self.add_item,
        add_label="Ajouter …"
    )
    layout.addWidget(toolbar)
    layout.addWidget(self.table_widget)
"""

from PySide6.QtWidgets import (
    QMenu, QMessageBox, QPushButton, QWidget, QHBoxLayout, QFrame
)
from PySide6.QtCore import Qt, QByteArray
from PySide6.QtGui import QAction, QFont, QIcon, QPixmap, QPainter
from database import data_manager

# ── Material Design SVG path data ─────────────────────────────────────────────
_PATH_ADD = (
    "M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"
)
_PATH_EDIT = (
    "M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25z"
    "M20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34"
    "c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"
)
_PATH_DELETE = (
    "M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12z"
    "M19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"
)
_PATH_REFRESH = (
    "M17.65 6.35C16.2 4.9 14.21 4 12 4c-4.42 0-7.99 3.58-7.99 8"
    "s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08"
    "c-.82 2.33-3.04 4-5.65 4-3.31 0-6-2.69-6-6s2.69-6 6-6"
    "c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z"
)


# Public SVG icon paths
PATH_ADD = _PATH_ADD
PATH_EDIT = _PATH_EDIT
PATH_DELETE = _PATH_DELETE
PATH_REFRESH = _PATH_REFRESH
PATH_SEARCH = "M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"
PATH_SETTINGS = "M19.14 12.94c.04-.3.06-.61.06-.94 0-.32-.02-.64-.07-.94l2.03-1.58c.18-.14.23-.41.12-.61l-1.92-3.32c-.12-.22-.37-.29-.59-.22l-2.39.96c-.5-.38-1.03-.7-1.62-.94l-.36-2.54c-.04-.24-.24-.41-.48-.41h-3.84c-.24 0-.43.17-.47.41l-.36 2.54c-.59.24-1.13.57-1.62.94l-2.39-.96c-.22-.08-.47 0-.59.22L2.74 8.87c-.12.21-.08.47.12.61l2.03 1.58c-.05.3-.09.63-.09.94s.02.64.07.94l-2.03 1.58c-.18.14-.23.41-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.05.24.24.41.48.41h3.84c.24 0 .44-.17.47-.41l.36-2.54c.59-.24 1.13-.56 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32c.12-.22.07-.47-.12-.61l-2.01-1.58zM12 15.6c-1.98 0-3.6-1.62-3.6-3.6s1.62-3.6 3.6-3.6 3.6 1.62 3.6 3.6-1.62 3.6-3.6 3.6z"
PATH_PARTNER = "M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z"
PATH_SUPPLIER = "M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"
PATH_WRENCH = "M22.7 19l-9.1-9.1c.9-2.3.4-5-1.5-6.9-2-2-5-2.4-7.4-1.3L9 6 6 9 1.6 4.3C.5 6.7.9 9.8 2.9 11.8c1.9 1.9 4.6 2.4 6.9 1.5l9.1 9.1c.4.4 1 .4 1.4 0l2.3-2.3c.5-.4.5-1.1.1-1.5z"
PATH_BOX = "M20 6h-4V4c0-1.11-.89-2-2-2h-4c-1.11 0-2 .89-2 2v2H4c-1.11 0-1.99.89-1.99 2L2 19c0 1.11.89 2 2 2h16c1.11 0 2-.89 2-2V8c0-1.11-.89-2-2-2zm-8-2h4v2h-4V4zm8 15H4V8h16v11z"
PATH_LIST = "M4 6h16v2H4zm0 5h16v2H4zm0 5h16v2H4z"
PATH_DOCUMENT = "M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z"

def _svg_icon(path_data: str, color: str = "#ffffff", size: int = 16) -> QIcon:
    """Render an inline Material SVG path to a QIcon."""
    try:
        from PySide6.QtSvg import QSvgRenderer
        svg = (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
            f'<path fill="{color}" d="{path_data}"/>'
            f'</svg>'
        )
        renderer = QSvgRenderer(QByteArray(svg.encode()))
        px = QPixmap(size, size)
        px.fill(Qt.transparent)
        p = QPainter(px)
        renderer.render(p)
        p.end()
        return QIcon(px)
    except Exception:
        return QIcon()

def get_svg_icon(path_data: str, color: str = "#ffffff", size: int = 16) -> QIcon:
    """Public helper to get an SVG icon."""
    return _svg_icon(path_data, color, size)


def _btn(label: str, path: str, bg: str, hover: str, enabled: bool = True) -> QPushButton:
    """Create a styled icon+text button."""
    b = QPushButton(f" {label}")
    b.setIcon(_svg_icon(path, "#ffffff", 15))
    b.setEnabled(enabled)
    b.setMinimumHeight(30)
    b.setCursor(Qt.PointingHandCursor)
    b.setStyleSheet(
        f"QPushButton {{"
        f"  background-color: {bg}; color: #ffffff;"
        f"  font-weight: 600; font-size: 12px;"
        f"  border: none; border-radius: 5px;"
        f"  padding: 0 13px;"
        f"}}"
        f"QPushButton:hover {{ background-color: {hover}; }}"
        f"QPushButton:pressed {{ background-color: {hover}; padding-top: 1px; }}"
        f"QPushButton:disabled {{"
        f"  background-color: #cfd8dc; color: #90a4ae;"
        f"}}"
    )
    return b


def _vsep() -> QFrame:
    """Thin vertical separator."""
    s = QFrame()
    s.setFrameShape(QFrame.VLine)
    s.setFixedWidth(1)
    s.setFixedHeight(22)
    s.setStyleSheet("background-color: #cfd8dc;")
    return s


# ─────────────────────────────────────────────────────────────────────────────
def make_table_editable(
    table_widget,
    table_name: str,
    pk_col: str,
    get_pk_fn,
    edit_dialog_class,
    load_data_callback,
    parent_widget,
    add_callback=None,
    add_label: str = "Ajouter",
    refresh_callback=None,
    delete_callback=None,
):
    """
    Build a professional toolbar and wire up edit/delete on *table_widget*.

    Parameters
    ----------
    add_callback : callable | None
        If given, an "Ajouter" button is included in the toolbar.
    add_label : str
        Label for the add button.
    refresh_callback : callable | None
        Defaults to *load_data_callback* when not provided.

    Returns
    -------
    QWidget
        The toolbar widget — place it in the layout BEFORE the table.
    """
    if refresh_callback is None:
        refresh_callback = load_data_callback

    # ── CRUD helpers ──────────────────────────────────────────────────────────
    def _edit(row):
        pk = get_pk_fn(row)
        if pk is None:
            return
        record = data_manager.db.fetch_one(
            f"SELECT * FROM {table_name} WHERE {pk_col} = %s", (pk,)
        )
        if not record:
            QMessageBox.critical(parent_widget, "Erreur", "Enregistrement introuvable.")
            return
        dlg = edit_dialog_class(parent_widget, record=record)
        if dlg.exec():
            load_data_callback()

    def _delete(row):
        pk = get_pk_fn(row)
        if pk is None:
            return
        reply = QMessageBox.question(
            parent_widget,
            "Confirmation",
            "Supprimer cet enregistrement ?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            if delete_callback:
                ok = delete_callback(pk)
            else:
                ok, _ = data_manager.db.delete_record(table_name, pk_col, pk)
            if ok:
                load_data_callback()
            else:
                QMessageBox.critical(
                    parent_widget, "Erreur",
                    "Suppression impossible — cet enregistrement est lié à d'autres données."
                )

    # ── Right-click context menu ───────────────────────────────────────────────
    def _ctx_menu(pos):
        item = table_widget.itemAt(pos)
        if not item:
            return
        row = item.row()
        if get_pk_fn(row) is None:
            return
        menu = QMenu(table_widget)
        a_edit = QAction("Modifier", table_widget)
        a_edit.setFont(QFont("Segoe UI", 10, QFont.Bold))
        a_del = QAction("Supprimer", table_widget)
        menu.addAction(a_edit)
        menu.addSeparator()
        menu.addAction(a_del)
        chosen = menu.exec(table_widget.mapToGlobal(pos))
        if chosen == a_edit:
            _edit(row)
        elif chosen == a_del:
            _delete(row)

    table_widget.setContextMenuPolicy(Qt.CustomContextMenu)
    table_widget.customContextMenuRequested.connect(_ctx_menu)
    table_widget.cellDoubleClicked.connect(lambda r, c: _edit(r))

    # ── Build toolbar ─────────────────────────────────────────────────────────
    bar = QWidget()
    bar.setObjectName("tbl_toolbar")
    hl = QHBoxLayout(bar)
    hl.setContentsMargins(0, 2, 0, 4)
    hl.setSpacing(5)

    # Add
    if add_callback:
        btn_add = _btn(add_label, _PATH_ADD, "#2e7d32", "#1b5e20")
        btn_add.clicked.connect(add_callback)
        hl.addWidget(btn_add)
        hl.addWidget(_vsep())

    # Edit  (disabled until row selected)
    btn_edit = _btn("Modifier",   _PATH_EDIT,   "#1565c0", "#0d47a1", enabled=False)
    btn_del  = _btn("Supprimer",  _PATH_DELETE, "#c62828", "#b71c1c", enabled=False)
    hl.addWidget(btn_edit)
    hl.addWidget(btn_del)

    hl.addWidget(_vsep())

    # Refresh
    btn_ref = _btn("Actualiser", _PATH_REFRESH, "#546e7a", "#37474f")
    btn_ref.clicked.connect(refresh_callback)
    hl.addWidget(btn_ref)

    hl.addStretch()

    # Enable/disable on selection change
    def _sel():
        rows = list(set(idx.row() for idx in table_widget.selectedIndexes()))
        has = len(rows) > 0 and get_pk_fn(rows[0]) is not None
        btn_edit.setEnabled(has)
        btn_del.setEnabled(has)

    table_widget.itemSelectionChanged.connect(_sel)
    btn_edit.clicked.connect(lambda: _edit(table_widget.selectedIndexes()[0].row()
                                           if table_widget.selectedIndexes() else None))
    btn_del.clicked.connect(lambda: _delete(table_widget.selectedIndexes()[0].row()
                                            if table_widget.selectedIndexes() else None))

    return bar
