from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy.orm import joinedload

from src.models.base import get_session
from src.models.contract import Contract
from src.models.assignment import Assignment
from src.models.audit_log import AuditLog
from src.controllers.auth_controller import auth_controller
import config


class ContractController:

    def get_all_contracts(self, company_id=None):
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

    def get_contracts_by_user(self, user_id):
        with get_session() as session:
            contracts = session.query(Contract).options(
                joinedload(Contract.assignment)
            ).join(Assignment).filter(
                Assignment.user_id == user_id
            ).order_by(Contract.generated_at.desc()).all()
            return [self._format_contract(c) for c in contracts]

    def get_contracts_by_assignment(self, assignment_id):
        with get_session() as session:
            contracts = session.query(Contract).filter_by(
                assignment_id=assignment_id
            ).order_by(Contract.generated_at.desc()).all()
            return [self._format_contract(c) for c in contracts]

    def generate_contract(self, assignment_id, objet, conditions, notes=""):
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

    def sign_contract(self, contract_id, signer_name, signer_email):
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

    def verify_contract(self, contract_id):
        with get_session() as session:
            contract = session.query(Contract).filter_by(id=contract_id).first()
            if not contract:
                return False, "Contrat introuvable"
            if contract.verify_integrity():
                return True, "Intégrité vérifiée — contrat non modifié"
            return False, "ALERTE : le contrat a été modifié depuis sa génération"

    def export_pdf(self, contract_id, output_path=None):
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import cm
            from reportlab.lib import colors
            from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                            HRFlowable, Table, TableStyle, KeepTogether)
            from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
            from reportlab.platypus.flowables import Flowable
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
                joinedload(Assignment.user),
                joinedload(Assignment.assigner),
                joinedload(Assignment.resource).joinedload(Assignment.resource.property.mapper.class_.resource_type)
            ).filter_by(id=contract.assignment_id).first()

            if not a:
                return False, "Affectation associée introuvable"

            # Extraire les données
            user_name    = a.user.full_name if a.user else "—"
            user_email   = a.user.email if a.user else "—"
            assigner     = a.assigner.full_name if a.assigner else "—"
            res_name     = a.resource.name if a.resource else "—"
            res_serial   = (a.resource.serial_number or "Non renseigné") if a.resource else "—"
            res_type     = (a.resource.resource_type.name
                            if a.resource and a.resource.resource_type else "—")
            date_debut   = a.start_date.strftime("%d/%m/%Y") if a.start_date else "—"
            date_fin     = a.end_date.strftime("%d/%m/%Y") if a.end_date else "Non définie"
            gen_date     = contract.generated_at.strftime("%d/%m/%Y à %H:%M") if contract.generated_at else "—"

            # Extraire objet / conditions / notes du contenu texte
            objet = conditions = notes_txt = ""
            current = None
            for line in contract.content.split("\n"):
                line = line.strip()
                if line.startswith("OBJET :"):        current = "o"; continue
                if line.startswith("CONDITIONS :"):   current = "c"; continue
                if line.startswith("NOTES :"):        current = "n"; continue
                if line.startswith("---") or not line: continue
                if current == "o": objet      += line + " "
                if current == "c": conditions += line + " "
                if current == "n": notes_txt  += line + " "

            pdf_dir = config.BASE_DIR / "contracts"
            pdf_dir.mkdir(exist_ok=True)

            if output_path:
                pdf_path = Path(output_path)
            else:
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                pdf_path = pdf_dir / f"contrat_{contract_id:04d}_{ts}.pdf"

            # ── Couleurs ──────────────────────────────────────────────
            NAVY    = colors.HexColor("#1e3a5f")
            BLUE    = colors.HexColor("#2563eb")
            LIGHT   = colors.HexColor("#eff6ff")
            GRAY_BG = colors.HexColor("#f8fafc")
            GRAY    = colors.HexColor("#64748b")
            DARK    = colors.HexColor("#0f172a")
            WHITE   = colors.white
            GREEN   = colors.HexColor("#10b981")
            BORDER  = colors.HexColor("#dbeafe")

            W = A4[0] - 4*cm  # largeur utile

            # ── Styles ────────────────────────────────────────────────
            def _style(name, **kw):
                base = getSampleStyleSheet()["Normal"]
                return ParagraphStyle(name, parent=base, **kw)

            s_ref      = _style("ref",      fontSize=9,  textColor=GRAY,  alignment=TA_RIGHT)
            s_section  = _style("sec",      fontSize=11, textColor=BLUE,  fontName="Helvetica-Bold",
                                spaceBefore=14, spaceAfter=6)
            s_label    = _style("lbl",      fontSize=9,  textColor=GRAY)
            s_value    = _style("val",      fontSize=11, textColor=DARK,  fontName="Helvetica-Bold", spaceAfter=2)
            s_body     = _style("body",     fontSize=10, textColor=DARK,  leading=15, spaceAfter=6)
            s_footer   = _style("footer",   fontSize=8,  textColor=GRAY,  alignment=TA_CENTER)
            s_signed   = _style("signed",   fontSize=10, textColor=GREEN, fontName="Helvetica-Bold",
                                alignment=TA_CENTER)
            s_sig_lbl  = _style("siglbl",   fontSize=9,  textColor=GRAY,  alignment=TA_CENTER)
            s_sig_name = _style("signame",  fontSize=10, textColor=DARK,  fontName="Helvetica-Bold",
                                alignment=TA_CENTER)

            # ── Helper : bloc info avec fond gris ─────────────────────
            def info_table(rows):
                data = [[Paragraph(lbl, s_label), Paragraph(val, s_value)] for lbl, val in rows]
                t = Table(data, colWidths=[4*cm, W - 4*cm])
                t.setStyle(TableStyle([
                    ("BACKGROUND",   (0,0), (-1,-1), GRAY_BG),
                    ("ROWBACKGROUNDS",(0,0),(-1,-1), [GRAY_BG, WHITE]),
                    ("BOX",          (0,0), (-1,-1), 0.5, BORDER),
                    ("LINEBELOW",    (0,0), (-1,-2), 0.3, BORDER),
                    ("TOPPADDING",   (0,0), (-1,-1), 6),
                    ("BOTTOMPADDING",(0,0), (-1,-1), 6),
                    ("LEFTPADDING",  (0,0), (-1,-1), 10),
                    ("RIGHTPADDING", (0,0), (-1,-1), 10),
                    ("VALIGN",       (0,0), (-1,-1), "MIDDLE"),
                ]))
                return t

            # ── Construction du document ──────────────────────────────
            story = []

            # === EN-TÊTE BLEU ===
            header_data = [[
                Paragraph("<font color='white'><b>GestRes Pro</b></font>", _style("h1", fontSize=18, textColor=WHITE, fontName="Helvetica-Bold")),
                Paragraph(f"<font color='white'>CONTRAT-{contract_id:04d}</font>",
                          _style("h2", fontSize=14, textColor=WHITE, alignment=TA_RIGHT, fontName="Helvetica-Bold")),
            ]]
            header = Table(header_data, colWidths=[W/2, W/2])
            header.setStyle(TableStyle([
                ("BACKGROUND",    (0,0), (-1,-1), NAVY),
                ("TOPPADDING",    (0,0), (-1,-1), 16),
                ("BOTTOMPADDING", (0,0), (-1,-1), 16),
                ("LEFTPADDING",   (0,0), (-1,-1), 16),
                ("RIGHTPADDING",  (0,0), (-1,-1), 16),
                ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
            ]))
            story.append(header)

            # Sous-titre
            sub_data = [[
                Paragraph("Contrat d'affectation de ressource",
                          _style("sub", fontSize=10, textColor=WHITE, fontName="Helvetica")),
                Paragraph(f"Généré le {gen_date}",
                          _style("sub2", fontSize=9, textColor=colors.HexColor("#93c5fd"), alignment=TA_RIGHT)),
            ]]
            sub = Table(sub_data, colWidths=[W/2, W/2])
            sub.setStyle(TableStyle([
                ("BACKGROUND",    (0,0), (-1,-1), BLUE),
                ("TOPPADDING",    (0,0), (-1,-1), 8),
                ("BOTTOMPADDING", (0,0), (-1,-1), 8),
                ("LEFTPADDING",   (0,0), (-1,-1), 16),
                ("RIGHTPADDING",  (0,0), (-1,-1), 16),
            ]))
            story.append(sub)
            story.append(Spacer(1, 0.5*cm))

            # === PARTIES ===
            story.append(Paragraph("Parties concernées", s_section))
            story.append(info_table([
                ("Bénéficiaire",  user_name),
                ("Email",         user_email),
                ("Responsable",   assigner),
            ]))
            story.append(Spacer(1, 0.4*cm))

            # === RESSOURCE ===
            story.append(Paragraph("Ressource concernée", s_section))
            story.append(info_table([
                ("Désignation",      res_name),
                ("Type",             res_type),
                ("N° de série",      res_serial),
                ("Date de début",    date_debut),
                ("Date de fin",      date_fin),
            ]))
            story.append(Spacer(1, 0.4*cm))

            # === OBJET ===
            if objet.strip():
                story.append(Paragraph("Objet du contrat", s_section))
                story.append(HRFlowable(width="100%", thickness=1, color=BORDER))
                story.append(Spacer(1, 0.2*cm))
                story.append(Paragraph(objet.strip(), s_body))
                story.append(Spacer(1, 0.2*cm))

            # === CONDITIONS ===
            if conditions.strip():
                story.append(Paragraph("Conditions d'utilisation", s_section))
                story.append(HRFlowable(width="100%", thickness=1, color=BORDER))
                story.append(Spacer(1, 0.2*cm))
                story.append(Paragraph(conditions.strip(), s_body))
                story.append(Spacer(1, 0.2*cm))

            # === NOTES ===
            if notes_txt.strip() and notes_txt.strip() != "Aucune note particulière.":
                story.append(Paragraph("Notes et clauses particulières", s_section))
                story.append(HRFlowable(width="100%", thickness=1, color=BORDER))
                story.append(Spacer(1, 0.2*cm))
                story.append(Paragraph(notes_txt.strip(), s_body))
                story.append(Spacer(1, 0.2*cm))

            # === SIGNATURE ÉLECTRONIQUE ===
            if contract.is_signed and contract.signed_at:
                story.append(Spacer(1, 0.3*cm))
                signed_box = Table([[
                    Paragraph(
                        f"✔  Contrat signé électroniquement le "
                        f"{contract.signed_at.strftime('%d/%m/%Y à %H:%M UTC')}",
                        s_signed)
                ]], colWidths=[W])
                signed_box.setStyle(TableStyle([
                    ("BACKGROUND",    (0,0), (-1,-1), colors.HexColor("#d1fae5")),
                    ("BOX",           (0,0), (-1,-1), 1, GREEN),
                    ("TOPPADDING",    (0,0), (-1,-1), 10),
                    ("BOTTOMPADDING", (0,0), (-1,-1), 10),
                ]))
                story.append(signed_box)
                story.append(Spacer(1, 0.3*cm))

            # === ZONE SIGNATURES ===
            story.append(Spacer(1, 0.5*cm))
            story.append(Paragraph("Signatures", s_section))
            story.append(Spacer(1, 0.2*cm))

            sig_col = (W - 0.8*cm) / 2
            sig_data = [
                [Paragraph("Le bénéficiaire", s_sig_lbl),   Paragraph("Le responsable", s_sig_lbl)],
                [Spacer(1, 2.5*cm),                          Spacer(1, 2.5*cm)],
                [Paragraph(user_name, s_sig_name),           Paragraph(assigner, s_sig_name)],
                [Paragraph("Date : _____ / _____ / _____",  s_sig_lbl),
                 Paragraph("Date : _____ / _____ / _____",  s_sig_lbl)],
            ]
            sig_table = Table(sig_data, colWidths=[sig_col, sig_col], spaceBefore=0)
            sig_table.setStyle(TableStyle([
                ("BOX",           (0,0), (0,-1), 1, BORDER),
                ("BOX",           (1,0), (1,-1), 1, BORDER),
                ("BACKGROUND",    (0,0), (-1, 0), LIGHT),
                ("BACKGROUND",    (0,2), (-1,-1), GRAY_BG),
                ("ALIGN",         (0,0), (-1,-1), "CENTER"),
                ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
                ("TOPPADDING",    (0,0), (-1,-1), 8),
                ("BOTTOMPADDING", (0,0), (-1,-1), 8),
                ("LEFTPADDING",   (0,0), (-1,-1), 4),
                ("RIGHTPADDING",  (0,0), (-1,-1), 4),
                ("COLPADDING",    (0,0), (-1,-1), 20),
            ]))
            story.append(sig_table)

            # === PIED DE PAGE ===
            story.append(Spacer(1, 0.8*cm))
            story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER))
            story.append(Spacer(1, 0.2*cm))
            story.append(Paragraph(
                f"GestRes Pro — BTS SIO SLAM 2026  |  "
                f"Réf. CONTRAT-{contract_id:04d}  |  "
                f"Hash SHA-256 : {contract.content_hash[:24]}...",
                s_footer
            ))

            doc = SimpleDocTemplate(
                str(pdf_path),
                pagesize=A4,
                rightMargin=2*cm, leftMargin=2*cm,
                topMargin=1.5*cm, bottomMargin=1.5*cm
            )
            doc.build(story)

            contract.pdf_path = str(pdf_path)
            session.commit()

            return True, str(pdf_path)

    def _build_contract_content(self, assignment, objet, conditions, notes):
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

    def _format_contract(self, contract):
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
