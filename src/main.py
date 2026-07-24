import sys
import os

# Add the src directory to sys.path so we can import modules properly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication, QLineEdit, QAbstractSpinBox
from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt, QObject, QEvent, QTimer, QSettings, QThread, Signal
from ui.main_window import MainWindow

class InitWorker(QThread):
    finished_init = Signal(object)

    def __init__(self, saved_user):
        super().__init__()
        self.saved_user = saved_user

    def run(self):
        try:
            from database.init_db import init_database
            from database.auth_manager import AuthManager
            init_database()
            AuthManager.initialize_default_admin()
            
            user = None
            if self.saved_user:
                user = AuthManager.get_user_by_username(self.saved_user)
            self.finished_init.emit(user)
        except Exception as e:
            print(f"Init error: {e}")
            self.finished_init.emit(None)


class InputSelectAllFilter(QObject):
    """Global event filter to select all text when an input field gains focus."""
    def eventFilter(self, watched, event):
        if event.type() == QEvent.FocusIn:
            if isinstance(watched, QLineEdit):
                # Use QTimer.singleShot to ensure selection occurs after mouse press completes
                QTimer.singleShot(0, watched.selectAll)
            elif isinstance(watched, QAbstractSpinBox):
                line_edit = watched.findChild(QLineEdit)
                if line_edit:
                    QTimer.singleShot(0, line_edit.selectAll)
        return super().eventFilter(watched, event)



def build_light_palette():
    """Force a complete light palette so the app never inherits a dark system theme."""
    palette = QPalette()

    # ── Window / background ──────────────────────────────────────────────────
    palette.setColor(QPalette.Window,          QColor("#f4f7fa"))
    palette.setColor(QPalette.WindowText,      QColor("#2c3e50"))

    # ── Widgets ──────────────────────────────────────────────────────────────
    palette.setColor(QPalette.Base,            QColor("#ffffff"))
    palette.setColor(QPalette.AlternateBase,   QColor("#fafbfc"))
    palette.setColor(QPalette.Text,            QColor("#2c3e50"))
    palette.setColor(QPalette.PlaceholderText, QColor("#90a4ae"))

    # ── Buttons ──────────────────────────────────────────────────────────────
    palette.setColor(QPalette.Button,          QColor("#ffffff"))
    palette.setColor(QPalette.ButtonText,      QColor("#007572"))

    # ── Highlighted / selected items ─────────────────────────────────────────
    palette.setColor(QPalette.Highlight,       QColor("#007572"))
    palette.setColor(QPalette.HighlightedText, QColor("#ffffff"))

    # ── Tooltip ──────────────────────────────────────────────────────────────
    palette.setColor(QPalette.ToolTipBase,     QColor("#ffffff"))
    palette.setColor(QPalette.ToolTipText,     QColor("#2c3e50"))

    # ── Borders / lines (Light) ───────────────────────────────────────────────
    palette.setColor(QPalette.Mid,             QColor("#cfd8dc"))
    palette.setColor(QPalette.Midlight,        QColor("#eceff1"))
    palette.setColor(QPalette.Dark,            QColor("#b0bec5"))
    palette.setColor(QPalette.Shadow,          QColor("#90a4ae"))
    palette.setColor(QPalette.Light,           QColor("#ffffff"))

    # ── Disabled state ───────────────────────────────────────────────────────
    palette.setColor(QPalette.Disabled, QPalette.Text,       QColor("#90a4ae"))
    palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor("#90a4ae"))
    palette.setColor(QPalette.Disabled, QPalette.Window,     QColor("#eceff1"))
    palette.setColor(QPalette.Disabled, QPalette.Base,       QColor("#f1f3f5"))

    return palette


def main():
    # Prevent Qt from auto-detecting and applying the OS dark/light theme
    os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = ""          # no native platform theming
    os.environ.pop("QT_STYLE_OVERRIDE", None)               # clear any override

    app = QApplication(sys.argv)

    # Global filter to select all text when simple input fields get focus
    select_all_filter = InputSelectAllFilter(app)
    app.installEventFilter(select_all_filter)

    # Fusion gives us full stylesheet control across all platforms
    app.setStyle("Fusion")

    # Apply our custom light palette — this overrides the system palette completely
    app.setPalette(build_light_palette())

    # Extra: ensure QMenu and QToolTip also stay light
    app.setStyleSheet(
        "QMenu { background-color: #ffffff; color: #2c3e50; border: 1px solid #cfd8dc; }"
        "QMenu::item:selected { background-color: #007572; color: #ffffff; }"
        "QToolTip { background-color: #ffffff; color: #2c3e50; border: 1px solid #007572; }"
        "QMessageBox { background-color: #f4f7fa; }"
        "QDialog { background-color: #f4f7fa; }"
    )

    # Check for saved session before heavy DB imports
    settings = QSettings("ModernLam", "Comptabilite")
    saved_user = settings.value("saved_username")

    from ui.login.login_view import LoginView
    login_window = LoginView()
    
    # We need to hold a reference to main_window so it isn't garbage collected
    main_window_ref = []

    def show_login():
        login_window.user_input.clear()
        login_window.pass_input.clear()
        login_window.showMaximized()

    def on_logout():
        settings = QSettings("ModernLam", "Comptabilite")
        settings.remove("saved_username")
        for w in main_window_ref:
            w.close()
        main_window_ref.clear()
        show_login()

    def on_login_success(user):
        window = MainWindow(current_user=user)
        window.logout_requested.connect(on_logout)
        main_window_ref.append(window)
        window.showMaximized()
        login_window.close()

    login_window.login_successful.connect(on_login_success)

    # Put login window in loading state immediately
    if hasattr(login_window, 'set_loading_state'):
        login_window.set_loading_state(True)
    login_window.showMaximized()

    def on_init_done(user):
        if hasattr(login_window, 'set_loading_state'):
            login_window.set_loading_state(False)
        if user:
            on_login_success(user)

    worker = InitWorker(saved_user)
    worker.finished_init.connect(on_init_done)
    login_window._worker = worker
    worker.start()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
