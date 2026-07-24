import os
import json
import logging
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QStackedWidget, QLabel, QFrame, QMessageBox
)
from PySide6.QtCore import Qt, QFile, QTextStream, QSize, QThread, Signal, QTimer
from database.base.stock_connector import sync_stock_data_logic

class StockSyncWorker(QThread):
    sync_finished = Signal(dict)

    def run(self):
        try:
            results = sync_stock_data_logic()
            self.sync_finished.emit(results)
        except Exception as e:
            logging.error(f"Background sync exception: {e}")
            self.sync_finished.emit({"success": False, "error": str(e)})
from PySide6.QtGui import QIcon, QPixmap, QPainter
from ui.dashboard.dashboard_view import DashboardView
from ui.hr.hr_view import HRView
from ui.caisse.caisse_view import CaisseView
from ui.caisse.tabs.cloture_tab import ClotureCaisseTab
from ui.fournisseurs.fournisseurs_view import FournisseursView
from ui.partenaires.partenaires_view import PartenairesView
from ui.banque.banque_view import BanqueView
from ui.settings.settings_view import SettingsView
from ui.donnees_base.donnees_base_view import DonneesBaseView

class MainWindow(QMainWindow):
    logout_requested = Signal()

    def __init__(self, current_user=None):
        super().__init__()
        self.current_user = current_user or {}
        # Ensure default permissions exist if somehow missing
        if 'permissions' not in self.current_user:
            self.current_user['permissions'] = {"sections": ["Dashboard"], "tabs": {}}
            
        self.setWindowTitle("FINANCELAM")
        self.resize(1150, 750)
        
        # Load stylesheet
        self.load_stylesheet()
        
        # Main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        self.setup_sidebar()
        self.setup_content_area()
        
        # Background Stock Sync setup
        self.sync_worker = None
        self.sync_timer = QTimer(self)
        self.sync_timer.timeout.connect(self.start_background_sync)
        self.sync_timer.start(300000) # Every 5 minutes
        
        # Trigger initial sync 2 seconds after startup
        QTimer.singleShot(2000, self.start_background_sync)
        
    def load_stylesheet(self):
        try:
            from PySide6.QtWidgets import QApplication
            dir_path = os.path.dirname(os.path.abspath(__file__))
            style_path = os.path.join(dir_path, "styles.qss")
            style_file = QFile(style_path)
            if style_file.open(QFile.ReadOnly | QFile.Text):
                stream = QTextStream(style_file)
                qss = stream.readAll()
                style_file.close()
                # Apply to the whole application so dialogs, menus and popups are also themed
                QApplication.instance().setStyleSheet(qss)
            else:
                print(f"Warning: Could not open stylesheet at {style_path}")
        except Exception as e:
            print(f"Error loading stylesheet: {e}")
            
    def setup_sidebar(self):
        # Sidebar widget as a QFrame to match stylesheet selector QFrame#sidebar_container
        self.sidebar_widget = QFrame()
        self.sidebar_widget.setObjectName("sidebar_container")
        self.sidebar_widget.setFixedWidth(240)
        
        self.sidebar_layout = QVBoxLayout(self.sidebar_widget)
        self.sidebar_layout.setContentsMargins(0, 25, 0, 20)
        self.sidebar_layout.setSpacing(5)
        
        # Header / Title widget + Toggle Button
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(15, 10, 15, 10)
        
        # Toggle button
        self.toggle_btn = QPushButton()
        self.toggle_btn.setFixedSize(30, 30)
        self.toggle_btn.setCursor(Qt.PointingHandCursor)
        self.toggle_btn.setStyleSheet("border: none; background: transparent; padding: 5px;")
        
        # Render hamburger icon
        from PySide6.QtSvg import QSvgRenderer
        from PySide6.QtCore import QByteArray
        def render_pixmap(path_data, color):
            svg = (
                f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
                f'<path fill="{color}" d="{path_data}"/>'
                f'</svg>'
            )
            renderer = QSvgRenderer(QByteArray(svg.encode()))
            px = QPixmap(18, 18)
            px.fill(Qt.transparent)
            p = QPainter(px)
            renderer.render(p)
            p.end()
            return px
            
        hamburger_path = "M3 18h18v-2H3v2zm0-5h18v-2H3v2zm0-7v2h18V6H3z"
        self.toggle_btn.setIcon(QIcon(render_pixmap(hamburger_path, "#607d8b")))
        self.toggle_btn.clicked.connect(self.toggle_sidebar)
        
        self.title_widget = QWidget()
        title_layout = QVBoxLayout(self.title_widget)
        title_layout.setContentsMargins(5, 0, 0, 0)
        title_layout.setSpacing(2)
        
        title = QLabel("FINANCELAM")
        title.setObjectName("sidebar_title")
        
        sub_title = QLabel("Comptabilité")
        sub_title.setObjectName("sidebar_sub")
        
        user_name = self.current_user.get('nom_complet', 'Utilisateur')
        user_lbl = QLabel(f"👤 {user_name}")
        user_lbl.setStyleSheet("color: #007572; font-weight: bold; font-size: 11px; margin-top: 5px;")
        
        title_layout.addWidget(title)
        title_layout.addWidget(sub_title)
        title_layout.addWidget(user_lbl)
        
        header_layout.addWidget(self.toggle_btn)
        header_layout.addWidget(self.title_widget)
        header_layout.addStretch()
        
        self.sidebar_layout.addWidget(header_widget)
        
        # Line separator
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background-color: #f1f5f9; margin: 0px 20px 15px 20px;")
        line.setFixedHeight(1)
        self.sidebar_layout.addWidget(line)
        
        # Navigation Buttons
        self.nav_buttons = {}
        
        sections = [
            ("Dashboard", "Tableau de Bord", "M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8V11h-8v10zm0-18v6h8V3h-8z"),
            ("HR", "Ressources Humaines", "M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"),
            ("Caisse", "Caisse et Coffre", "M21 18v1c0 1.1-.9 2-2 2H5c-1.11 0-2-.9-2-2V5c0-1.1.89-2 2-2h14c1.1 0 2 .9 2 2v1h-9c-1.11 0-2 .9-2 2v8c0 1.1.89 2 2 2h9zm-9-2h10V8H12v8zm4-2.5c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5z"),
            ("Cloture", "Clôture de Caisse", "M18 8h-1V6c0-2.76-2.24-5-5-5S7 3.24 7 6v2H6c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V10c0-1.1-.9-2-2-2zm-6 9c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2zm3.1-9H8.9V6c0-1.71 1.39-3.1 3.1-3.1 1.71 0 3.1 1.39 3.1 3.1v2z"),
            ("Fournisseurs", "état des\n  fournisseurs", "M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm-5 14H4v-4h11v4zm0-5H4V9h11v4zm5 5h-4V9h4v9z"),
            ("Partenaires", "Sous-Traitants\n  Conventions", "M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z"),
            ("Banque", "Etat compte Bancaire", "M12 2L2 7v13h20V7L12 2zm8 16H4V9h16v9zm-8-7.25c-1.24 0-2.25 1.01-2.25 2.25s1.01 2.25 2.25 2.25 2.25-1.01 2.25-2.25-1.01-2.25-2.25-2.25z"),
            ("DonneesBase", "Données de base", "M3 13h2v-2H3v2zm0 4h2v-2H3v2zm0-8h2V7H3v2zm4 4h14v-2H7v2zm0 4h14v-2H7v2zM7 7v2h14V7H7z"),
            ("Settings", "Paramètres", "M19.14 12.94c.04-.3.06-.61.06-.94 0-.32-.02-.64-.07-.94l2.03-1.58c.18-.14.23-.41.12-.61l-1.92-3.32c-.12-.22-.37-.29-.59-.22l-2.39.96c-.5-.38-1.03-.7-1.62-.94l-.36-2.54c-.04-.24-.24-.41-.48-.41h-3.84c-.24 0-.43.17-.47.41l-.36 2.54c-.59.24-1.13.57-1.62.94l-2.39-.96c-.22-.08-.47 0-.59.22L2.74 8.87c-.12.21-.08.47.12.61l2.03 1.58c-.05.3-.09.63-.09.94s.02.64.07.94l-2.03 1.58c-.18.14-.23.41-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.05.24.24.41.48.41h3.84c.24 0 .44-.17.47-.41l.36-2.54c.59-.24 1.13-.56 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32c.12-.22.07-.47-.12-.61l-2.01-1.58zM12 15.6c-1.98 0-3.6-1.62-3.6-3.6s1.62-3.6 3.6-3.6 3.6 1.62 3.6 3.6-1.62 3.6-3.6 3.6z")
        ]
        
        allowed_sections = self.current_user.get('permissions', {}).get('sections', [])
        
        first_allowed = None
        for key, text, path in sections:
            # Check permissions
            if key not in allowed_sections and "admin" not in self.current_user.get('username', '').lower():
                continue
                
            if first_allowed is None:
                first_allowed = key
                
            btn = QPushButton(f"  {text}")
            btn.setProperty("full_text", f"  {text}")
            btn.setCheckable(True)
            btn.setProperty("class", "nav_button")
            btn.setCursor(Qt.PointingHandCursor)
            
            # Professional dynamic icon with active/inactive states
            icon = QIcon()
            
            px_off = render_pixmap(path, "#607d8b")
            px_on = render_pixmap(path, "#007572")
            px_active = render_pixmap(path, "#ffffff")
            
            icon.addPixmap(px_off, QIcon.Normal, QIcon.Off)
            icon.addPixmap(px_active, QIcon.Normal, QIcon.On)
            icon.addPixmap(px_on, QIcon.Active, QIcon.Off)
            icon.addPixmap(px_active, QIcon.Active, QIcon.On)
            
            btn.setIcon(icon)
            btn.setIconSize(QSize(18, 18))
            
            btn.clicked.connect(lambda checked, k=key: self.switch_section(k))
            self.sidebar_layout.addWidget(btn)
            self.nav_buttons[key] = btn
            
        self.sidebar_layout.addStretch()
        
        # Logout button
        self.logout_btn = QPushButton("  Déconnexion")
        self.logout_btn.setProperty("full_text", "  Déconnexion")
        self.logout_btn.setProperty("class", "nav_button")
        self.logout_btn.setCursor(Qt.PointingHandCursor)
        self.logout_btn.setStyleSheet("color: #e74c3c;")
        
        logout_path = "M17 7l-1.41 1.41L18.17 11H8v2h10.17l-2.58 2.58L17 17l5-5zM4 5h8V3H4c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h8v-2H4V5z"
        icon_logout = QIcon()
        px_logout_off = render_pixmap(logout_path, "#e74c3c")
        px_logout_on = render_pixmap(logout_path, "#c0392b")
        icon_logout.addPixmap(px_logout_off, QIcon.Normal, QIcon.Off)
        icon_logout.addPixmap(px_logout_on, QIcon.Normal, QIcon.On)
        icon_logout.addPixmap(px_logout_on, QIcon.Active, QIcon.Off)
        
        self.logout_btn.setIcon(icon_logout)
        self.logout_btn.setIconSize(QSize(18, 18))
        self.logout_btn.clicked.connect(self.logout_requested.emit)
        self.sidebar_layout.addWidget(self.logout_btn)
        
        self.main_layout.addWidget(self.sidebar_widget)
        
        # Select first allowed section
        if first_allowed:
            self.nav_buttons[first_allowed].setChecked(True)
            # Switch will happen after stacked widget is ready in setup_content_area
            QTimer.singleShot(100, lambda: self.switch_section(first_allowed))
        
    def setup_content_area(self):
        self.stacked_widget = QStackedWidget()
        self.pages = {}
        
        # We add a loading page as index 0 or default
        self.loading_page = QWidget()
        loading_layout = QVBoxLayout(self.loading_page)
        lbl = QLabel("Chargement en cours...")
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setStyleSheet("font-size: 24px; font-weight: bold; color: #007572;")
        loading_layout.addWidget(lbl)
        self.stacked_widget.addWidget(self.loading_page)
        
        self.main_layout.addWidget(self.stacked_widget)
        
    def switch_section(self, key):
        # Update button check states immediately
        for k, btn in self.nav_buttons.items():
            if k != key:
                btn.setChecked(False)
            else:
                btn.setChecked(True)
                
        # Show loading indicator first
        self.stacked_widget.setCurrentWidget(self.loading_page)
        
        # Use singleShot to allow the GUI to draw the loading page BEFORE blocking
        QTimer.singleShot(50, lambda: self._do_switch_section(key))
        
    def _do_switch_section(self, key):
        if key not in self.pages:
            # Lazy load the page
            if key == "Dashboard":
                self.pages[key] = DashboardView()
            elif key == "HR":
                self.pages[key] = HRView()
            elif key == "Caisse":
                page = CaisseView()
                if hasattr(page, 'set_permissions'):
                    if "admin" not in self.current_user.get('username', '').lower():
                        tabs = self.current_user.get('permissions', {}).get('tabs', {}).get('Caisse')
                        if tabs is not None:
                            page.set_permissions(tabs)
                self.pages[key] = page
            elif key == "Cloture":
                self.pages[key] = ClotureCaisseTab()
            elif key == "Fournisseurs":
                self.pages[key] = FournisseursView()
            elif key == "Partenaires":
                self.pages[key] = PartenairesView()
            elif key == "Banque":
                self.pages[key] = BanqueView()
            elif key == "DonneesBase":
                self.pages[key] = DonneesBaseView()
            elif key == "Settings":
                self.pages[key] = SettingsView(self)
            else:
                self.pages[key] = QWidget()
                
            self.stacked_widget.addWidget(self.pages[key])
            
        self.stacked_widget.setCurrentWidget(self.pages[key])
        
        if key in ("Fournisseurs", "Partenaires"):
            self.start_background_sync()

    def toggle_sidebar(self):
        if self.sidebar_widget.width() == 240:
            self.sidebar_widget.setFixedWidth(65)
            self.title_widget.hide()
            for btn in self.nav_buttons.values():
                btn.setText("")
                btn.setToolTip(btn.property("full_text").strip())
                btn.setStyleSheet("padding: 12px 0px; text-align: center; margin: 3px 5px;")
            self.logout_btn.setText("")
            self.logout_btn.setToolTip(self.logout_btn.property("full_text").strip())
            self.logout_btn.setStyleSheet("padding: 12px 0px; text-align: center; margin: 3px 5px; color: #e74c3c;")
        else:
            self.sidebar_widget.setFixedWidth(240)
            self.title_widget.show()
            for btn in self.nav_buttons.values():
                btn.setText(btn.property("full_text"))
                btn.setToolTip("")
                btn.setStyleSheet("")
            self.logout_btn.setText(self.logout_btn.property("full_text"))
            self.logout_btn.setToolTip("")
            self.logout_btn.setStyleSheet("color: #e74c3c;")

    def start_background_sync(self):
        if self.sync_worker and self.sync_worker.isRunning():
            return
        self.sync_worker = StockSyncWorker(self)
        self.sync_worker.sync_finished.connect(self.on_sync_finished)
        self.sync_worker.start()

    def on_sync_finished(self, results):
        if results.get("success"):
            logging.info("Background stock sync succeeded!")
            sup_new = results["suppliers"]["imported"]
            part_new = results["partners"]["imported"]
            rec_new = results["receptions"]["imported"]
            if sup_new > 0 or part_new > 0 or rec_new > 0:
                self.refresh_active_view()
        else:
            logging.warning(f"Background stock sync failed or skipped: {results.get('error')}")

    def refresh_active_view(self):
        active_widget = self.stacked_widget.currentWidget()
        if hasattr(active_widget, "on_filter_changed"):
            active_widget.on_filter_changed()
        elif hasattr(active_widget, "load_data"):
            try:
                active_widget.load_data()
            except Exception:
                pass

    def closeEvent(self, event):
        reply = QMessageBox.question(
            self, 
            "Confirmation de sortie",  
            "Voulez-vous vraiment quitter l'application ?",  
            QMessageBox.Yes | QMessageBox.No,  
            QMessageBox.No  
        )
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()
