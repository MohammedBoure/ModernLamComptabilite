"""User-management screen for creating and maintaining application accounts."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox, QDialog, QDialogButtonBox, QFormLayout, QHBoxLayout, QLabel,
    QLineEdit, QMessageBox, QPushButton, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QWidget,
)

from database import data_manager


ROLE_LABELS = {
    "ADMIN": "Administrateur",
    "DIRECTION": "Direction",
    "ACCOUNTANT": "Comptable",
    "CASHIER": "Caissier",
    "HR": "Ressources humaines",
    "VIEWER": "Lecture seule",
}


class UserDialog(QDialog):
    def __init__(self, user=None, parent=None):
        super().__init__(parent)
        self.user = user or {}
        self.setWindowTitle("Nouveau utilisateur" if not user else "Modifier utilisateur")
        self.setMinimumWidth(420)

        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.full_name = QLineEdit(self.user.get("nom_complet", ""))
        self.username = QLineEdit(self.user.get("username", ""))
        self.role = QComboBox()
        for code, label in ROLE_LABELS.items():
            self.role.addItem(label, code)
        current_role = self.user.get("role_code", "VIEWER")
        self.role.setCurrentIndex(max(0, self.role.findData(current_role)))
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        self.password_confirm = QLineEdit()
        self.password_confirm.setEchoMode(QLineEdit.Password)
        self.password.setPlaceholderText("Au moins 8 caracteres")
        self.password_confirm.setPlaceholderText("Confirmer le mot de passe")
        form.addRow("Nom complet *", self.full_name)
        form.addRow("Identifiant *", self.username)
        form.addRow("Role *", self.role)
        form.addRow("Mot de passe" + (" *" if not user else " (laisser vide pour conserver)"), self.password)
        form.addRow("Confirmation", self.password_confirm)
        layout.addLayout(form)
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def values(self):
        password = self.password.text()
        if password != self.password_confirm.text():
            raise ValueError("Les deux mots de passe ne correspondent pas.")
        return {
            "nom_complet": self.full_name.text().strip(),
            "username": self.username.text().strip(),
            "role_code": self.role.currentData(),
            "password": password,
        }


class UsersView(QWidget):
    """Account administration. Service authorization remains mandatory."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_users = []
        self.setup_ui()
        self.load_users()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)
        layout.addWidget(QLabel("<h2>Utilisateurs de l'application</h2>"))
        layout.addWidget(QLabel("Creation, roles et activation des comptes. Les mots de passe ne sont jamais affiches."))

        toolbar = QHBoxLayout()
        self.add_button = QPushButton("+ Nouvel utilisateur")
        self.edit_button = QPushButton("Modifier")
        self.status_button = QPushButton("Activer / Desactiver")
        self.refresh_button = QPushButton("Actualiser")
        self.add_button.clicked.connect(self.create_user)
        self.edit_button.clicked.connect(self.edit_user)
        self.status_button.clicked.connect(self.toggle_active)
        self.refresh_button.clicked.connect(self.load_users)
        for button in (self.add_button, self.edit_button, self.status_button, self.refresh_button):
            toolbar.addWidget(button)
        toolbar.addStretch()
        layout.addLayout(toolbar)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["Identifiant", "Nom complet", "Role", "Statut", "Cree le", "Modifie le"])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.itemDoubleClicked.connect(lambda _item: self.edit_user())
        layout.addWidget(self.table)

    def _selected_user(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Selection requise", "Veuillez selectionner un utilisateur.")
            return None
        row = selected[0].row()
        return self.current_users[row] if 0 <= row < len(self.current_users) else None

    def load_users(self):
        try:
            self.current_users = data_manager.users.list_users()
        except PermissionError as error:
            QMessageBox.warning(self, "Acces refuse", str(error))
            self.current_users = []
        self.table.setRowCount(len(self.current_users))
        for row_index, user in enumerate(self.current_users):
            values = (
                user.get("username"), user.get("nom_complet"), ROLE_LABELS.get(user.get("role_code"), user.get("role_code")),
                "Actif" if user.get("is_active") else "Desactive", user.get("created_at"), user.get("updated_at"),
            )
            for column, value in enumerate(values):
                item = QTableWidgetItem(str(value or ""))
                if column == 0:
                    item.setData(Qt.UserRole, user.get("id_utilisateur"))
                self.table.setItem(row_index, column, item)
        self.table.resizeColumnsToContents()

    def create_user(self):
        dialog = UserDialog(parent=self)
        if dialog.exec() != QDialog.Accepted:
            return
        try:
            values = dialog.values()
            data_manager.users.create_user(**values)
            self.load_users()
            QMessageBox.information(self, "Succes", "Utilisateur cree avec succes.")
        except (PermissionError, ValueError) as error:
            QMessageBox.warning(self, "Creation refusee", str(error))

    def edit_user(self):
        user = self._selected_user()
        if not user:
            return
        dialog = UserDialog(user, self)
        if dialog.exec() != QDialog.Accepted:
            return
        try:
            values = dialog.values()
            data_manager.users.update_user(user["id_utilisateur"], **values)
            self.load_users()
            QMessageBox.information(self, "Succes", "Utilisateur modifie avec succes.")
        except (PermissionError, ValueError) as error:
            QMessageBox.warning(self, "Modification refusee", str(error))

    def toggle_active(self):
        user = self._selected_user()
        if not user:
            return
        desired = not bool(user.get("is_active"))
        verb = "activer" if desired else "desactiver"
        answer = QMessageBox.question(
            self, "Confirmer", f"Voulez-vous {verb} le compte {user.get('username')} ?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No,
        )
        if answer != QMessageBox.Yes:
            return
        try:
            data_manager.users.set_active(user["id_utilisateur"], desired)
            self.load_users()
        except (PermissionError, ValueError) as error:
            QMessageBox.warning(self, "Operation refusee", str(error))
