from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

from sqlalchemy.orm import joinedload

from src.models.base import get_session
from src.models.contract import Contract
from src.models.assignment import Assignment
from src.models.audit_log import AuditLog
from src.controllers.auth_controller import auth_controller
import config


class ContractController:

    def get_all_contracts(self, company_id: Optional[int] = None) -> List[Dict[str, Any]]:
        with get_session() as session:
            query = session.query(Contract).options(
                joinedload(Contract.assignment)
            )
            if company_id:
                query = query.join(Assignment).join(
                    Assignment.resource
                ).filter_by(company_id=company_id)

            contracts = query.order_by(Contract.generated_at.desc()).all()
            return [self._format_contract(c) for c in contracts]

    def get_contracts_by_assignment(self, assignment_id: int) -> List[Dict[str, Any]]:
        with get_session() as session:
            contracts = session.query(Contract).filter_by(
                assignment_id=assignment_id
            ).order_by(Contract.generated_at.desc()).all()
            return [self._format_contract(c) for c in contracts]

    def generate_contract(self, assignment_id: int, objet: str,
                          conditions: str, notes: str = "") -> Tuple[bool, str, Optional[int]]:
        if not objet.strip():
            return False, "L'objet du contrat est requis", None
        if not conditions.strip():
            return False, "Les conditions d'utilisation sont requises", None

        with get_session() as session:
            a = session.query(Assignment).options(
                joinedload(Assignment.resource),
                joinedload(Assignment.user),
                joinedload(Assignment.assigner)
            ).filter_by(id=assignment_id).first()

            if not a:
                return False, "Affectation introuvable", None

            content = self._build_contract_content(a, objet, conditions, notes)
            content_hash = Contract.compute_hash(content)

            contract = Contract(
                assignment_id=assignment_id,
                content=content,
                content_hash=content_hash
            )
            session.add(contract)

            log = AuditLog.log(
                action="CREATE",
                user_id=auth_controller.current_user.id if auth_controller.current_user else None,
                table_name="contracts",
                new_values={"assignment_id": assignment_id, "objet": objet}
            )
            session.add(log)
            session.commit()

            return True, "Contrat généré avec succès", contract.id

    def sign_contract(self, contract_id: int, signer_name: str,
                      signer_email: str) -> Tuple[bool, str]:
        with get_session() as session:
            contract = session.query(Contract).filter_by(id=contract_id).first()
            if not contract:
                return False, "Contrat introuvable"
            if contract.is_signed:
                return False, "Contrat déjà signé"
            if not contract.verify_integrity():
                return False, "Intégrité du contrat compromise — signature impossible"

            signer_data = f"{signer_name}|{signer_email}"
            contract.sign(signer_data)

            log = AuditLog.log(
                action="UPDATE",
                user_id=auth_controller.current_user.id if auth_controller.current_user else None,
                table_name="contracts", record_id=contract_id,
                new_values={"signed_by": signer_email, "action": "signature"}
            )
            session.add(log)
            session.commit()
            return True, "Contrat signé avec succès"

    def verify_contract(self, contract_id: int) -> Tuple[bool, str]:
        with get_session() as session:
            contract = session.query(Contract).filter_by(id=contract_id).first()
            if not contract:
                return False, "Contrat introuvable"
            if contract.verify_integrity():
                return True, "Intégrité vérifiée — contrat non modifié"
            return False, "ALERTE : le contrat a été modifié depuis sa génération"

    def export_pdf(self, contract_id: int,
                   output_path: Optional[str] = None) -> Tuple[bool, str]:
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import cm
            from reportlab.lib import colors
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
            from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
        except ImportError:
            return False, "reportlab non installé — pip install reportlab"

        with get_session() as session:
            contract = session.query(Contract).options(
                joinedload(Contract.assignment)
            ).filter_by(id=contract_id).first()

            if not contract:
                return False, "Contrat introuvable"

            a = session.query(Assignment).options(
                joinedload(Assignment.resource),
                joinedload(Assignment.user)
            ).filter_by(id=contract.assignment_id).first()

            if not a:
                return False, "Affectation associée introuvable"

            pdf_dir = config.BASE_DIR / "contracts"
            pdf_dir.mkdir(exist_ok=True)

            if output_path:
                pdf_path = Path(output_path)
            else:
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                pdf_path = pdf_dir / f"contrat_{contract_id}_{ts}.pdf"

            doc = SimpleDocTemplate(
                str(pdf_path),
                pagesize=A4,
                rightMargin=2*cm, leftMargin=2*cm,
                topMargin=2*cm, bottomMargin=2*cm
            )

            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                "title", parent=styles["Heading1"],
                fontSize=20, textColor=colors.HexColor("#1e293b"),
                spaceAfter=6, alignment=TA_CENTER
            )
            subtitle_style = ParagraphStyle(
                "subtitle", parent=styles["Normal"],
                fontSize=11, textColor=colors.HexColor("#64748b"),
                spaceAfter=20, alignment=TA_CENTER
            )
            section_style = ParagraphStyle(
                "section", parent=styles["Heading2"],
                fontSize=13, textColor=colors.HexColor("#2563eb"),
                spaceBefore=16, spaceAfter=8
            )
            body_style = ParagraphStyle(
                "body", parent=styles["Normal"],
                fontSize=11, textColor=colors.HexColor("#1e293b"),
                spaceAfter=8, leading=16
            )
            label_style = ParagraphStyle(
                "label", parent=styles["Normal"],
                fontSize=10, textColor=colors.HexColor("#64748b"),
                spaceAfter=4
            )
            value_style = ParagraphStyle(
                "value", parent=styles["Normal"],
                fontSize=11, textColor=colors.HexColor("#1e293b"),
                spaceAfter=10, fontName="Helvetica-Bold"
            )
            footer_style = ParagraphStyle(
                "footer", parent=styles["Normal"],
                fontSize=9, textColor=colors.HexColor("#94a3b8"),
                alignment=TA_CENTER
            )

            story = []

            story.append(Spacer(1, 0.5*cm))
            story.append(Paragraph("GestRes Pro", title_style))
            story.append(Paragraph("Contrat d'affectation de ressource", subtitle_style))
            story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#2563eb")))
            story.append(Spacer(1, 0.5*cm))

            ref = f"Réf. CONTRAT-{contract_id:04d} — généré le {contract.generated_at.strftime('%d/%m/%Y à %H:%M')}"
            story.append(Paragraph(ref, label_style))
            story.append(Spacer(1, 0.3*cm))

            story.append(Paragraph("Parties concernées", section_style))
            parties_data = [
                ["Bénéficiaire :", a.user.full_name if a.user else "—"],
                ["Email :", a.user.email if a.user else "—"],
                ["Affectée par :", a.assigner.full_name if a.assigner else "—"],
            ]
            for label, value in parties_data:
                story.append(Paragraph(label, label_style))
                story.append(Paragraph(value, value_style))

            story.append(Paragraph("Ressource concernée", section_style))
            resource_data = [
                ["Nom :", a.resource.name if a.resource else "—"],
                ["N° de série :", a.resource.serial_number or "Non renseigné" if a.resource else "—"],
                ["Type :", a.resource.resource_type.name if (a.resource and a.resource.resource_type) else "—"],
                ["Date de début :", a.start_date.strftime("%d/%m/%Y") if a.start_date else "—"],
                ["Date de fin prévue :", a.end_date.strftime("%d/%m/%Y") if a.end_date else "Non définie"],
            ]
            for label, value in resource_data:
                story.append(Paragraph(label, label_style))
                story.append(Paragraph(value, value_style))

            lines = contract.content.split("\n")
            current_section = None
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                if line.startswith("OBJET :"):
                    story.append(Paragraph("Objet du contrat", section_style))
                    current_section = "objet"
                elif line.startswith("CONDITIONS :"):
                    story.append(Paragraph("Conditions d'utilisation", section_style))
                    current_section = "conditions"
                elif line.startswith("NOTES :"):
                    story.append(Paragraph("Notes et clauses particulières", section_style))
                    current_section = "notes"
                elif line.startswith("---"):
                    current_section = None
                elif current_section:
                    story.append(Paragraph(line, body_style))

            story.append(Spacer(1, 1*cm))
            story.append(Paragraph("Signatures", section_style))
            story.append(Spacer(1, 0.3*cm))

            sig_table_data = [
                [
                    Paragraph("Le bénéficiaire", label_style),
                    Paragraph("Le responsable", label_style)
                ],
                [Spacer(1, 2*cm), Spacer(1, 2*cm)],
                [
                    Paragraph(f"Nom : {a.user.full_name if a.user else '_______________'}", body_style),
                    Paragraph(f"Nom : {a.assigner.full_name if a.assigner else '_______________'}", body_style)
                ],
                [
                    Paragraph("Signature : _______________", body_style),
                    Paragraph("Signature : _______________", body_style)
                ],
            ]

            if contract.is_signed and contract.signed_at:
                sig_info = Paragraph(
                    f"Signé électroniquement le {contract.signed_at.strftime('%d/%m/%Y à %H:%M')}",
                    ParagraphStyle("signed", parent=body_style,
                                   textColor=colors.HexColor("#10b981"), fontName="Helvetica-Bold")
                )
                story.append(sig_info)
                story.append(Spacer(1, 0.3*cm))

            sig_table = Table(sig_table_data, colWidths=[8*cm, 8*cm])
            sig_table.setStyle(TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ]))
            story.append(sig_table)

            story.append(Spacer(1, 1*cm))
            story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e2e8f0")))
            story.append(Spacer(1, 0.3*cm))
            story.append(Paragraph(
                f"Document généré par GestRes Pro — Hash d'intégrité SHA-256 : {contract.content_hash[:16]}...",
                footer_style
            ))

            doc.build(story)

            contract.pdf_path = str(pdf_path)
            session.commit()

            return True, str(pdf_path)

    def _build_contract_content(self, assignment, objet: str,
                                conditions: str, notes: str) -> str:
        resource_name = assignment.resource.name if assignment.resource else "N/A"
        serial = assignment.resource.serial_number if (assignment.resource and assignment.resource.serial_number) else "N/A"
        user_name = assignment.user.full_name if assignment.user else "N/A"
        user_email = assignment.user.email if assignment.user else "N/A"
        start_date = assignment.start_date.strftime("%d/%m/%Y") if assignment.start_date else "N/A"
        assigner = assignment.assigner.full_name if assignment.assigner else "N/A"
        generated = datetime.now(timezone.utc).strftime("%d/%m/%Y à %H:%M UTC")

        return f"""CONTRAT D'AFFECTATION DE RESSOURCE
Référence : CONTRAT-{assignment.id:04d}
Généré le : {generated}

---
PARTIES :
Bénéficiaire : {user_name} ({user_email})
Responsable : {assigner}

---
RESSOURCE :
Nom : {resource_name}
Numéro de série : {serial}
Date de début : {start_date}

---
OBJET :
{objet.strip()}

---
CONDITIONS :
{conditions.strip()}

---
NOTES :
{notes.strip() if notes.strip() else "Aucune note particulière."}
"""

    def _format_contract(self, contract: Contract) -> Dict[str, Any]:
        return {
            "id": contract.id,
            "assignment_id": contract.assignment_id,
            "is_signed": contract.is_signed,
            "status": "Signé" if contract.is_signed else "Non signé",
            "status_color": "#10b981" if contract.is_signed else "#f59e0b",
            "generated_at": contract.generated_at.strftime("%d/%m/%Y %H:%M") if contract.generated_at else "",
            "signed_at": contract.signed_at.strftime("%d/%m/%Y %H:%M") if contract.signed_at else "",
            "has_pdf": bool(contract.pdf_path),
            "pdf_path": contract.pdf_path or "",
            "content_hash": contract.content_hash
        }


contract_controller = ContractController()
