from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QDialog, QFormLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QMessageBox, QTextEdit, QFrame
)
from PySide6.QtCore import Qt

from src.views.styles import COLORS, primary_button_style, secondary_button_style
from src.views.widgets.data_table import DataTable
from src.controllers.resource_controller import resource_controller
from src.controllers.company_controller import company_controller
from src.controllers.auth_controller import auth_controller
import config


class ResourceFormDialog(QDialog):

    def __init__(self, parent=None, resource_data: dict = None):
        super().__init__(parent)
        self._resource_data = resource_data
        self._companies = company_controller.get_all_companies()
        self.setWindowTitle("Modifier la ressource" if resource_data else "Nouvelle ressource")
        self.setMinimumWidth(500)
        self.setStyleSheet(f"background-color: {COLORS['white']};")
        self._setup_ui()
        if resource_data:
            self._populate(resource_data)

    def _setup_ui(self):
        is_edit = self._resource_data is not None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(20)

        title = QLabel("Modifier la ressource" if is_edit else "Ajouter une ressource")
        title.setStyleSheet(f"font-size: 18px; font-weight: 700; color: {COLORS['text_primary']};")
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(14)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

        self.company_combo = QComboBox()
        for c in self._companies:
            self.company_combo.addItem(c["name"], c["id"])
        self.company_combo.currentIndexChanged.connect(self._on_company_changed)
        form.addRow(self._label("Entreprise *"), self.company_combo)

        self.type_combo = QComboBox()
        form.addRow(self._label("Type *"), self.type_combo)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Ex : MacBook Pro 14 pouces")
        form.addRow(self._label("Nom *"), self.name_input)

        self.serial_input = QLineEdit()
        self.serial_input.setPlaceholderText("Numéro de série (optionnel)")
        form.addRow(self._label("N° de série"), self.serial_input)

        if is_edit:
            self.status_combo = QComboBox()
            for key, label in config.RESOURCE_STATUS.items():
                self.status_combo.addItem(label, key)
            form.addRow(self._label("Statut"), self.status_combo)

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

        save_btn = QPushButton("Enregistrer")
        save_btn.setStyleSheet(primary_button_style())
        save_btn.clicked.connect(self._on_save)
        btn_layout.addWidget(save_btn)

        layout.addLayout(btn_layout)

        if self.company_combo.count() > 0:
            self._load_types(self.company_combo.currentData())

    def _label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(f"font-size: 13px; font-weight: 600; color: {COLORS['text_primary']}; background: transparent;")
        return lbl

    def _on_company_changed(self):
        company_id = self.company_combo.currentData()
        if company_id:
            self._load_types(company_id)

    def _load_types(self, company_id: int):
        self.type_combo.clear()
        types = resource_controller.get_all_resource_types(company_id)
        for rt in types:
            self.type_combo.addItem(rt["name"], rt["id"])
        if not types:
            self.type_combo.addItem("Aucun type disponible", None)

    def _populate(self, data: dict):
        for i in range(self.company_combo.count()):
            if self.company_combo.itemData(i) == data.get("company_id"):
                self.company_combo.setCurrentIndex(i)
                break

        self._load_types(data.get("company_id"))

        for i in range(self.type_combo.count()):
            if self.type_combo.itemData(i) == data.get("resource_type_id"):
                self.type_combo.setCurrentIndex(i)
                break

        self.name_input.setText(data.get("name", ""))
        self.serial_input.setText(data.get("serial_number", ""))

        if hasattr(self, "status_combo"):
            for i in range(self.status_combo.count()):
                if self.status_combo.itemData(i) == data.get("status"):
                    self.status_combo.setCurrentIndex(i)
                    break

    def _on_save(self):
        is_edit = self._resource_data is not None
        company_id = self.company_combo.currentData()
        resource_type_id = self.type_combo.currentData()
        name = self.name_input.text().strip()
        serial = self.serial_input.text().strip() or None

        if not resource_type_id:
            self.error_label.setText("Veuillez d'abord créer un type de ressource pour cette entreprise.")
            self.error_label.show()
            return

        if is_edit:
            status = self.status_combo.currentData() if hasattr(self, "status_combo") else None
            success, msg = resource_controller.update_resource(
                self._resource_data["id"],
                name=name, status=status, serial_number=serial
            )
        else:
            success, msg, _ = resource_controller.create_resource(
                company_id, resource_type_id, name, serial
            )

        if success:
            self.accept()
        else:
            self.error_label.setText(msg)
            self.error_label.show()


class _StatusMiniCard(QFrame):
    def __init__(self, label: str, value: str, text_color: str, bg_color: str, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border-radius: 10px;
                border: 1.5px solid {text_color}30;
            }}
        """)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(14, 10, 14, 10)
        lay.setSpacing(10)
        self._val = QLabel(value)
        self._val.setStyleSheet(f"font-size: 22px; font-weight: 800; color: {text_color}; background: transparent;")
        lay.addWidget(self._val)
        lbl = QLabel(label)
        lbl.setStyleSheet(f"font-size: 12px; font-weight: 600; color: {text_color}; background: transparent;")
        lay.addWidget(lbl)
        lay.addStretch()

    def set_value(self, v: str):
        self._val.setText(v)


class ResourcesView(QWidget):

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
            layout.addWidget(_page_header("🖥️  Mes ressources",
                                          "Équipements qui vous sont affectés"))
        else:
            layout.addWidget(_page_header("🖥️  Gestion des ressources",
                                          "Matériel, logiciels et équipements de l'entreprise"))

        inner = QWidget()
        inner.setStyleSheet(f"background-color: {COLORS['background']};")
        inner_layout = QVBoxLayout(inner)
        inner_layout.setContentsMargins(30, 20, 30, 24)
        inner_layout.setSpacing(16)

        # Mini-cards (masquées pour les employés sauf "Affectées")
        cards_row = QHBoxLayout()
        cards_row.setSpacing(12)
        self._card_available  = _StatusMiniCard("Disponibles",  "0", COLORS["success_dark"],  COLORS["success_light"])
        self._card_assigned   = _StatusMiniCard("Affectées",    "0", COLORS["info"],           COLORS["info_light"])
        self._card_maintenance= _StatusMiniCard("Maintenance",  "0", COLORS["warning_dark"],   COLORS["warning_light"])
        self._card_retired    = _StatusMiniCard("Retirées",     "0", COLORS["text_muted"],      COLORS["border_light"])
        if self._is_employee:
            cards_row.addWidget(self._card_assigned)
        else:
            for c in [self._card_available, self._card_assigned, self._card_maintenance, self._card_retired]:
                cards_row.addWidget(c)
        cards_row.addStretch()
        inner_layout.addLayout(cards_row)

        # Colonnes
        columns = [
            {"key": "name",              "label": "🖥️  Nom"},
            {"key": "resource_type_name","label": "📂  Type"},
            {"key": "serial_number",     "label": "🔢  N° de série"},
            {"key": "company_name",      "label": "🏢  Entreprise"},
            {"key": "status_label", "label": "Statut", "width": 130,
             "badge": True, "badge_colors": {
                 "Disponible":  (COLORS["success_dark"],  COLORS["success_light"]),
                 "Affectée":    (COLORS["info"],           COLORS["info_light"]),
                 "Maintenance": (COLORS["warning_dark"],   COLORS["warning_light"]),
                 "Retirée":     (COLORS["text_muted"],     COLORS["border_light"]),
             }},
            {"key": "created_at",        "label": "📅  Ajouté le", "width": 120},
        ]

        if self._is_employee:
            self.table = DataTable(columns, title="Mes ressources affectées",
                                   show_add_button=False, page_size=15)
        else:
            self.table = DataTable(columns, title="Parc de ressources", page_size=15)


            self.table.set_actions([
                {"name": "edit",   "icon": "✏️",  "label": "Modifier", "color": COLORS["primary"]},
                {"name": "retire", "icon": "🗑️", "label": "Retirer",  "color": COLORS["danger"]},
            ])
            self.table.add_clicked.connect(self._on_add)
            self.table.action_triggered.connect(self._on_action)

        self.table.refresh_clicked.connect(self.load_data)
        inner_layout.addWidget(self.table)
        layout.addWidget(inner)

    # Badge colors per status
    _BADGE = {
        "available":   (COLORS["success_dark"],  COLORS["success_light"],  "Disponible"),
        "assigned":    (COLORS["info"],           COLORS["info_light"],     "Affectée"),
        "maintenance": (COLORS["warning_dark"],   COLORS["warning_light"],  "Maintenance"),
        "retired":     (COLORS["text_muted"],      COLORS["border_light"],   "Retirée"),
    }

    def load_data(self):
        try:
            user = auth_controller.current_user
            if self._is_employee and user:
                resources = resource_controller.get_resources_by_user(user.id)
            else:
                resources = resource_controller.get_all_resources()
            self.table.set_data(resources)

            # Update mini-cards
            counts = {"available": 0, "assigned": 0, "maintenance": 0, "retired": 0}
            for r in resources:
                s = r.get("status", "")
                if s in counts:
                    counts[s] += 1
            self._card_assigned.set_value(str(counts["assigned"]))
            if not self._is_employee:
                self._card_available.set_value(str(counts["available"]))
                self._card_maintenance.set_value(str(counts["maintenance"]))
                self._card_retired.set_value(str(counts["retired"]))

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible de charger les ressources : {e}")

    def _on_add(self):
        dialog = ResourceFormDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_data()

    def _on_action(self, action: str, resource_id: int):
        if action == "edit":
            data = resource_controller.get_resource_by_id(resource_id)
            if data:
                dialog = ResourceFormDialog(self, data)
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    self.load_data()

        elif action == "retire":
            reply = QMessageBox.question(
                self, "Confirmation",
                "Retirer cette ressource du parc ? Elle passera au statut 'Retirée'.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                success, msg = resource_controller.delete_resource(resource_id)
                if success:
                    self.load_data()
                else:
                    QMessageBox.warning(self, "Impossible", msg)
