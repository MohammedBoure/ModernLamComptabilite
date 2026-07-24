import os
import logging
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QGroupBox, QFormLayout, QSpinBox, QMessageBox
)
from PySide6.QtCore import Qt
from database.base.config import get_external_path

def load_app_env_settings():
    env_path = get_external_path(".env")
    defaults = {
        "DB_HOST": "localhost",
        "DB_PORT": 3306,
        "DB_USER": "root",
        "DB_PASSWORD": "root",
        "DB_NAME": "modernlam"
    }
    if os.path.exists(env_path):
        try:
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        k, v = line.split('=', 1)
                        k = k.strip()
                        v = v.strip()
                        if k in defaults:
                            if k == 'DB_PORT':
                                try:
                                    defaults[k] = int(v)
                                except ValueError:
                                    pass
                            else:
                                defaults[k] = v
        except Exception as e:
            logging.error(f"Error reading local .env: {e}")
    return defaults

def save_app_env_settings(host, port, user, password, db_name):
    env_path = get_external_path(".env")
    keys_updated = {
        "DB_HOST": host,
        "DB_PORT": str(port),
        "DB_USER": user,
        "DB_PASSWORD": password,
        "DB_NAME": db_name
    }
    lines = []
    
    if os.path.exists(env_path):
        try:
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    stripped = line.strip()
                    if stripped and not stripped.startswith('#') and '=' in stripped:
                        k, v = stripped.split('=', 1)
                        k = k.strip()
                        if k in keys_updated:
                            lines.append(f"{k}={keys_updated.pop(k)}\n")
                            continue
                    lines.append(line)
        except Exception as e:
            logging.error(f"Error reading .env: {e}")
            
    # Append any remaining keys that weren't in the file
    for k, v in keys_updated.items():
        lines.append(f"{k}={v}\n")
        
    try:
        with open(env_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        return True
    except Exception as e:
        logging.error(f"Error writing .env: {e}")
        return False

def test_app_db_connection(config):
    import mysql.connector
    try:
        conn = mysql.connector.connect(
            host=config['host'],
            port=config['port'],
            user=config['user'],
            password=config['password'],
            connect_timeout=3,
            use_pure=True,
            auth_plugin='mysql_native_password'
        )
        cursor = conn.cursor()
        cursor.execute(f"SHOW DATABASES LIKE '{config['database']}'")
        exists = cursor.fetchone()
        cursor.close()
        conn.close()
        if exists:
            return True, "Connexion réussie !"
        else:
            return True, "Connexion réussie ! (Remarque : La base de données n'existe pas encore, elle sera créée automatiquement au démarrage du programme)"
    except Exception as e:
        return False, str(e)


class AppDbConfigWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = load_app_env_settings()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        title_label = QLabel("Connexion à la Base de Données de l'Application")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #007572;")
        layout.addWidget(title_label)

        # 1. Connection Group
        group_conn = QGroupBox("Paramètres de la Base de Données Locale")
        form_layout = QFormLayout(group_conn)
        form_layout.setSpacing(10)

        self.edit_host = QLineEdit(self.settings.get('DB_HOST', 'localhost'))
        self.sp_port = QSpinBox()
        self.sp_port.setRange(1, 65535)
        self.sp_port.setValue(int(self.settings.get('DB_PORT', 3306)))
        
        self.edit_user = QLineEdit(self.settings.get('DB_USER', 'root'))
        self.edit_pass = QLineEdit(self.settings.get('DB_PASSWORD', 'root'))
        self.edit_pass.setEchoMode(QLineEdit.Password)
        self.edit_name = QLineEdit(self.settings.get('DB_NAME', 'modernlam'))

        form_layout.addRow("Adresse IP / Hôte:", self.edit_host)
        form_layout.addRow("Port:", self.sp_port)
        form_layout.addRow("Nom d'utilisateur:", self.edit_user)
        form_layout.addRow("Mot de passe:", self.edit_pass)
        form_layout.addRow("Nom de la Base de données:", self.edit_name)

        buttons_layout = QHBoxLayout()
        self.btn_test = QPushButton("⚡ Tester la Connexion")
        self.btn_test.setStyleSheet("background-color: #37474f; color: white; padding: 8px; font-weight: bold; border-radius: 4px;")
        self.btn_test.clicked.connect(self.test_connection)

        self.btn_save = QPushButton("💾 Enregistrer la configuration")
        self.btn_save.setStyleSheet("background-color: #2e7d32; color: white; padding: 8px; font-weight: bold; border-radius: 4px;")
        self.btn_save.clicked.connect(self.save_settings)

        buttons_layout.addWidget(self.btn_test)
        buttons_layout.addWidget(self.btn_save)
        
        layout.addWidget(group_conn)
        layout.addLayout(buttons_layout)
        
        # Guide label
        lbl_info = QLabel(
            "Note: Les modifications de connexion à la base de données de l'application nécessitent un redémarrage "
            "complet du programme pour s'appliquer."
        )
        lbl_info.setWordWrap(True)
        lbl_info.setStyleSheet("color: #d32f2f; font-weight: bold; font-size: 11px;")
        layout.addWidget(lbl_info)
        
        layout.addStretch()

    def test_connection(self):
        config = {
            "host": self.edit_host.text().strip(),
            "port": self.sp_port.value(),
            "user": self.edit_user.text().strip(),
            "password": self.edit_pass.text(),
            "database": self.edit_name.text().strip()
        }
        success, msg = test_app_db_connection(config)
        if success:
            QMessageBox.information(self, "Succès", f"Connexion à la base de données réussie :\n{msg}")
        else:
            QMessageBox.critical(self, "Échec", f"Impossible de se connecter à la base de données locale :\n{msg}")

    def save_settings(self):
        host = self.edit_host.text().strip()
        port = self.sp_port.value()
        user = self.edit_user.text().strip()
        password = self.edit_pass.text()
        db_name = self.edit_name.text().strip()
        
        success = save_app_env_settings(host, port, user, password, db_name)
        if success:
            QMessageBox.information(
                self, 
                "Succès", 
                "Configuration de la base de données enregistrée avec succès !\n\n"
                "Veuillez redémarrer le programme pour appliquer les nouveaux paramètres."
            )
        else:
            QMessageBox.critical(self, "Erreur", "Une erreur est survenue lors de la sauvegarde dans le fichier .env.")
