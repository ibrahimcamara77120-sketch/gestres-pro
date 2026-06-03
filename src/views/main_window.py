from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QStackedWidget, QMessageBox,
    QInputDialog, QLineEdit
)
from PySide6.QtGui import QIcon

from src.controllers.auth_controller import auth_controller
from src.views.login_view import LoginView
from src.views.dashboard_view import DashboardView
from src.views.styles import COLORS, GLOBAL_STYLE


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self._setup_ui()
        self._connect_signals()
        self._check_initial_setup()

    def _setup_ui(self):
        self.setWindowTitle("GestRes Pro - Gestionnaire de Ressources d'Entreprise")
        self.setMinimumSize(1400, 900)
        self.setStyleSheet(GLOBAL_STYLE)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)

        self.stack = QStackedWidget()
        layout.addWidget(self.stack)

        self.login_view = LoginView()
        self.stack.addWidget(self.login_view)

        self.dashboard_view = DashboardView()
        self.stack.addWidget(self.dashboard_view)

        self.stack.setCurrentWidget(self.login_view)

    def _connect_signals(self):
        self.login_view.login_successful.connect(self._on_login_successful)
        self.dashboard_view.logout_requested.connect(self._on_logout_requested)

    def _check_initial_setup(self):
        try:
            from src.models.base import get_session
            from src.models.user import User, Role

            with get_session() as session:
                super_admin_role = session.query(Role).filter_by(name="super_admin").first()
                if super_admin_role:
                    existing = session.query(User).filter_by(role_id=super_admin_role.id).first()
                    if not existing:
                        self._create_initial_admin()
        except Exception:
            pass

    def _create_initial_admin(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("Configuration initiale")
        msg.setText("🔐 Bienvenue dans GestRes Pro !")
        msg.setInformativeText(
            "Aucun administrateur n'existe encore.\n"
            "Vous allez créer le premier super administrateur."
        )
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.setStyleSheet(f"""
            QMessageBox {{ background-color: {COLORS['white']}; }}
            QMessageBox QLabel {{ color: {COLORS['text_primary']}; font-size: 14px; }}
            QPushButton {{
                background-color: {COLORS['primary']}; color: white;
                border: none; border-radius: 6px; padding: 8px 20px;
                font-size: 14px; min-width: 80px;
            }}
            QPushButton:hover {{ background-color: {COLORS['primary_hover']}; }}
        """)
        msg.exec()

        email, ok = QInputDialog.getText(self, "Super Administrateur", "📧 Email du super administrateur:",
                                         QLineEdit.EchoMode.Normal, "")
        if not ok or not email:
            return

        password, ok = QInputDialog.getText(self, "Super Administrateur",
                                             "🔑 Mot de passe:\n(min 8 caractères, majuscule, minuscule, chiffre, caractère spécial)",
                                             QLineEdit.EchoMode.Password)
        if not ok or not password:
            return

        first_name, ok = QInputDialog.getText(self, "Super Administrateur", "👤 Prénom:",
                                               QLineEdit.EchoMode.Normal, "Admin")
        if not ok:
            first_name = "Admin"

        last_name, ok = QInputDialog.getText(self, "Super Administrateur", "👤 Nom:",
                                              QLineEdit.EchoMode.Normal, "System")
        if not ok:
            last_name = "System"

        success, message = auth_controller.create_initial_super_admin(
            email=email, password=password,
            first_name=first_name or "Admin",
            last_name=last_name or "System"
        )

        if success:
            success_msg = QMessageBox(self)
            success_msg.setWindowTitle("Succès")
            success_msg.setText("✅ Super administrateur créé avec succès !")
            success_msg.setInformativeText(f"Email: {email}\n\nVous pouvez maintenant vous connecter.")
            success_msg.setIcon(QMessageBox.Icon.Information)
            success_msg.setStyleSheet(f"""
                QMessageBox {{ background-color: {COLORS['white']}; }}
                QMessageBox QLabel {{ color: {COLORS['text_primary']}; font-size: 14px; }}
                QPushButton {{
                    background-color: {COLORS['success']}; color: white;
                    border: none; border-radius: 6px; padding: 8px 20px;
                    font-size: 14px; min-width: 80px;
                }}
                QPushButton:hover {{ background-color: #059669; }}
            """)
            success_msg.exec()
        else:
            error_msg = QMessageBox(self)
            error_msg.setWindowTitle("Erreur")
            error_msg.setText("❌ Erreur lors de la création")
            error_msg.setInformativeText(message)
            error_msg.setIcon(QMessageBox.Icon.Warning)
            error_msg.setStyleSheet(f"""
                QMessageBox {{ background-color: {COLORS['white']}; }}
                QMessageBox QLabel {{ color: {COLORS['text_primary']}; font-size: 14px; }}
                QPushButton {{
                    background-color: {COLORS['danger']}; color: white;
                    border: none; border-radius: 6px; padding: 8px 20px;
                    font-size: 14px; min-width: 80px;
                }}
                QPushButton:hover {{ background-color: #dc2626; }}
            """)
            error_msg.exec()
            self._create_initial_admin()

    def _on_login_successful(self):
        try:
            self.dashboard_view.refresh()
            self.stack.setCurrentWidget(self.dashboard_view)
            self.setWindowTitle(f"GestRes Pro - {auth_controller.current_user.full_name}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible de charger le tableau de bord :\n{e}")
            auth_controller.logout()
            self.login_view.reset()

    def _on_logout_requested(self):
        auth_controller.logout()
        self.login_view.reset()
        self.stack.setCurrentWidget(self.login_view)
        self.setWindowTitle("GestRes Pro - Gestionnaire de Ressources d'Entreprise")

    def closeEvent(self, event):
        if auth_controller.is_authenticated:
            msg = QMessageBox(self)
            msg.setWindowTitle("Quitter")
            msg.setText("Voulez-vous vraiment quitter l'application ?")
            msg.setIcon(QMessageBox.Icon.Question)
            msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            msg.setDefaultButton(QMessageBox.StandardButton.No)
            msg.setStyleSheet(f"""
                QMessageBox {{ background-color: {COLORS['white']}; }}
                QMessageBox QLabel {{ color: {COLORS['text_primary']}; font-size: 14px; }}
                QPushButton {{
                    background-color: {COLORS['secondary']}; color: white;
                    border: none; border-radius: 6px; padding: 8px 20px;
                    font-size: 14px; min-width: 80px;
                }}
                QPushButton:hover {{ background-color: {COLORS['secondary_hover']}; }}
            """)

            if msg.exec() == QMessageBox.StandardButton.Yes:
                auth_controller.logout()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()
