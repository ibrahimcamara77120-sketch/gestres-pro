from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFrame, QSpacerItem,
    QSizePolicy, QGraphicsDropShadowEffect
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont, QColor

from src.controllers.auth_controller import auth_controller
from src.views.styles import COLORS, primary_button_style


class LoginView(QWidget):
    login_successful = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['sidebar_bg']};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        center_layout = QHBoxLayout()
        layout.addLayout(center_layout)
        center_layout.addStretch()

        container = QFrame()
        container.setFixedWidth(400)
        container.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['white']};
                border-radius: 8px;
                border: 1px solid {COLORS['border']};
            }}
        """)


        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(40, 50, 40, 50)
        container_layout.setSpacing(0)

        logo_label = QLabel("GR")
        logo_label.setFixedSize(52, 52)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_label.setStyleSheet(f"""
            background-color: {COLORS['primary']};
            color: white;
            border-radius: 6px;
            font-size: 20px;
            font-weight: bold;
        """)
        logo_wrapper = QHBoxLayout()
        logo_wrapper.addStretch()
        logo_wrapper.addWidget(logo_label)
        logo_wrapper.addStretch()
        container_layout.addLayout(logo_wrapper)

        container_layout.addSpacing(16)

        title = QLabel("Connexion")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"""
            font-size: 28px;
            font-weight: bold;
            color: {COLORS['text_primary']};
            background: transparent;
        """)
        container_layout.addWidget(title)

        subtitle = QLabel("Gestionnaire de Ressources d'Entreprise")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet(f"""
            font-size: 14px;
            color: {COLORS['text_secondary']};
            background: transparent;
            margin-top: 8px;
        """)
        container_layout.addWidget(subtitle)

        container_layout.addSpacing(35)

        email_label = QLabel("Adresse email")
        email_label.setStyleSheet(f"""
            font-size: 13px;
            font-weight: 600;
            color: {COLORS['text_primary']};
            background: transparent;
            margin-bottom: 6px;
        """)
        container_layout.addWidget(email_label)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("vous@exemple.com")
        self.email_input.setMinimumHeight(48)
        self.email_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {COLORS['white']};
                color: {COLORS['text_primary']};
                border: 2px solid {COLORS['border']};
                border-radius: 10px;
                padding: 12px 16px;
                font-size: 15px;
            }}
            QLineEdit:focus {{
                border-color: {COLORS['primary']};
            }}
            QLineEdit::placeholder {{
                color: {COLORS['text_muted']};
            }}
        """)
        container_layout.addWidget(self.email_input)

        container_layout.addSpacing(20)

        password_label = QLabel("Mot de passe")
        password_label.setStyleSheet(f"""
            font-size: 13px;
            font-weight: 600;
            color: {COLORS['text_primary']};
            background: transparent;
            margin-bottom: 6px;
        """)
        container_layout.addWidget(password_label)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Votre mot de passe")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setMinimumHeight(48)
        self.password_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {COLORS['white']};
                color: {COLORS['text_primary']};
                border: 2px solid {COLORS['border']};
                border-radius: 10px;
                padding: 12px 16px;
                font-size: 15px;
            }}
            QLineEdit:focus {{
                border-color: {COLORS['primary']};
            }}
            QLineEdit::placeholder {{
                color: {COLORS['text_muted']};
            }}
        """)
        container_layout.addWidget(self.password_input)

        container_layout.addSpacing(12)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet(f"""
            color: {COLORS['danger']};
            font-size: 13px;
            background-color: {COLORS['danger_light']};
            border-radius: 8px;
            padding: 10px;
        """)
        self.error_label.setWordWrap(True)
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_label.hide()
        container_layout.addWidget(self.error_label)

        container_layout.addSpacing(25)

        self.login_button = QPushButton("Se connecter")
        self.login_button.setMinimumHeight(52)
        self.login_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['primary']};
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 16px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {COLORS['primary_hover']};
            }}
            QPushButton:pressed {{
                background-color: #1e40af;
            }}
            QPushButton:disabled {{
                background-color: {COLORS['border']};
                color: {COLORS['text_muted']};
            }}
        """)
        container_layout.addWidget(self.login_button)

        container_layout.addSpacing(30)

        footer = QLabel("Projet BTS SIO - Gestion des Ressources")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setStyleSheet(f"""
            font-size: 12px;
            color: {COLORS['text_muted']};
            background: transparent;
        """)
        container_layout.addWidget(footer)

        center_layout.addWidget(container)
        center_layout.addStretch()

    def _connect_signals(self):
        self.login_button.clicked.connect(self._on_login_clicked)
        self.password_input.returnPressed.connect(self._on_login_clicked)
        self.email_input.returnPressed.connect(self.password_input.setFocus)

    def _on_login_clicked(self):
        email = self.email_input.text().strip()
        password = self.password_input.text()

        if not email:
            self._show_error("Veuillez entrer votre adresse email")
            self.email_input.setFocus()
            return

        if not password:
            self._show_error("Veuillez entrer votre mot de passe")
            self.password_input.setFocus()
            return

        self.login_button.setEnabled(False)
        self.login_button.setText("Connexion en cours...")

        success, message = auth_controller.login(email, password)

        if success:
            self._clear_error()
            self.login_successful.emit()
        else:
            self._show_error(message)
            self.password_input.clear()
            self.password_input.setFocus()

        self.login_button.setEnabled(True)
        self.login_button.setText("Se connecter")

    def _show_error(self, message: str):
        self.error_label.setText(message)
        self.error_label.show()

    def _clear_error(self):
        self.error_label.setText("")
        self.error_label.hide()

    def reset(self):
        self.email_input.clear()
        self.password_input.clear()
        self._clear_error()
        self.email_input.setFocus()
