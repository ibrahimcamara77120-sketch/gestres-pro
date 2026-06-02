from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFrame, QSizePolicy,
    QGraphicsDropShadowEffect
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont, QColor, QPainter, QLinearGradient, QBrush

from src.controllers.auth_controller import auth_controller
from src.views.styles import COLORS, primary_button_style


class GradientBackground(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0.0, QColor("#1e1b4b"))
        gradient.setColorAt(0.5, QColor("#312e81"))
        gradient.setColorAt(1.0, QColor("#4c1d95"))
        painter.fillRect(self.rect(), QBrush(gradient))


class LoginView(QWidget):
    login_successful = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        # Fond dégradé
        self._bg = GradientBackground(self)
        outer_layout.addWidget(self._bg)

        # Centrage horizontal + vertical dans le fond dégradé
        center_h = QHBoxLayout(self._bg)
        center_h.setContentsMargins(0, 0, 0, 0)
        center_h.addStretch(1)

        center_v = QVBoxLayout()
        center_v.setContentsMargins(0, 0, 0, 0)
        center_h.addLayout(center_v)
        center_h.addStretch(1)

        center_v.addStretch(1)

        # Carte de connexion
        card = QFrame()
        card.setFixedWidth(420)
        card.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.97);
                border-radius: 20px;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
        """)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(60)
        shadow.setXOffset(0)
        shadow.setYOffset(20)
        shadow.setColor(QColor(0, 0, 0, 80))
        card.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(44, 48, 44, 48)
        card_layout.setSpacing(0)

        # Logo
        logo_row = QHBoxLayout()
        logo_row.addStretch()
        logo = QLabel("GR")
        logo.setFixedSize(56, 56)
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 {COLORS['primary']}, stop:1 #8b5cf6);
            color: white;
            border-radius: 14px;
            font-size: 22px;
            font-weight: 800;
        """)
        logo_row.addWidget(logo)
        logo_row.addStretch()
        card_layout.addLayout(logo_row)

        card_layout.addSpacing(24)

        # Titre
        title = QLabel("Bienvenue")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"""
            font-size: 30px;
            font-weight: 800;
            color: {COLORS['text_primary']};
            background: transparent;
            letter-spacing: -0.5px;
        """)
        card_layout.addWidget(title)

        subtitle = QLabel("Connectez-vous à GestRes Pro")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet(f"""
            font-size: 14px;
            color: {COLORS['text_muted']};
            background: transparent;
            margin-top: 6px;
        """)
        card_layout.addWidget(subtitle)

        card_layout.addSpacing(36)

        # Email
        email_label = QLabel("Adresse email")
        email_label.setStyleSheet(f"""
            font-size: 13px;
            font-weight: 600;
            color: {COLORS['text_secondary']};
            background: transparent;
            margin-bottom: 6px;
        """)
        card_layout.addWidget(email_label)

        card_layout.addSpacing(6)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("vous@exemple.com")
        self.email_input.setMinimumHeight(48)
        self.email_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {COLORS['surface_raised']};
                color: {COLORS['text_primary']};
                border: 1.5px solid {COLORS['border']};
                border-radius: 10px;
                padding: 12px 16px;
                font-size: 15px;
            }}
            QLineEdit:focus {{
                border: 2px solid {COLORS['primary']};
                background-color: {COLORS['white']};
            }}
            QLineEdit::placeholder {{
                color: {COLORS['text_muted']};
            }}
        """)
        card_layout.addWidget(self.email_input)

        card_layout.addSpacing(20)

        # Mot de passe
        pwd_label = QLabel("Mot de passe")
        pwd_label.setStyleSheet(f"""
            font-size: 13px;
            font-weight: 600;
            color: {COLORS['text_secondary']};
            background: transparent;
            margin-bottom: 6px;
        """)
        card_layout.addWidget(pwd_label)

        card_layout.addSpacing(6)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Votre mot de passe")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setMinimumHeight(48)
        self.password_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {COLORS['surface_raised']};
                color: {COLORS['text_primary']};
                border: 1.5px solid {COLORS['border']};
                border-radius: 10px;
                padding: 12px 16px;
                font-size: 15px;
            }}
            QLineEdit:focus {{
                border: 2px solid {COLORS['primary']};
                background-color: {COLORS['white']};
            }}
            QLineEdit::placeholder {{
                color: {COLORS['text_muted']};
            }}
        """)
        card_layout.addWidget(self.password_input)

        card_layout.addSpacing(12)

        # Erreur
        self.error_label = QLabel("")
        self.error_label.setStyleSheet(f"""
            color: {COLORS['danger_dark']};
            font-size: 13px;
            font-weight: 500;
            background-color: {COLORS['danger_light']};
            border-radius: 8px;
            border-left: 3px solid {COLORS['danger']};
            padding: 10px 14px;
        """)
        self.error_label.setWordWrap(True)
        self.error_label.hide()
        card_layout.addWidget(self.error_label)

        card_layout.addSpacing(24)

        # Bouton
        self.login_button = QPushButton("Se connecter")
        self.login_button.setMinimumHeight(52)
        self.login_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_button.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {COLORS['primary']}, stop:1 #8b5cf6);
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 16px;
                font-weight: 700;
                letter-spacing: 0.3px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {COLORS['primary_hover']}, stop:1 #7c3aed);
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {COLORS['primary_dark']}, stop:1 #6d28d9);
            }}
            QPushButton:disabled {{
                background: {COLORS['border']};
                color: {COLORS['text_muted']};
            }}
        """)
        card_layout.addWidget(self.login_button)

        card_layout.addSpacing(28)

        # Footer
        footer = QLabel("GestRes Pro · BTS SIO SLAM 2026")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setStyleSheet(f"""
            font-size: 12px;
            color: {COLORS['text_muted']};
            background: transparent;
        """)
        card_layout.addWidget(footer)

        center_v.addWidget(card, 0, Qt.AlignmentFlag.AlignHCenter)
        center_v.addStretch(1)

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
        self.login_button.setText("Connexion…")

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
