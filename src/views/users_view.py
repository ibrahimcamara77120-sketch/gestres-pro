from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QDialog, QFormLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QMessageBox,
    QFrame, QScrollArea
)
from PySide6.QtCore import Qt

from src.views.styles import COLORS, primary_button_style, secondary_button_style, danger_button_style
from src.views.widgets.data_table import DataTable
from src.controllers.user_controller import user_controller
from src.controllers.company_controller import company_controller
from src.controllers.auth_controller import auth_controller


class UserFormDialog(QDialog):

    def __init__(self, parent=None, user_data: dict = None):
        super().__init__(parent)
        self._user_data = user_data
        self._roles = user_controller.get_all_roles()
        self._companies = company_controller.get_all_companies()
        self._setup_ui()
        if user_data:
            self._populate(user_data)

    def _setup_ui(self):
        is_edit = self._user_data is not None
        self.setWindowTitle("Modifier l'utilisateur" if is_edit else "Nouvel utilisateur")
        self.setMinimumWidth(480)
        self.setStyleSheet(f"background-color: {COLORS['white']};")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(20)

        title = QLabel("Modifier l'utilisateur" if is_edit else "Créer un utilisateur")
        title.setStyleSheet(f"font-size: 18px; font-weight: 700; color: {COLORS['text_primary']};")
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(14)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("nom@entreprise.com")
        form.addRow(self._label("Email *"), self.email_input)

        if not is_edit:
            self.password_input = QLineEdit()
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.password_input.setPlaceholderText("Min 8 car., maj, chiffre, symbole")
            form.addRow(self._label("Mot de passe *"), self.password_input)

        self.first_name_input = QLineEdit()
        self.first_name_input.setPlaceholderText("Prénom")
        form.addRow(self._label("Prénom"), self.first_name_input)

        self.last_name_input = QLineEdit()
        self.last_name_input.setPlaceholderText("Nom de famille")
        form.addRow(self._label("Nom"), self.last_name_input)

        self.role_combo = QComboBox()
        for role in self._roles:
            self.role_combo.addItem(role["display_name"], role["id"])
        form.addRow(self._label("Rôle *"), self.role_combo)

        self.company_combo = QComboBox()
        self.company_combo.addItem("Aucune entreprise", None)
        for c in self._companies:
            self.company_combo.addItem(c["name"], c["id"])
        form.addRow(self._label("Entreprise"), self.company_combo)

        layout.addLayout(form)

        self.error_label = QLabel()
        self.error_label.setStyleSheet(f"color: {COLORS['danger']}; font-size: 13px;")
        self.error_label.setWordWrap(True)
        self.error_label.hide()
        layout.addWidget(self.error_label)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        cancel_btn = QPushButton("Annuler")
        cancel_btn.setStyleSheet(secondary_button_style())
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        self.save_btn = QPushButton("Enregistrer")
        self.save_btn.setStyleSheet(primary_button_style())
        self.save_btn.clicked.connect(self._on_save)
        btn_layout.addWidget(self.save_btn)

        layout.addLayout(btn_layout)

    def _label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(f"font-size: 13px; font-weight: 600; color: {COLORS['text_primary']}; background: transparent;")
        return lbl

    def _populate(self, data: dict):
        self.email_input.setText(data.get("email", ""))
        self.first_name_input.setText(data.get("first_name", ""))
        self.last_name_input.setText(data.get("last_name", ""))

        for i in range(self.role_combo.count()):
            if self.role_combo.itemData(i) == data.get("role_id"):
                self.role_combo.setCurrentIndex(i)
                break

        for i in range(self.company_combo.count()):
            if self.company_combo.itemData(i) == data.get("company_id"):
                self.company_combo.setCurrentIndex(i)
                break

    def _on_save(self):
        is_edit = self._user_data is not None
        email = self.email_input.text().strip()
        first_name = self.first_name_input.text().strip()
        last_name = self.last_name_input.text().strip()
        role_id = self.role_combo.currentData()
        company_id = self.company_combo.currentData()

        if is_edit:
            success, msg = user_controller.update_user(
                self._user_data["id"],
                email=email,
                first_name=first_name,
                last_name=last_name,
                role_id=role_id,
                company_id=company_id if company_id else -1
            )
        else:
            password = self.password_input.text()
            success, msg, _ = user_controller.create_user(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role_id=role_id,
                company_id=company_id
            )

        if success:
            self.accept()
        else:
            self.error_label.setText(msg)
            self.error_label.show()


class ResetPasswordDialog(QDialog):

    def __init__(self, user_id: int, user_name: str, parent=None):
        super().__init__(parent)
        self._user_id = user_id
        self.setWindowTitle("Réinitialiser le mot de passe")
        self.setMinimumWidth(420)
        self.setStyleSheet(f"background-color: {COLORS['white']};")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(20)

        title = QLabel(f"Réinitialiser le mot de passe")
        title.setStyleSheet(f"font-size: 18px; font-weight: 700; color: {COLORS['text_primary']};")
        layout.addWidget(title)

        info = QLabel(f"Utilisateur : {user_name}")
        info.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 13px;")
        layout.addWidget(info)

        form = QFormLayout()
        form.setSpacing(14)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Nouveau mot de passe")
        form.addRow(QLabel("Nouveau mot de passe *"), self.password_input)

        self.confirm_input = QLineEdit()
        self.confirm_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_input.setPlaceholderText("Confirmer le mot de passe")
        form.addRow(QLabel("Confirmation *"), self.confirm_input)

        layout.addLayout(form)

        self.error_label = QLabel()
        self.error_label.setStyleSheet(f"color: {COLORS['danger']}; font-size: 13px;")
        self.error_label.hide()
        layout.addWidget(self.error_label)

        btn_layout = QHBoxLayout()
        cancel_btn = QPushButton("Annuler")
        cancel_btn.setStyleSheet(secondary_button_style())
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        save_btn = QPushButton("Réinitialiser")
        save_btn.setStyleSheet(primary_button_style())
        save_btn.clicked.connect(self._on_save)
        btn_layout.addWidget(save_btn)

        layout.addLayout(btn_layout)

    def _on_save(self):
        pwd = self.password_input.text()
        confirm = self.confirm_input.text()

        if pwd != confirm:
            self.error_label.setText("Les mots de passe ne correspondent pas")
            self.error_label.show()
            return

        success, msg = user_controller.reset_password(self._user_id, pwd)
        if success:
            self.accept()
        else:
            self.error_label.setText(msg)
            self.error_label.show()


class UsersView(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self.load_data()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        header = QHBoxLayout()
        title = QLabel("Utilisateurs")
        title.setStyleSheet(f"font-size: 24px; font-weight: 700; color: {COLORS['text_primary']}; background: transparent;")
        header.addWidget(title)
        header.addStretch()
        layout.addLayout(header)

        columns = [
            {"key": "full_name", "label": "Nom complet"},
            {"key": "email", "label": "Email"},
            {"key": "role_display", "label": "Rôle"},
            {"key": "company_name", "label": "Entreprise"},
            {"key": "status", "label": "Statut", "width": 100,
             "style": lambda v, r: {"color": COLORS["success"] if r.get("is_active") else COLORS["danger"]}},
            {"key": "last_login", "label": "Dernière connexion", "width": 160},
        ]

        self.table = DataTable(columns, title="Liste des utilisateurs", page_size=15)
        self.table.set_actions([
            {"name": "edit", "icon": "✏️", "label": "Modifier", "color": COLORS["primary"]},
            {"name": "reset_pwd", "icon": "🔑", "label": "Réinitialiser mdp", "color": COLORS["warning"]},
            {"name": "toggle", "icon": "🔄", "label": "Activer/Désactiver", "color": COLORS["secondary"]},
        ])

        is_admin = auth_controller.is_admin()
        self.table.add_button.setVisible(is_admin)

        self.table.add_clicked.connect(self._on_add)
        self.table.refresh_clicked.connect(self.load_data)
        self.table.action_triggered.connect(self._on_action)

        layout.addWidget(self.table)

    def load_data(self):
        try:
            users = user_controller.get_all_users()
            self.table.set_data(users)
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible de charger les utilisateurs : {e}")

    def _on_add(self):
        dialog = UserFormDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_data()

    def _on_action(self, action: str, user_id: int):
        if action == "edit":
            data = user_controller.get_user_by_id(user_id)
            if data:
                dialog = UserFormDialog(self, data)
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    self.load_data()

        elif action == "reset_pwd":
            data = user_controller.get_user_by_id(user_id)
            if data:
                dialog = ResetPasswordDialog(user_id, data["full_name"], self)
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    QMessageBox.information(self, "Succès", "Mot de passe réinitialisé.")

        elif action == "toggle":
            if auth_controller.current_user and auth_controller.current_user.id == user_id:
                QMessageBox.warning(self, "Action impossible", "Vous ne pouvez pas modifier votre propre compte ici.")
                return
            data = user_controller.get_user_by_id(user_id)
            if data:
                action_label = "désactiver" if data["is_active"] else "réactiver"
                reply = QMessageBox.question(
                    self, "Confirmation",
                    f"Voulez-vous {action_label} cet utilisateur ?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.Yes:
                    if data["is_active"]:
                        success, msg = user_controller.delete_user(user_id)
                    else:
                        success, msg = user_controller.update_user(user_id, is_active=True)
                    if success:
                        self.load_data()
                    else:
                        QMessageBox.warning(self, "Erreur", msg)
