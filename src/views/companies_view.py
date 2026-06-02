from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QDialog, QFormLayout,
    QLabel, QLineEdit, QPushButton, QMessageBox, QFrame
)
from PySide6.QtCore import Qt

from src.views.styles import COLORS, primary_button_style, secondary_button_style
from src.views.widgets.data_table import DataTable
from src.controllers.company_controller import company_controller
from src.controllers.auth_controller import auth_controller


class CompanyFormDialog(QDialog):

    def __init__(self, parent=None, company_data: dict = None):
        super().__init__(parent)
        self._company_data = company_data
        self.setWindowTitle("Modifier l'entreprise" if company_data else "Nouvelle entreprise")
        self.setMinimumWidth(460)
        self.setStyleSheet(f"background-color: {COLORS['white']};")
        self._setup_ui()
        if company_data:
            self._populate(company_data)

    def _setup_ui(self):
        is_edit = self._company_data is not None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(20)

        title = QLabel("Modifier l'entreprise" if is_edit else "Créer une entreprise")
        title.setStyleSheet(f"font-size: 18px; font-weight: 700; color: {COLORS['text_primary']};")
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(14)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nom de l'entreprise")
        form.addRow(self._label("Nom *"), self.name_input)

        self.siret_input = QLineEdit()
        self.siret_input.setPlaceholderText("14 chiffres (optionnel)")
        self.siret_input.setMaxLength(17)
        form.addRow(self._label("SIRET"), self.siret_input)

        self.address_input = QLineEdit()
        self.address_input.setPlaceholderText("Adresse complète")
        form.addRow(self._label("Adresse"), self.address_input)

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

    def _label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(f"font-size: 13px; font-weight: 600; color: {COLORS['text_primary']}; background: transparent;")
        return lbl

    def _populate(self, data: dict):
        self.name_input.setText(data.get("name", ""))
        self.siret_input.setText(data.get("siret", ""))
        self.address_input.setText(data.get("address", ""))

    def _on_save(self):
        is_edit = self._company_data is not None
        name = self.name_input.text().strip()
        siret = self.siret_input.text().strip() or None
        address = self.address_input.text().strip() or None

        if is_edit:
            success, msg = company_controller.update_company(
                self._company_data["id"], name=name, siret=siret, address=address
            )
        else:
            success, msg, _ = company_controller.create_company(name, siret, address)

        if success:
            self.accept()
        else:
            self.error_label.setText(msg)
            self.error_label.show()


class CompaniesView(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self.load_data()

    def _setup_ui(self):
        from src.views.users_view import _page_header
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(_page_header("🏢  Gestion des entreprises",
                                      "Espaces clients, organisations et espaces cloisonnés"))

        inner = QWidget()
        inner.setStyleSheet(f"background-color: {COLORS['background']};")
        inner_layout = QVBoxLayout(inner)
        inner_layout.setContentsMargins(30, 24, 30, 24)
        inner_layout.setSpacing(0)

        columns = [
            {"key": "name",           "label": "🏢  Nom"},
            {"key": "siret_formatted","label": "🔢  SIRET"},
            {"key": "address",        "label": "📍  Adresse"},
            {"key": "users_count",    "label": "👥  Utilisateurs", "width": 130},
            {"key": "resources_count","label": "🖥️  Ressources",   "width": 120},
            {"key": "status",         "label": "Statut",            "width": 110},
        ]

        self.table = DataTable(columns, title="Liste des entreprises", page_size=15)

        # Filter: active/inactive
        self.table.add_filter("Affichage", [
            ("Actives uniquement", "Active"),
            ("Toutes (inc. inactives)", None),
        ], "status")

        self.table.set_actions([
            {"name": "edit",   "icon": "✏️",  "label": "Modifier",            "color": COLORS["primary"]},
            {"name": "stats",  "icon": "📊",  "label": "Statistiques",         "color": COLORS["info"]},
            {"name": "toggle", "icon": "🔄",  "label": "Activer/Désactiver",   "color": COLORS["secondary"]},
        ])

        is_super = auth_controller.is_super_admin()
        self.table.add_button.setVisible(is_super)

        self.table.add_clicked.connect(self._on_add)
        self.table.refresh_clicked.connect(self.load_data)
        self.table.action_triggered.connect(self._on_action)

        inner_layout.addWidget(self.table)
        layout.addWidget(inner)

    def load_data(self):
        try:
            companies = company_controller.get_all_companies(include_inactive=True)
            self.table.set_data(companies)
            # Status badges — col 5
            for row_idx in range(self.table.table.rowCount()):
                start = (self.table._current_page - 1) * self.table._page_size
                idx = start + row_idx
                if idx < len(self.table._filtered_data):
                    is_active = self.table._filtered_data[idx].get("is_active", True)
                    if is_active:
                        self.table.set_status_badge(row_idx, 5, "Active",
                                                    COLORS["success_dark"], COLORS["success_light"])
                    else:
                        self.table.set_status_badge(row_idx, 5, "Inactive",
                                                    COLORS["danger_dark"], COLORS["danger_light"])
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible de charger les entreprises : {e}")

    def _on_add(self):
        dialog = CompanyFormDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_data()

    def _on_action(self, action: str, company_id: int):
        if action == "edit":
            data = company_controller.get_company_by_id(company_id)
            if data:
                dialog = CompanyFormDialog(self, data)
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    self.load_data()

        elif action == "stats":
            stats = company_controller.get_company_stats(company_id)
            data = company_controller.get_company_by_id(company_id)
            name = data["name"] if data else "Entreprise"
            QMessageBox.information(
                self, f"Statistiques — {name}",
                f"Utilisateurs actifs : {stats['users_count']}\n"
                f"Ressources totales : {stats['resources_count']}\n"
                f"Ressources disponibles : {stats['available_resources']}"
            )

        elif action == "toggle":
            data = company_controller.get_company_by_id(company_id)
            if data:
                action_label = "désactiver" if data["is_active"] else "réactiver"
                reply = QMessageBox.question(
                    self, "Confirmation",
                    f"Voulez-vous {action_label} cette entreprise ?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.Yes:
                    if data["is_active"]:
                        success, msg = company_controller.delete_company(company_id)
                    else:
                        success, msg = company_controller.update_company(company_id, is_active=True)
                    if success:
                        self.load_data()
                    else:
                        QMessageBox.warning(self, "Impossible", msg)
