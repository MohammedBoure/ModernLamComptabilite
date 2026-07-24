from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QFrame, QMessageBox, QGraphicsDropShadowEffect, QCheckBox
)
from PySide6.QtCore import Qt, Signal, QSettings
from PySide6.QtGui import QIcon, QFont, QPixmap, QColor
from database.auth_manager import AuthManager
import os

class LoginView(QWidget):
    # Signal emitted when login is successful, passing the user object
    login_successful = Signal(dict)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("ModernLam - Connexion")
        self.resize(1150, 750)
        
        # Main layout
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Setup UI
        self.setup_ui()
        
    def setup_ui(self):
        # Left side - Background / Logo
        left_frame = QFrame()
        left_frame.setStyleSheet("background-color: #007572;")
        left_layout = QVBoxLayout(left_frame)
        left_layout.setAlignment(Qt.AlignCenter)
        
        logo_label = QLabel()
        # Try to load the logo
        dir_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        logo_path = os.path.join(dir_path, "logo.png")
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path).scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(pixmap)
        else:
            logo_label.setText("ModernLam")
            logo_label.setStyleSheet("color: white; font-size: 36px; font-weight: bold;")
        
        subtitle = QLabel("FINANCELAM")
        # تم تكبير الخط إلى 26px، وجعله عريضاً (bold)، وتحديد نوع الخط ونظام الألوان
        subtitle.setStyleSheet("""
            color: #e0f2f1; 
            font-size: 26px; 
            font-weight: bold; 
            font-family: 'Segoe UI', Arial, sans-serif;
            margin-top: 25px;
            margin-bottom: 10px;
        """)
        
        left_layout.addWidget(logo_label, alignment=Qt.AlignCenter)
        left_layout.addWidget(subtitle, alignment=Qt.AlignCenter)
        
        # Right side - Login Form
        right_frame = QFrame()
        right_frame.setStyleSheet("background-color: #f4f7fa;")
        right_layout = QVBoxLayout(right_frame)
        right_layout.setAlignment(Qt.AlignCenter)
        
        # Form Container
        form_container = QFrame()
        form_container.setObjectName("login_container")
        form_container.setFixedWidth(400)
        form_container.setStyleSheet("""
            QFrame#login_container {
                background-color: white;
                border-radius: 10px;
            }
        """)
        
        # Drop shadow for form
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 5)
        form_container.setGraphicsEffect(shadow)
        
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(40, 50, 40, 50)
        form_layout.setSpacing(20)
        
        # Title
        title_lbl = QLabel("Bienvenue")
        title_lbl.setStyleSheet("font-size: 28px; font-weight: bold; color: #2c3e50;")
        title_lbl.setAlignment(Qt.AlignCenter)
        
        sub_title_lbl = QLabel("Connectez-vous à votre compte")
        sub_title_lbl.setStyleSheet("font-size: 14px; color: #7f8c8d; margin-bottom: 20px;")
        sub_title_lbl.setAlignment(Qt.AlignCenter)
        
        # Username
        user_lbl = QLabel("Nom d'utilisateur")
        user_lbl.setStyleSheet("font-size: 14px; font-weight: bold; color: #34495e;")
        
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Entrez votre nom d'utilisateur")
        self.user_input.setMinimumHeight(45)
        self.user_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                background-color: #fcfcfc;
            }
            QLineEdit:focus {
                border: 2px solid #007572;
                background-color: #ffffff;
            }
        """)
        
        # Password
        pass_lbl = QLabel("Mot de passe")
        pass_lbl.setStyleSheet("font-size: 14px; font-weight: bold; color: #34495e;")
        
        self.pass_input = QLineEdit()
        self.pass_input.setEchoMode(QLineEdit.Password)
        self.pass_input.setPlaceholderText("Entrez votre mot de passe")
        self.pass_input.setMinimumHeight(45)
        self.pass_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                background-color: #fcfcfc;
            }
            QLineEdit:focus {
                border: 2px solid #007572;
                background-color: #ffffff;
            }
        """)
        self.pass_input.returnPressed.connect(self.attempt_login)
        
        # Error Label
        self.error_lbl = QLabel("")
        self.error_lbl.setStyleSheet("color: #e74c3c; font-size: 13px; font-weight: bold;")
        self.error_lbl.setAlignment(Qt.AlignCenter)
        self.error_lbl.hide()
        
        # Remember Me Checkbox
        self.remember_cb = QCheckBox("Se souvenir de moi")
        self.remember_cb.setStyleSheet("color: #34495e; font-size: 13px;")
        
        # Login Button
        self.login_btn = QPushButton("Se Connecter")
        self.login_btn.setMinimumHeight(50)
        self.login_btn.setCursor(Qt.PointingHandCursor)
        self.login_btn.setStyleSheet("""
            QPushButton {
                background-color: #007572;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 16px;
                font-weight: bold;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #009688;
            }
            QPushButton:pressed {
                background-color: #004d40;
            }
        """)
        self.login_btn.clicked.connect(self.attempt_login)
        
        # Assemble Form
        form_layout.addWidget(title_lbl)
        form_layout.addWidget(sub_title_lbl)
        form_layout.addWidget(user_lbl)
        form_layout.addWidget(self.user_input)
        form_layout.addWidget(pass_lbl)
        form_layout.addWidget(self.pass_input)
        form_layout.addWidget(self.remember_cb)
        form_layout.addWidget(self.error_lbl)
        form_layout.addWidget(self.login_btn)
        
        right_layout.addWidget(form_container)
        
        # Add to main layout
        self.main_layout.addWidget(left_frame, 1) # 1 part
        self.main_layout.addWidget(right_frame, 1) # 1 part
        
    def attempt_login(self):
        self.error_lbl.hide()
        username = self.user_input.text().strip()
        password = self.pass_input.text()
        
        if not username or not password:
            self.show_error("Veuillez remplir tous les champs.")
            return
            
        self.login_btn.setEnabled(False)
        self.login_btn.setText("Connexion en cours...")
        
        # Check authentication
        user = AuthManager.authenticate(username, password)
        
        if user:
            settings = QSettings("ModernLam", "Comptabilite")
            if self.remember_cb.isChecked():
                settings.setValue("saved_username", username)
            else:
                settings.remove("saved_username")
            
            self.login_successful.emit(user)
        else:
            self.show_error("Nom d'utilisateur ou mot de passe incorrect.")
            self.login_btn.setEnabled(True)
            self.login_btn.setText("Se Connecter")
            self.pass_input.clear()
            self.pass_input.setFocus()
            
    def show_error(self, message):
        self.error_lbl.setText(message)
        self.error_lbl.show()

    def set_loading_state(self, is_loading):
        self.user_input.setDisabled(is_loading)
        self.pass_input.setDisabled(is_loading)
        self.login_btn.setDisabled(is_loading)
        if is_loading:
            self.login_btn.setText("Chargement en cours...")
        else:
            self.login_btn.setText("Se Connecter")
