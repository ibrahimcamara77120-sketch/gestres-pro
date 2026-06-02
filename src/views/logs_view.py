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

    _ACTION_BADGE = {
        "LOGIN":           ("#059669", "#d1fae5"),
        "LOGOUT":          ("#64748b", "#f1f5f9"),
        "LOGIN_FAILED":    ("#dc2626", "#fee2e2"),
        "CREATE":          ("#4f46e5", "#eef2ff"),
        "UPDATE":          ("#d97706", "#fef3c7"),
        "DELETE":          ("#dc2626", "#fee2e2"),
        "PASSWORD_CHANGE": ("#0284c7", "#e0f2fe"),
        "PASSWORD_RESET":  ("#0284c7", "#e0f2fe"),
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self._all_logs = []
        self._setup_ui()
        self.load_data()

    def _setup_ui(self):
        from PySide6.QtWidgets import QPushButton, QFrame
        from src.views.users_view import _page_header

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header with export button
        header_frame = _page_header("📊  Journaux d'audit",
                                    "Traçabilité complète de toutes les actions utilisateurs")
        # Inject export button into the header frame
        export_btn = QPushButton("⬇️  Exporter CSV")
        export_btn.setFixedHeight(36)
        export_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        export_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['white']};
                color: {COLORS['text_secondary']};
                border: 1.5px solid {COLORS['border']};
                border-radius: 8px;
                padding: 0px 16px;
                font-size: 13px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {COLORS['primary_light']};
                border-color: {COLORS['primary']};
                color: {COLORS['primary']};
            }}
        """)
        export_btn.clicked.connect(self._export_csv)
        # Inject into header layout
        header_inner = header_frame.layout()
        if header_inner:
            row = QHBoxLayout()
            row.setContentsMargins(0, 0, 0, 0)
            row.addStretch()
            row.addWidget(export_btn)
            header_inner.addLayout(row)
        layout.addWidget(header_frame)

        inner = QWidget()
        inner.setStyleSheet(f"background-color: {COLORS['background']};")
        inner_layout = QVBoxLayout(inner)
        inner_layout.setContentsMargins(30, 24, 30, 24)
        inner_layout.setSpacing(0)

        columns = [
            {"key": "created_at", "label": "🕐  Date / Heure",  "width": 165},
            {"key": "action",     "label": "⚡  Action",         "width": 160},
            {"key": "user_name",  "label": "👤  Utilisateur"},
            {"key": "table_name", "label": "🗄️  Table",         "width": 120},
            {"key": "record_id",  "label": "ID",                 "width": 65},
            {"key": "ip_address", "label": "🌐  IP",             "width": 130},
        ]

        self.table = DataTable(columns, title="Historique des actions",
                               show_add_button=False, page_size=20)

        self.table.add_filter("Action", [("Toutes les actions", None)] + [(a, a) for a in ACTIONS], "action")

        self.table.set_actions([])
        self.table.refresh_clicked.connect(self.load_data)

        inner_layout.addWidget(self.table)
        layout.addWidget(inner)

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

            self.table.set_data(self._all_logs)
            self._apply_action_badges()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible de charger les journaux : {e}")

    def _apply_action_badges(self):
        for row_idx in range(self.table.table.rowCount()):
            start = (self.table._current_page - 1) * self.table._page_size
            idx = start + row_idx
            if idx < len(self.table._filtered_data):
                action = self.table._filtered_data[idx].get("action", "")
                if action in self._ACTION_BADGE:
                    tc, bc = self._ACTION_BADGE[action]
                    self.table.set_status_badge(row_idx, 1, action, tc, bc)


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
