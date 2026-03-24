import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QDialog, QFormLayout,
    QLabel, QPushButton, QComboBox, QMessageBox, QTextEdit,
    QFrame, QScrollArea, QFileDialog
)
from PySide6.QtCore import Qt

from src.views.styles import COLORS, primary_button_style, secondary_button_style
from src.views.widgets.data_table import DataTable
from src.controllers.contract_controller import contract_controller
from src.controllers.assignment_controller import assignment_controller
from src.controllers.auth_controller import auth_controller


class ContractFormDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Générer un contrat")
        self.setMinimumWidth(600)
        self.setMinimumHeight(580)
        self.setStyleSheet(f"background-color: {COLORS['white']};")
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(20)

        title = QLabel("Générer un contrat d'affectation")
        title.setStyleSheet(f"font-size: 18px; font-weight: 700; color: {COLORS['text_primary']};")
        layout.addWidget(title)

        info = QLabel("Remplissez le formulaire ci-dessous. Un PDF signable sera généré automatiquement.")
        info.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 13px;")
        info.setWordWrap(True)
        layout.addWidget(info)

        form = QFormLayout()
        form.setSpacing(14)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

        self.assignment_combo = QComboBox()
        self._load_assignments()
        form.addRow(self._label("Affectation *"), self.assignment_combo)

        self.objet_input = QTextEdit()
        self.objet_input.setPlaceholderText(
            "Ex : Mise à disposition d'un ordinateur portable dans le cadre de l'activité professionnelle de l'employé."
        )
        self.objet_input.setMaximumHeight(90)
        self.objet_input.setStyleSheet(self._textarea_style())
        form.addRow(self._label("Objet du contrat *"), self.objet_input)

        self.conditions_input = QTextEdit()
        self.conditions_input.setPlaceholderText(
            "Ex :\n"
            "- Le bénéficiaire s'engage à utiliser le matériel uniquement dans le cadre professionnel.\n"
            "- Toute dégradation volontaire engage la responsabilité du bénéficiaire.\n"
            "- Le matériel doit être restitué en bon état à la fin de l'affectation."
        )
        self.conditions_input.setMinimumHeight(120)
        self.conditions_input.setStyleSheet(self._textarea_style())
        form.addRow(self._label("Conditions d'utilisation *"), self.conditions_input)

        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("Notes ou clauses particulières (optionnel)")
        self.notes_input.setMaximumHeight(80)
        self.notes_input.setStyleSheet(self._textarea_style())
        form.addRow(self._label("Notes / clauses"), self.notes_input)

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

        generate_btn = QPushButton("Générer le contrat")
        generate_btn.setStyleSheet(primary_button_style())
        generate_btn.clicked.connect(self._on_generate)
        btn_layout.addWidget(generate_btn)

        layout.addLayout(btn_layout)

    def _label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(f"font-size: 13px; font-weight: 600; color: {COLORS['text_primary']}; background: transparent;")
        return lbl

    def _textarea_style(self) -> str:
        return f"""
            QTextEdit {{
                background-color: {COLORS['white']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
                color: {COLORS['text_primary']};
            }}
            QTextEdit:focus {{
                border-color: {COLORS['primary']};
            }}
        """

    def _load_assignments(self):
        self.assignment_combo.clear()
        assignments = assignment_controller.get_all_assignments(status="active")
        for a in assignments:
            label = f"{a['resource_name']} → {a['user_name']} (depuis {a['start_date']})"
            self.assignment_combo.addItem(label, a["id"])
        if not assignments:
            self.assignment_combo.addItem("Aucune affectation active", None)

    def _on_generate(self):
        assignment_id = self.assignment_combo.currentData()
        objet = self.objet_input.toPlainText().strip()
        conditions = self.conditions_input.toPlainText().strip()
        notes = self.notes_input.toPlainText().strip()

        if not assignment_id:
            self.error_label.setText("Aucune affectation active disponible.")
            self.error_label.show()
            return

        if not objet:
            self.error_label.setText("L'objet du contrat est obligatoire.")
            self.error_label.show()
            return

        if not conditions:
            self.error_label.setText("Les conditions d'utilisation sont obligatoires.")
            self.error_label.show()
            return

        success, msg, contract_id = contract_controller.generate_contract(
            assignment_id, objet, conditions, notes
        )

        if not success:
            self.error_label.setText(msg)
            self.error_label.show()
            return

        ok_pdf, pdf_result = contract_controller.export_pdf(contract_id)

        if ok_pdf:
            self._contract_id = contract_id
            reply = QMessageBox.question(
                self, "Contrat généré",
                f"Contrat généré avec succès !\nPDF créé : {pdf_result}\n\nVoulez-vous ouvrir le PDF ?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                try:
                    os.startfile(pdf_result)
                except AttributeError:
                    os.system(f"open '{pdf_result}'")
            self.accept()
        else:
            QMessageBox.warning(self, "Contrat créé sans PDF", f"Contrat enregistré mais PDF non généré : {pdf_result}")
            self.accept()


class SignContractDialog(QDialog):

    def __init__(self, contract_id: int, parent=None):
        super().__init__(parent)
        self._contract_id = contract_id
        self.setWindowTitle("Signer le contrat")
        self.setMinimumWidth(440)
        self.setStyleSheet(f"background-color: {COLORS['white']};")
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(20)

        title = QLabel("Apposer une signature électronique")
        title.setStyleSheet(f"font-size: 18px; font-weight: 700; color: {COLORS['text_primary']};")
        layout.addWidget(title)

        info = QLabel(
            "La signature est électronique et horodatée. Elle génère un hash cryptographique "
            "liant votre identité au contenu du contrat."
        )
        info.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 13px;")
        info.setWordWrap(True)
        layout.addWidget(info)

        form = QFormLayout()
        form.setSpacing(14)

        self.name_input = QTextEdit.__class__.__mro__  # placeholder init
        from PySide6.QtWidgets import QLineEdit
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nom et prénom du signataire")
        form.addRow(QLabel("Nom *"), self.name_input)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("email@entreprise.com")
        form.addRow(QLabel("Email *"), self.email_input)

        user = auth_controller.current_user
        if user:
            self.name_input.setText(user.full_name)
            self.email_input.setText(user.email)

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

        sign_btn = QPushButton("Signer")
        sign_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['success']};
                color: white; border: none; border-radius: 8px;
                padding: 12px 24px; font-size: 14px; font-weight: 600;
            }}
            QPushButton:hover {{ background-color: #059669; }}
        """)
        sign_btn.clicked.connect(self._on_sign)
        btn_layout.addWidget(sign_btn)

        layout.addLayout(btn_layout)

    def _on_sign(self):
        name = self.name_input.text().strip()
        email = self.email_input.text().strip()

        if not name or not email:
            self.error_label.setText("Nom et email obligatoires.")
            self.error_label.show()
            return

        success, msg = contract_controller.sign_contract(self._contract_id, name, email)
        if success:
            self.accept()
        else:
            self.error_label.setText(msg)
            self.error_label.show()


class ContractsView(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self.load_data()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        title = QLabel("Contrats")
        title.setStyleSheet(f"font-size: 24px; font-weight: 700; color: {COLORS['text_primary']}; background: transparent;")
        layout.addWidget(title)

        columns = [
            {"key": "id", "label": "Réf.", "width": 80,
             "formatter": lambda v, r: f"CONTRAT-{v:04d}"},
            {"key": "assignment_id", "label": "Affectation", "width": 120,
             "formatter": lambda v, r: f"AFF-{v:04d}"},
            {"key": "generated_at", "label": "Généré le", "width": 150},
            {"key": "signed_at", "label": "Signé le", "width": 150,
             "formatter": lambda v, r: v if v else "Non signé"},
            {"key": "status", "label": "Statut", "width": 130,
             "style": lambda v, r: {"color": r.get("status_color", COLORS["secondary"])}},
            {"key": "has_pdf", "label": "PDF", "width": 80,
             "formatter": lambda v, r: "✅" if v else "❌"},
        ]

        self.table = DataTable(columns, title="Liste des contrats", page_size=15)
        self.table.set_actions([
            {"name": "sign", "icon": "✍️", "label": "Signer", "color": COLORS["success"]},
            {"name": "export", "icon": "📄", "label": "Exporter PDF", "color": COLORS["primary"]},
            {"name": "verify", "icon": "🔍", "label": "Vérifier intégrité", "color": COLORS["info"]},
        ])

        self.table.add_button.setText("+ Générer un contrat")
        self.table.add_clicked.connect(self._on_add)
        self.table.refresh_clicked.connect(self.load_data)
        self.table.action_triggered.connect(self._on_action)

        layout.addWidget(self.table)

    def load_data(self):
        try:
            contracts = contract_controller.get_all_contracts()
            self.table.set_data(contracts)
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible de charger les contrats : {e}")

    def _on_add(self):
        dialog = ContractFormDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_data()

    def _on_action(self, action: str, contract_id: int):
        if action == "sign":
            contracts = contract_controller.get_all_contracts()
            contract = next((c for c in contracts if c["id"] == contract_id), None)
            if contract and contract["is_signed"]:
                QMessageBox.information(self, "Déjà signé", "Ce contrat est déjà signé.")
                return
            dialog = SignContractDialog(contract_id, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                QMessageBox.information(self, "Succès", "Contrat signé avec succès.")
                self.load_data()

        elif action == "export":
            output_path, _ = QFileDialog.getSaveFileName(
                self, "Enregistrer le PDF",
                f"contrat_{contract_id:04d}.pdf",
                "PDF (*.pdf)"
            )
            if output_path:
                success, result = contract_controller.export_pdf(contract_id, output_path)
                if success:
                    reply = QMessageBox.question(
                        self, "PDF créé", f"PDF enregistré.\n{result}\n\nOuvrir ?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                    )
                    if reply == QMessageBox.StandardButton.Yes:
                        try:
                            os.startfile(result)
                        except AttributeError:
                            os.system(f"open '{result}'")
                else:
                    QMessageBox.warning(self, "Erreur", result)

        elif action == "verify":
            success, msg = contract_controller.verify_contract(contract_id)
            if success:
                QMessageBox.information(self, "Intégrité OK", msg)
            else:
                QMessageBox.critical(self, "Intégrité compromise", msg)
