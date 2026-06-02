"""
Assistant de configuration — premier lancement.
Affiché quand aucun fichier .env n'existe ou que la BDD est inaccessible.
"""
from pathlib import Path

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFrame, QSpinBox,
    QGraphicsDropShadowEffect, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QLinearGradient, QBrush

from src.views.styles import COLORS


class SetupWizard(QDialog):
    """Dialogue de configuration initiale de la base de données."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuration GestRes Pro")
        self.setMinimumWidth(500)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowCloseButtonHint)
        self.setStyleSheet(f"background-color: {COLORS['white']};")
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Bandeau header
        header = QFrame()
        header.setFixedHeight(90)
        header.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {COLORS['sidebar_bg']}, stop:1 #312e81);
                border: none;
            }}
        """)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(28, 0, 28, 0)

        logo = QLabel("GR")
        logo.setFixedSize(44, 44)
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setStyleSheet(f"""
            background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                stop:0 {COLORS['primary']}, stop:1 #8b5cf6);
            color: white; border-radius: 10px;
            font-size: 18px; font-weight: 800;
        """)
        header_layout.addWidget(logo)
        header_layout.addSpacing(14)

        h_text = QVBoxLayout()
        h_text.setSpacing(2)
        t = QLabel("GestRes Pro — Configuration")
        t.setStyleSheet("color: white; font-size: 17px; font-weight: 700; background: transparent;")
        s = QLabel("Connexion à la base de données PostgreSQL")
        s.setStyleSheet(f"color: {COLORS['sidebar_text']}; font-size: 12px; background: transparent;")
        h_text.addWidget(t)
        h_text.addWidget(s)
        header_layout.addLayout(h_text)
        header_layout.addStretch()
        layout.addWidget(header)

        # Corps
        body = QVBoxLayout()
        body.setContentsMargins(28, 24, 28, 24)
        body.setSpacing(16)

        info = QLabel(
            "Renseignez les informations de connexion à votre serveur PostgreSQL.\n"
            "Ces paramètres seront sauvegardés localement dans un fichier .env."
        )
        info.setWordWrap(True)
        info.setStyleSheet(f"""
            color: {COLORS['text_secondary']};
            font-size: 13px;
            background-color: {COLORS['primary_light']};
            border-left: 3px solid {COLORS['primary']};
            border-radius: 6px;
            padding: 12px 14px;
        """)
        body.addWidget(info)

        def field(label_text, placeholder, default=""):
            row = QVBoxLayout()
            row.setSpacing(6)
            lbl = QLabel(label_text)
            lbl.setStyleSheet(f"font-size: 13px; font-weight: 600; color: {COLORS['text_primary']}; background: transparent;")
            inp = QLineEdit()
            inp.setPlaceholderText(placeholder)
            inp.setText(default)
            inp.setMinimumHeight(42)
            inp.setStyleSheet(f"""
                QLineEdit {{
                    background: {COLORS['surface_raised']};
                    border: 1.5px solid {COLORS['border']};
                    border-radius: 8px;
                    padding: 10px 14px;
                    font-size: 14px;
                    color: {COLORS['text_primary']};
                }}
                QLineEdit:focus {{ border-color: {COLORS['primary']}; background: white; }}
            """)
            row.addWidget(lbl)
            row.addWidget(inp)
            return row, inp

        row1, self.host_input = field("Hôte du serveur", "localhost", "localhost")
        body.addLayout(row1)

        # Port sur la même ligne que la base
        two_col = QHBoxLayout()
        two_col.setSpacing(14)

        port_col = QVBoxLayout()
        port_col.setSpacing(6)
        port_lbl = QLabel("Port")
        port_lbl.setStyleSheet(f"font-size: 13px; font-weight: 600; color: {COLORS['text_primary']}; background: transparent;")
        self.port_input = QSpinBox()
        self.port_input.setRange(1, 65535)
        self.port_input.setValue(5432)
        self.port_input.setMinimumHeight(42)
        self.port_input.setStyleSheet(f"""
            QSpinBox {{
                background: {COLORS['surface_raised']};
                border: 1.5px solid {COLORS['border']};
                border-radius: 8px;
                padding: 10px 14px;
                font-size: 14px;
                color: {COLORS['text_primary']};
            }}
            QSpinBox:focus {{ border-color: {COLORS['primary']}; }}
        """)
        port_col.addWidget(port_lbl)
        port_col.addWidget(self.port_input)
        two_col.addLayout(port_col)

        db_col, self.db_input = field("Nom de la base", "gestres_pro", "gestres_pro")
        two_col.addLayout(db_col)
        body.addLayout(two_col)

        row3, self.user_input = field("Utilisateur PostgreSQL", "gestres_user", "gestres_user")
        body.addLayout(row3)

        pwd_col = QVBoxLayout()
        pwd_col.setSpacing(6)
        pwd_lbl = QLabel("Mot de passe")
        pwd_lbl.setStyleSheet(f"font-size: 13px; font-weight: 600; color: {COLORS['text_primary']}; background: transparent;")
        self.pwd_input = QLineEdit()
        self.pwd_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pwd_input.setPlaceholderText("Mot de passe de l'utilisateur PostgreSQL")
        self.pwd_input.setMinimumHeight(42)
        self.pwd_input.setStyleSheet(f"""
            QLineEdit {{
                background: {COLORS['surface_raised']};
                border: 1.5px solid {COLORS['border']};
                border-radius: 8px;
                padding: 10px 14px;
                font-size: 14px;
                color: {COLORS['text_primary']};
            }}
            QLineEdit:focus {{ border-color: {COLORS['primary']}; background: white; }}
        """)
        pwd_col.addWidget(pwd_lbl)
        pwd_col.addWidget(self.pwd_input)
        body.addLayout(pwd_col)

        self.error_label = QLabel()
        self.error_label.setStyleSheet(f"""
            color: {COLORS['danger_dark']}; font-size: 13px;
            background: {COLORS['danger_light']};
            border-left: 3px solid {COLORS['danger']};
            border-radius: 6px; padding: 10px 14px;
        """)
        self.error_label.setWordWrap(True)
        self.error_label.hide()
        body.addWidget(self.error_label)

        # Boutons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        test_btn = QPushButton("🔌  Tester la connexion")
        test_btn.setMinimumHeight(44)
        test_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        test_btn.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS['white']};
                color: {COLORS['text_primary']};
                border: 1.5px solid {COLORS['border']};
                border-radius: 8px;
                font-size: 14px; font-weight: 500;
                padding: 0 20px;
            }}
            QPushButton:hover {{
                background: {COLORS['primary_light']};
                border-color: {COLORS['primary']};
                color: {COLORS['primary']};
            }}
        """)
        test_btn.clicked.connect(self._test_connection)
        btn_row.addWidget(test_btn)

        save_btn = QPushButton("✅  Enregistrer et continuer")
        save_btn.setMinimumHeight(44)
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 {COLORS['primary']}, stop:1 #8b5cf6);
                color: white; border: none;
                border-radius: 8px;
                font-size: 14px; font-weight: 700;
                padding: 0 24px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 {COLORS['primary_hover']}, stop:1 #7c3aed);
            }}
        """)
        save_btn.clicked.connect(self._save_config)
        btn_row.addWidget(save_btn)

        body.addLayout(btn_row)
        layout.addLayout(body)

    def _get_values(self):
        return {
            "host": self.host_input.text().strip() or "localhost",
            "port": str(self.port_input.value()),
            "db": self.db_input.text().strip() or "gestres_pro",
            "user": self.user_input.text().strip() or "gestres_user",
            "pwd": self.pwd_input.text(),
        }

    def _test_connection(self):
        v = self._get_values()
        try:
            import psycopg2
            conn = psycopg2.connect(
                host=v["host"], port=int(v["port"]),
                dbname=v["db"], user=v["user"], password=v["pwd"],
                connect_timeout=5
            )
            conn.close()
            self.error_label.hide()
            QMessageBox.information(self, "Connexion réussie",
                "✅ Connexion à PostgreSQL établie avec succès !")
        except Exception as e:
            self.error_label.setText(f"❌ Connexion échouée : {e}")
            self.error_label.show()

    def _save_config(self):
        v = self._get_values()
        if not v["pwd"]:
            self.error_label.setText("Le mot de passe est requis.")
            self.error_label.show()
            return

        env_path = Path(__file__).parent.parent.parent / ".env"
        env_path.write_text(
            f"DB_HOST={v['host']}\n"
            f"DB_PORT={v['port']}\n"
            f"DB_NAME={v['db']}\n"
            f"DB_USER={v['user']}\n"
            f"DB_PASSWORD={v['pwd']}\n"
        )
        self.accept()
