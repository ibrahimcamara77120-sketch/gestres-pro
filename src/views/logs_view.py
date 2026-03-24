from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QMessageBox, QFileDialog
)
from PySide6.QtCore import Qt
import csv

from src.views.styles import COLORS
from src.views.widgets.data_table import DataTable
from src.models.base import get_session
from src.models.audit_log import AuditLog
from src.models.user import User


ACTIONS = [
    "LOGIN", "LOGOUT", "LOGIN_FAILED",
    "CREATE", "UPDATE", "DELETE",
    "PASSWORD_CHANGE", "PASSWORD_RESET"
]


class LogsView(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._all_logs = []
        self._setup_ui()
        self.load_data()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        header = QHBoxLayout()
        title = QLabel("Journaux d'audit")
        title.setStyleSheet(f"font-size: 24px; font-weight: 700; color: {COLORS['text_primary']}; background: transparent;")
        header.addWidget(title)
        header.addStretch()

        filter_label = QLabel("Action :")
        filter_label.setStyleSheet(f"color: {COLORS['text_secondary']}; background: transparent;")
        header.addWidget(filter_label)

        self.action_filter = QComboBox()
        self.action_filter.setFixedWidth(180)
        self.action_filter.addItem("Toutes les actions", None)
        for action in ACTIONS:
            self.action_filter.addItem(action, action)
        self.action_filter.currentIndexChanged.connect(self._apply_filter)
        header.addWidget(self.action_filter)

        from PySide6.QtWidgets import QPushButton
        export_btn = QPushButton("Exporter CSV")
        export_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['white']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 13px;
            }}
            QPushButton:hover {{ background-color: {COLORS['border_light']}; }}
        """)
        export_btn.clicked.connect(self._export_csv)
        header.addWidget(export_btn)

        layout.addLayout(header)

        columns = [
            {"key": "created_at", "label": "Date / Heure", "width": 160},
            {"key": "action", "label": "Action", "width": 150,
             "style": lambda v, r: {"color": self._action_color(v)}},
            {"key": "user_name", "label": "Utilisateur"},
            {"key": "table_name", "label": "Table", "width": 120},
            {"key": "record_id", "label": "ID", "width": 70},
            {"key": "ip_address", "label": "IP", "width": 130},
        ]

        self.table = DataTable(columns, title="Historique des actions",
                               show_add_button=False, page_size=20)
        self.table.set_actions([])

        self.table.refresh_clicked.connect(self.load_data)

        layout.addWidget(self.table)

    def load_data(self):
        try:
            with get_session() as session:
                logs = session.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(500).all()
                user_ids = {log.user_id for log in logs if log.user_id}
                users = {}
                if user_ids:
                    for user in session.query(User).filter(User.id.in_(user_ids)).all():
                        users[user.id] = user.full_name

                self._all_logs = []
                for log in logs:
                    self._all_logs.append({
                        "id": log.id,
                        "created_at": log.created_at.strftime("%d/%m/%Y %H:%M:%S") if log.created_at else "",
                        "action": log.action,
                        "user_name": users.get(log.user_id, "Système") if log.user_id else "Système",
                        "table_name": log.table_name or "",
                        "record_id": str(log.record_id) if log.record_id else "",
                        "ip_address": log.ip_address or "",
                    })

            self._apply_filter()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible de charger les journaux : {e}")

    def _apply_filter(self):
        action = self.action_filter.currentData()
        if action:
            filtered = [log for log in self._all_logs if log["action"] == action]
        else:
            filtered = self._all_logs
        self.table.set_data(filtered)

    def _action_color(self, action: str) -> str:
        colors = {
            "LOGIN": COLORS["success"],
            "LOGOUT": COLORS["secondary"],
            "LOGIN_FAILED": COLORS["danger"],
            "CREATE": COLORS["primary"],
            "UPDATE": COLORS["warning"],
            "DELETE": COLORS["danger"],
            "PASSWORD_CHANGE": COLORS["info"],
            "PASSWORD_RESET": COLORS["info"],
        }
        return colors.get(action, COLORS["text_primary"])

    def _export_csv(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Exporter les journaux", "journaux_audit.csv", "CSV (*.csv)"
        )
        if not path:
            return

        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=[
                    "created_at", "action", "user_name", "table_name", "record_id", "ip_address"
                ])
                writer.writeheader()
                for log in self._all_logs:
                    writer.writerow({k: log.get(k, "") for k in writer.fieldnames})
            QMessageBox.information(self, "Export réussi", f"Journaux exportés : {path}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Export échoué : {e}")
