from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QDialog, QFormLayout,
    QLabel, QPushButton, QComboBox, QMessageBox, QTextEdit,
    QDateEdit, QFrame
)
from PySide6.QtCore import Qt, QDate

from src.views.styles import COLORS, primary_button_style, secondary_button_style, danger_button_style
from src.views.widgets.data_table import DataTable
from src.controllers.assignment_controller import assignment_controller
from src.controllers.resource_controller import resource_controller
from src.controllers.user_controller import user_controller
from src.controllers.auth_controller import auth_controller
import config


class AssignmentFormDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nouvelle affectation")
        self.setMinimumWidth(500)
        self.setStyleSheet(f"background-color: {COLORS['white']};")
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(20)

        title = QLabel("Créer une affectation")
        title.setStyleSheet(f"font-size: 18px; font-weight: 700; color: {COLORS['text_primary']};")
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(14)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

        self.resource_combo = QComboBox()
        available = resource_controller.get_all_resources(status="available")
        for r in available:
            self.resource_combo.addItem(f"{r['name']} ({r['resource_type_name']})", r["id"])
        if not available:
            self.resource_combo.addItem("Aucune ressource disponible", None)
        form.addRow(self._label("Ressource *"), self.resource_combo)

        self.user_combo = QComboBox()
        users = user_controller.get_all_users()
        for u in users:
            if u["is_active"] and u.get("role_name") != "super_admin":
                self.user_combo.addItem(f"{u['full_name']} ({u['email']})", u["id"])
        form.addRow(self._label("Bénéficiaire *"), self.user_combo)

        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate())
        self.start_date.setStyleSheet(f"""
            QDateEdit {{
                background-color: {COLORS['white']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 10px 14px;
                font-size: 14px;
                color: {COLORS['text_primary']};
            }}
        """)
        form.addRow(self._label("Date de début *"), self.start_date)

        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("Notes ou instructions particulières (optionnel)")
        self.notes_input.setMaximumHeight(100)
        self.notes_input.setStyleSheet(f"""
            QTextEdit {{
                background-color: {COLORS['white']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
                color: {COLORS['text_primary']};
            }}
        """)
        form.addRow(self._label("Notes"), self.notes_input)

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

        save_btn = QPushButton("Créer l'affectation")
        save_btn.setStyleSheet(primary_button_style())
        save_btn.clicked.connect(self._on_save)
        btn_layout.addWidget(save_btn)

        layout.addLayout(btn_layout)

    def _label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(f"font-size: 13px; font-weight: 600; color: {COLORS['text_primary']}; background: transparent;")
        return lbl

    def _on_save(self):
        resource_id = self.resource_combo.currentData()
        user_id = self.user_combo.currentData()
        qdate = self.start_date.date()
        start_date = datetime(qdate.year(), qdate.month(), qdate.day())
        notes = self.notes_input.toPlainText().strip() or None

        if not resource_id:
            self.error_label.setText("Aucune ressource disponible.")
            self.error_label.show()
            return

        if not user_id:
            self.error_label.setText("Aucun utilisateur sélectionné.")
            self.error_label.show()
            return

        success, msg, _ = assignment_controller.create_assignment(
            resource_id, user_id, start_date, notes
        )
        if success:
            self.accept()
        else:
            self.error_label.setText(msg)
            self.error_label.show()


class AssignmentsView(QWidget):

    _BADGE = {
        "active":    (COLORS["success_dark"],  COLORS["success_light"],  "Active"),
        "returned":  (COLORS["info"],           COLORS["info_light"],     "Retournée"),
        "cancelled": (COLORS["danger_dark"],    COLORS["danger_light"],   "Annulée"),
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        user = auth_controller.current_user
        self._is_employee = user is not None and user.role.name == "employee"
        self._setup_ui()
        self.load_data()

    def _setup_ui(self):
        from src.views.users_view import _page_header
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        if self._is_employee:
            layout.addWidget(_page_header("📋  Mes affectations",
                                          "Ressources qui vous sont attribuées"))
        else:
            layout.addWidget(_page_header("📋  Gestion des affectations",
                                          "Suivi des ressources attribuées aux collaborateurs"))

        inner = QWidget()
        inner.setStyleSheet(f"background-color: {COLORS['background']};")
        inner_layout = QVBoxLayout(inner)
        inner_layout.setContentsMargins(30, 24, 30, 24)
        inner_layout.setSpacing(0)

        _status_badge_col = {
            "key": "status_label", "label": "Statut", "width": 120,
            "badge": True, "badge_colors": {
                "Active":    (COLORS["success_dark"], COLORS["success_light"]),
                "Retournée": (COLORS["info"],          COLORS["info_light"]),
                "Annulée":   (COLORS["danger_dark"],   COLORS["danger_light"]),
            }
        }

        if self._is_employee:
            columns = [
                {"key": "resource_name",  "label": "🖥️  Ressource"},
                {"key": "assigner_name",  "label": "🔑  Affecté par"},
                {"key": "start_date",     "label": "📅  Début",  "width": 110},
                {"key": "end_date",       "label": "📅  Fin",    "width": 110},
                _status_badge_col,
            ]
            self.table = DataTable(columns, title="Mes affectations",
                                   show_add_button=False, page_size=15)
        else:
            columns = [
                {"key": "resource_name",  "label": "🖥️  Ressource"},
                {"key": "user_name",      "label": "👤  Bénéficiaire"},
                {"key": "user_email",     "label": "✉️  Email"},
                {"key": "assigner_name",  "label": "🔑  Affecté par"},
                {"key": "start_date",     "label": "📅  Début",  "width": 110},
                {"key": "end_date",       "label": "📅  Fin",    "width": 110},
                _status_badge_col,
            ]
            self.table = DataTable(columns, title="Liste des affectations", page_size=15)
            self.table.set_actions([
                {"name": "close",      "icon": "✅", "label": "Clôturer (retour)", "color": COLORS["success"]},
                {"name": "cancel",     "icon": "❌", "label": "Annuler",           "color": COLORS["danger"]},
                {"name": "reactivate", "icon": "🔁", "label": "Réactiver",         "color": COLORS["info"]},
            ])
            self.table.add_clicked.connect(self._on_add)
            self.table.action_triggered.connect(self._on_action)

        self.table.refresh_clicked.connect(self.load_data)

        inner_layout.addWidget(self.table)
        layout.addWidget(inner)

    def load_data(self):
        try:
            user = auth_controller.current_user
            if self._is_employee and user:
                assignments = assignment_controller.get_all_assignments(user_id=user.id)
            else:
                assignments = assignment_controller.get_all_assignments()
            self.table.set_data(assignments)
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible de charger les affectations : {e}")

    def _on_add(self):
        dialog = AssignmentFormDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_data()

    def _on_action(self, action: str, assignment_id: int):
        data = assignment_controller.get_assignment_by_id(assignment_id)
        if not data:
            return

        status = data["status"]
        resource = data["resource_name"]

        if action == "reactivate":
            if status == "active":
                QMessageBox.information(self, "Info", "Cette affectation est déjà active.")
                return
            reply = QMessageBox.question(
                self, "Réactiver l'affectation",
                f"Réactiver l'affectation de '{resource}' ?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                success, msg = assignment_controller.reactivate_assignment(assignment_id)
                if success:
                    QMessageBox.information(self, "Succès", msg)
                    self.load_data()
                else:
                    QMessageBox.warning(self, "Erreur", msg)
            return

        if status != "active":
            QMessageBox.information(self, "Info", "Cette affectation n'est pas active.")
            return

        if action == "close":
            reply = QMessageBox.question(
                self, "Confirmer le retour",
                f"Confirmer le retour de la ressource '{resource}' ?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                success, msg = assignment_controller.close_assignment(assignment_id)
                if success:
                    QMessageBox.information(self, "Succès", msg)
                    self.load_data()
                else:
                    QMessageBox.warning(self, "Erreur", msg)

        elif action == "cancel":
            reply = QMessageBox.question(
                self, "Confirmer l'annulation",
                f"Annuler l'affectation de '{resource}' ?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                success, msg = assignment_controller.cancel_assignment(assignment_id)
                if success:
                    self.load_data()
                else:
                    QMessageBox.warning(self, "Erreur", msg)
