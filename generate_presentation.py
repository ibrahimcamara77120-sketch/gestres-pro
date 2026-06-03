"""
Génère le PDF de présentation orale GestRes Pro (~25 minutes)
Usage : python generate_presentation.py
Sortie : docs/presentation_gestres_pro.pdf
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable,
    Table, TableStyle, PageBreak, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

OUTPUT = "docs/presentation_gestres_pro.pdf"

# ── Couleurs ──────────────────────────────────────────────────────────────────
BLEU_FONCE  = colors.HexColor("#1A2E4A")
BLEU_MOYEN  = colors.HexColor("#2C5F8A")
BLEU_CLAIR  = colors.HexColor("#D6E8F7")
ORANGE      = colors.HexColor("#E8730A")
GRIS_NOTE   = colors.HexColor("#F4F4F4")
GRIS_BORD   = colors.HexColor("#CCCCCC")
VERT        = colors.HexColor("#1E7D45")
BLANC       = colors.white

# ── Styles ────────────────────────────────────────────────────────────────────
styles = getSampleStyleSheet()

def s(name, **kw):
    """Crée un ParagraphStyle à la volée."""
    return ParagraphStyle(name, **kw)

STYLE_PAGE_TITRE = s("PageTitre",
    fontSize=28, leading=36, textColor=BLANC,
    alignment=TA_CENTER, fontName="Helvetica-Bold",
    spaceAfter=6)

STYLE_PAGE_SOUS = s("PageSous",
    fontSize=14, leading=20, textColor=BLEU_CLAIR,
    alignment=TA_CENTER, fontName="Helvetica",
    spaceAfter=4)

STYLE_SECTION = s("Section",
    fontSize=18, leading=26, textColor=BLEU_FONCE,
    fontName="Helvetica-Bold", spaceBefore=14, spaceAfter=6)

STYLE_SOUS_SECTION = s("SousSec",
    fontSize=13, leading=18, textColor=BLEU_MOYEN,
    fontName="Helvetica-Bold", spaceBefore=8, spaceAfter=4)

STYLE_CORPS = s("Corps",
    fontSize=10.5, leading=16, textColor=colors.black,
    fontName="Helvetica", alignment=TA_JUSTIFY, spaceAfter=4)

STYLE_BULLET = s("Bullet",
    fontSize=10.5, leading=16, textColor=colors.black,
    fontName="Helvetica", leftIndent=14, spaceBefore=2,
    bulletIndent=4, spaceAfter=2)

STYLE_NOTE_TITRE = s("NoteTitre",
    fontSize=9, leading=12, textColor=BLEU_MOYEN,
    fontName="Helvetica-Bold", spaceBefore=4, spaceAfter=2)

STYLE_NOTE = s("Note",
    fontSize=9.5, leading=14, textColor=colors.HexColor("#333333"),
    fontName="Helvetica", alignment=TA_JUSTIFY, spaceAfter=2)

STYLE_TIMING = s("Timing",
    fontSize=9, leading=12, textColor=ORANGE,
    fontName="Helvetica-Bold", alignment=TA_CENTER)

STYLE_CODE = s("Code",
    fontSize=9, leading=13, textColor=colors.HexColor("#1A1A1A"),
    fontName="Courier", backColor=colors.HexColor("#F0F0F0"),
    leftIndent=10, rightIndent=10, spaceBefore=4, spaceAfter=4)


# ── Helpers ───────────────────────────────────────────────────────────────────
def hr(color=BLEU_MOYEN, thickness=1):
    return HRFlowable(width="100%", thickness=thickness,
                      color=color, spaceAfter=6, spaceBefore=4)

def note_box(timing, *lignes):
    """Encadré gris pour les notes de l'orateur."""
    inner = [Paragraph(f"<b>NOTES ORATEUR</b>  ·  {timing}", STYLE_NOTE_TITRE)]
    for l in lignes:
        inner.append(Paragraph(f"• {l}", STYLE_NOTE))
    data = [[inner]]
    t = Table(data, colWidths=[17*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), GRIS_NOTE),
        ("BOX",        (0,0), (-1,-1), 0.5, GRIS_BORD),
        ("TOPPADDING",    (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
        ("LEFTPADDING",   (0,0), (-1,-1), 12),
        ("RIGHTPADDING",  (0,0), (-1,-1), 12),
    ]))
    return t

def titre_section_box(numero, titre, duree):
    """Bandeau coloré pour une nouvelle grande section."""
    data = [[
        Paragraph(f"<font color='white'><b>{numero}</b></font>",
                  s("N", fontSize=22, fontName="Helvetica-Bold",
                    textColor=BLANC, alignment=TA_CENTER)),
        Paragraph(f"<font color='white'><b>{titre}</b></font>",
                  s("T", fontSize=16, fontName="Helvetica-Bold",
                    textColor=BLANC, leading=20)),
        Paragraph(f"<font color='#FFD580'>{duree}</font>",
                  s("D", fontSize=11, fontName="Helvetica",
                    textColor=colors.HexColor("#FFD580"), alignment=TA_CENTER)),
    ]]
    t = Table(data, colWidths=[1.8*cm, 12*cm, 3.2*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), BLEU_FONCE),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING",    (0,0), (-1,-1), 10),
        ("BOTTOMPADDING", (0,0), (-1,-1), 10),
        ("LEFTPADDING",   (0,0), (0,-1),  10),
        ("LEFTPADDING",   (1,0), (1,-1),  8),
    ]))
    return t

def page_couverture():
    """Page de garde."""
    elems = []
    # Bandeau haut
    data = [[Paragraph("GestRes Pro", STYLE_PAGE_TITRE),
             Paragraph("Système de gestion de ressources d'entreprise", STYLE_PAGE_SOUS)]]
    t = Table([[
        Paragraph("GestRes Pro",
                  s("PT", fontSize=34, fontName="Helvetica-Bold",
                    textColor=BLANC, alignment=TA_CENTER, leading=42)),
    ]], colWidths=[17*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), BLEU_FONCE),
        ("TOPPADDING",    (0,0), (-1,-1), 30),
        ("BOTTOMPADDING", (0,0), (-1,-1), 30),
    ]))
    elems.append(t)
    elems.append(Spacer(1, 0.4*cm))

    sub = Table([[
        Paragraph("Système de gestion de ressources d'entreprise",
                  s("ST", fontSize=15, fontName="Helvetica",
                    textColor=BLEU_FONCE, alignment=TA_CENTER)),
    ]], colWidths=[17*cm])
    sub.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), BLEU_CLAIR),
        ("TOPPADDING",    (0,0), (-1,-1), 12),
        ("BOTTOMPADDING", (0,0), (-1,-1), 12),
    ]))
    elems.append(sub)
    elems.append(Spacer(1, 1.2*cm))

    # Infos candidat
    infos = [
        ["Candidat",   "CAMARA Ibrahim"],
        ["N° candidat","2545812845"],
        ["Formation",  "Digital School of Paris – IEF2I"],
        ["Option",     "BTS SIO – SLAM (Solutions Logicielles et Applications Métiers)"],
        ["Session",    "2026"],
        ["Épreuve",    "E6 – Présentation orale du projet"],
        ["Durée de présentation", "~25 minutes"],
    ]
    rows = []
    for k, v in infos:
        rows.append([
            Paragraph(k, s("K", fontSize=10, fontName="Helvetica-Bold",
                           textColor=BLEU_FONCE)),
            Paragraph(v, s("V", fontSize=10, fontName="Helvetica",
                           textColor=colors.black)),
        ])
    t2 = Table(rows, colWidths=[5.5*cm, 11.5*cm])
    t2.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (0,-1), BLEU_CLAIR),
        ("BACKGROUND",    (1,0), (1,-1), BLANC),
        ("BOX",           (0,0), (-1,-1), 0.8, BLEU_MOYEN),
        ("INNERGRID",     (0,0), (-1,-1), 0.3, GRIS_BORD),
        ("TOPPADDING",    (0,0), (-1,-1), 7),
        ("BOTTOMPADDING", (0,0), (-1,-1), 7),
        ("LEFTPADDING",   (0,0), (-1,-1), 10),
    ]))
    elems.append(t2)
    elems.append(Spacer(1, 1*cm))
    elems.append(hr(BLEU_MOYEN, 2))
    elems.append(Spacer(1, 0.3*cm))

    # Plan rapide
    plan_titre = Paragraph("Plan de la présentation", STYLE_SOUS_SECTION)
    plan_data = [
        ["01", "Introduction & contexte",           "2 min"],
        ["02", "Analyse du besoin et spécifications","3 min"],
        ["03", "Architecture technique",             "4 min"],
        ["04", "Fonctionnalités principales",        "5 min"],
        ["05", "Sécurité et conformité RGPD",        "3 min"],
        ["06", "Tests et qualité logicielle",        "3 min"],
        ["07", "Difficultés et solutions",           "3 min"],
        ["08", "Bilan & compétences BTS SIO",        "2 min"],
    ]
    header = [
        Paragraph("<b>#</b>", s("H", fontSize=10, fontName="Helvetica-Bold", textColor=BLANC)),
        Paragraph("<b>Section</b>", s("H", fontSize=10, fontName="Helvetica-Bold", textColor=BLANC)),
        Paragraph("<b>Durée</b>", s("H", fontSize=10, fontName="Helvetica-Bold", textColor=BLANC, alignment=TA_CENTER)),
    ]
    rows2 = [header]
    for i, (num, sec, dur) in enumerate(plan_data):
        bg = BLEU_CLAIR if i % 2 == 0 else BLANC
        rows2.append([
            Paragraph(num, s("N2", fontSize=10, fontName="Helvetica-Bold", textColor=BLEU_MOYEN, alignment=TA_CENTER)),
            Paragraph(sec, s("S2", fontSize=10, fontName="Helvetica", textColor=colors.black)),
            Paragraph(dur, s("D2", fontSize=10, fontName="Helvetica", textColor=ORANGE, alignment=TA_CENTER)),
        ])
    t3 = Table(rows2, colWidths=[1.5*cm, 12.5*cm, 3*cm])
    t3.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), BLEU_FONCE),
        ("BACKGROUND", (0,1), (-1,1), BLEU_CLAIR),
        ("BACKGROUND", (0,2), (-1,2), BLANC),
        ("BACKGROUND", (0,3), (-1,3), BLEU_CLAIR),
        ("BACKGROUND", (0,4), (-1,4), BLANC),
        ("BACKGROUND", (0,5), (-1,5), BLEU_CLAIR),
        ("BACKGROUND", (0,6), (-1,6), BLANC),
        ("BACKGROUND", (0,7), (-1,7), BLEU_CLAIR),
        ("BACKGROUND", (0,8), (-1,8), BLANC),
        ("BOX",        (0,0), (-1,-1), 0.8, BLEU_MOYEN),
        ("INNERGRID",  (0,0), (-1,-1), 0.3, GRIS_BORD),
        ("TOPPADDING",    (0,0), (-1,-1), 7),
        ("BOTTOMPADDING", (0,0), (-1,-1), 7),
        ("LEFTPADDING",   (0,0), (-1,-1), 10),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
    ]))
    elems += [plan_titre, t3]
    elems.append(PageBreak())
    return elems


# ── Contenu ───────────────────────────────────────────────────────────────────
def section_01():
    e = []
    e.append(titre_section_box("01", "Introduction & Contexte du projet", "≈ 2 min"))
    e.append(Spacer(1, 0.5*cm))

    e.append(Paragraph("Bonjour à tous,", STYLE_CORPS))
    e.append(Spacer(1, 0.2*cm))
    e.append(Paragraph(
        "Je m'appelle <b>CAMARA Ibrahim</b>, je suis étudiant en deuxième année de BTS SIO option "
        "SLAM à la Digital School of Paris. Je vais vous présenter aujourd'hui mon projet de "
        "session 2026 : <b>GestRes Pro</b>, une application de gestion de ressources d'entreprise.",
        STYLE_CORPS))
    e.append(Spacer(1, 0.4*cm))

    e.append(Paragraph("Contexte et origine du projet", STYLE_SECTION))
    e.append(hr())
    e.append(Paragraph(
        "La problématique de départ est simple : dans de nombreuses entreprises, la gestion des "
        "ressources — qu'il s'agisse d'équipements informatiques, de véhicules, de badges d'accès "
        "ou de comptes applicatifs — est encore effectuée manuellement, via des fichiers Excel "
        "dispersés, sans traçabilité fiable ni conformité RGPD. Cela entraîne des pertes de "
        "matériel, des oublis d'affectation, des risques de sécurité et des difficultés lors d'audits.",
        STYLE_CORPS))
    e.append(Spacer(1, 0.3*cm))
    e.append(Paragraph(
        "C'est dans ce contexte que j'ai conçu et développé <b>GestRes Pro</b> : une application "
        "de bureau complète, sécurisée et conforme au RGPD, qui centralise le cycle de vie complet "
        "de toutes les ressources d'une organisation.",
        STYLE_CORPS))
    e.append(Spacer(1, 0.4*cm))

    e.append(Paragraph("Durée et périmètre de réalisation", STYLE_SOUS_SECTION))
    e.append(Paragraph(
        "Le projet a été réalisé <b>seul</b>, de <b>septembre 2025 à mai 2026</b>, dans le cadre "
        "de l'épreuve E6 du BTS SIO. Il représente environ <b>4 971 lignes de code source</b> "
        "réparties sur plus de 30 fichiers Python.",
        STYLE_CORPS))
    e.append(Spacer(1, 0.4*cm))

    e.append(note_box("≈ 2 min",
        "Regarder le jury, sourire, respirer.",
        "Insister sur le mot 'seul' — projet individuel.",
        "Mentionner que la démonstration sera faite en live avec la société test CleanPro Services.",
        "Ne pas rentrer dans les détails techniques ici, juste planter le décor."))
    e.append(PageBreak())
    return e


def section_02():
    e = []
    e.append(titre_section_box("02", "Analyse du besoin et spécifications", "≈ 3 min"))
    e.append(Spacer(1, 0.5*cm))

    e.append(Paragraph("Identification des acteurs", STYLE_SECTION))
    e.append(hr())
    e.append(Paragraph(
        "Avant d'écrire la première ligne de code, j'ai conduit une analyse des besoins en "
        "m'appuyant sur des cas d'usage concrets. Trois types d'utilisateurs ont été identifiés :",
        STYLE_CORPS))
    e.append(Spacer(1, 0.2*cm))

    acteurs = [
        ["Rôle", "Responsabilités principales", "Accès"],
        ["Super Administrateur",
         "Crée les espaces entreprise, configure les types de ressources, définit les rôles",
         "Toutes les permissions [\"all\"]"],
        ["Administrateur d'entreprise",
         "Gestion complète des ressources et utilisateurs, accès aux logs, génération de contrats",
         "8 permissions spécifiques"],
        ["Employé",
         "Consultation de ses propres affectations, signature électronique de contrats, historique personnel",
         "4 permissions restreintes"],
    ]
    rows = []
    for i, row in enumerate(acteurs):
        bg = BLEU_FONCE if i == 0 else (BLEU_CLAIR if i % 2 == 1 else BLANC)
        style = s("C", fontSize=9.5, fontName="Helvetica-Bold" if i == 0 else "Helvetica",
                  textColor=BLANC if i == 0 else colors.black, leading=14)
        rows.append([Paragraph(cell, style) for cell in row])
    t = Table(rows, colWidths=[4*cm, 8.5*cm, 4.5*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), BLEU_FONCE),
        ("BACKGROUND", (0,1), (-1,1), BLEU_CLAIR),
        ("BACKGROUND", (0,2), (-1,2), BLANC),
        ("BACKGROUND", (0,3), (-1,3), BLEU_CLAIR),
        ("BOX",        (0,0), (-1,-1), 0.8, BLEU_MOYEN),
        ("INNERGRID",  (0,0), (-1,-1), 0.3, GRIS_BORD),
        ("TOPPADDING",    (0,0), (-1,-1), 7),
        ("BOTTOMPADDING", (0,0), (-1,-1), 7),
        ("LEFTPADDING",   (0,0), (-1,-1), 8),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
    ]))
    e.append(t)
    e.append(Spacer(1, 0.5*cm))

    e.append(Paragraph("Types de ressources gérées", STYLE_SECTION))
    e.append(hr())
    ressources = [
        ("Équipements informatiques", "PC, laptops, serveurs, périphériques"),
        ("Comptes applicatifs",        "Accès aux logiciels, licences"),
        ("Véhicules",                  "Flotte automobile de l'entreprise"),
        ("Badges / cartes d'accès",    "Contrôle d'accès physique aux locaux"),
        ("Téléphonie",                 "Mobiles, fixes, abonnements"),
        ("Mobilier & équipements",     "Bureau, chaises, équipements divers"),
        ("Ressources personnalisées",  "Types définis librement par l'admin"),
    ]
    for nom, desc in ressources:
        e.append(Paragraph(f"<b>→ {nom}</b> : {desc}", STYLE_BULLET))
    e.append(Spacer(1, 0.5*cm))

    e.append(Paragraph("Contraintes identifiées", STYLE_SOUS_SECTION))
    contraintes = [
        "Conformité RGPD / CNIL : minimisation des données, droit à l'oubli, journaux d'accès",
        "Sécurité : aucune requête SQL brute, mots de passe hachés, intégrité des contrats",
        "Portabilité : application bureau autonome, base de données PostgreSQL (psycopg2)",
        "Traçabilité : chaque action sur une ressource est enregistrée dans un journal d'audit",
        "Multi-entreprise : chaque société dispose de son espace de données isolé",
    ]
    for c in contraintes:
        e.append(Paragraph(f"• {c}", STYLE_BULLET))
    e.append(Spacer(1, 0.4*cm))

    e.append(note_box("≈ 3 min",
        "Mentionner que le cahier des charges a orienté toutes les décisions d'architecture.",
        "Insister sur le fait que le RGPD n'est pas une contrainte ajoutée après coup : c'est pensé dès le départ.",
        "Si le jury pose une question sur les exigences, renvoyer aux compétences BTS SIO (A1.1, A1.2, A2.1)."))
    e.append(PageBreak())
    return e


def section_03():
    e = []
    e.append(titre_section_box("03", "Architecture technique", "≈ 4 min"))
    e.append(Spacer(1, 0.5*cm))

    e.append(Paragraph("Stack technologique", STYLE_SECTION))
    e.append(hr())
    stack = [
        ["Couche",          "Technologie",             "Rôle"],
        ["Langage",         "Python 3.14",             "Langage principal"],
        ["Interface graphique", "PySide6 ≥ 6.6",      "Framework Qt — vues et widgets"],
        ["ORM / Base de données", "SQLAlchemy 2.0 + PostgreSQL", "Modèles, requêtes, triggers PL/pgSQL"],
        ["Hachage",         "bcrypt 4.1 (rounds=12)",  "Sécurisation des mots de passe"],
        ["PDF",             "ReportLab 4.0 + PyMuPDF 1.27", "Génération et remplissage de contrats"],
        ["Tests",           "pytest 155 tests",        "Tests unitaires et d'intégration"],
        ["Backup",          "Module utils/backup.py",  "Sauvegarde locale automatique de la BDD"],
    ]
    rows = []
    for i, row in enumerate(stack):
        bg = BLEU_FONCE if i == 0 else (BLEU_CLAIR if i % 2 == 1 else BLANC)
        st = s("C", fontSize=9.5, fontName="Helvetica-Bold" if i == 0 else "Helvetica",
               textColor=BLANC if i == 0 else colors.black, leading=14)
        rows.append([Paragraph(c, st) for c in row])
    t = Table(rows, colWidths=[4.5*cm, 6*cm, 6.5*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), BLEU_FONCE),
        ("BACKGROUND", (0,1), (-1,1), BLEU_CLAIR),
        ("BACKGROUND", (0,2), (-1,2), BLANC),
        ("BACKGROUND", (0,3), (-1,3), BLEU_CLAIR),
        ("BACKGROUND", (0,4), (-1,4), BLANC),
        ("BACKGROUND", (0,5), (-1,5), BLEU_CLAIR),
        ("BACKGROUND", (0,6), (-1,6), BLANC),
        ("BACKGROUND", (0,7), (-1,7), BLEU_CLAIR),
        ("BOX",        (0,0), (-1,-1), 0.8, BLEU_MOYEN),
        ("INNERGRID",  (0,0), (-1,-1), 0.3, GRIS_BORD),
        ("TOPPADDING",    (0,0), (-1,-1), 7),
        ("BOTTOMPADDING", (0,0), (-1,-1), 7),
        ("LEFTPADDING",   (0,0), (-1,-1), 8),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
    ]))
    e.append(t)
    e.append(Spacer(1, 0.5*cm))

    e.append(Paragraph("Pattern MVC — séparation des responsabilités", STYLE_SECTION))
    e.append(hr())
    e.append(Paragraph(
        "J'ai choisi le pattern <b>MVC (Modèle-Vue-Contrôleur)</b> pour garantir une séparation "
        "claire des responsabilités et faciliter la maintenance. Voici comment s'organise le code :",
        STYLE_CORPS))
    e.append(Spacer(1, 0.3*cm))

    mvc = [
        ("MODÈLES (src/models/)",
         "10 modèles SQLAlchemy",
         ["user.py — utilisateurs, rôles, hachage bcrypt",
          "company.py — espaces entreprise multi-tenant",
          "resource.py + resource_type.py — ressources et leurs catégories",
          "assignment.py — affectations ressource ↔ utilisateur",
          "contract.py — contrats PDF signés électroniquement",
          "audit_log.py — journal de toutes les actions",
          "base.py — configuration moteur SQLAlchemy"]),
        ("CONTRÔLEURS (src/controllers/)",
         "6 contrôleurs",
         ["auth_controller.py — authentification, sessions, tokens",
          "company_controller.py — CRUD entreprises",
          "resource_controller.py — CRUD ressources et types",
          "assignment_controller.py — gestion des affectations",
          "contract_controller.py — génération, signature, vérification PDF",
          "user_controller.py — gestion des utilisateurs internes"]),
        ("VUES (src/views/)",
         "10 vues PySide6",
         ["login_view.py — écran d'authentification",
          "main_window.py — fenêtre principale, navigation par onglets",
          "dashboard_view.py — tableau de bord avec statistiques",
          "resources_view.py / users_view.py — gestion CRUD avec filtres",
          "assignments_view.py / contracts_view.py — affectations et contrats",
          "logs_view.py — journal d'audit filtrable",
          "companies_view.py — liste des espaces entreprise"]),
        ("UTILITAIRES (src/utils/)",
         "4 modules",
         ["security.py — bcrypt, SHA-256, validation SIRET, sanitize_input()",
          "validators.py — validation email, SIRET, forces de mot de passe",
          "backup.py — sauvegarde automatique de la BDD PostgreSQL",
          "maintenance.py — purge RGPD, anonymisation, nettoyage"]),
    ]
    for titre, sous, items in mvc:
        e.append(Paragraph(f"<b>{titre}</b> — {sous}", STYLE_SOUS_SECTION))
        for item in items:
            e.append(Paragraph(f"  → {item}", STYLE_BULLET))
        e.append(Spacer(1, 0.2*cm))

    e.append(Spacer(1, 0.2*cm))
    e.append(note_box("≈ 4 min",
        "Pointer chaque couche MVC sur un schéma si disponible (diagramme page 5 de l'annexe).",
        "Expliquer pourquoi MVC : testabilité, maintenabilité, respect du principe de responsabilité unique.",
        "Si question sur SQLAlchemy : 'j'utilise l'ORM pour ne jamais écrire de SQL brut, ce qui élimine le risque d'injection SQL'.",
        "Si question sur PySide6 vs Tkinter : 'PySide6 offre des widgets professionnels, des threads Qt et une meilleure expérience utilisateur'."))
    e.append(PageBreak())
    return e


def section_04():
    e = []
    e.append(titre_section_box("04", "Fonctionnalités principales", "≈ 5 min"))
    e.append(Spacer(1, 0.5*cm))

    e.append(Paragraph(
        "Je vais maintenant vous présenter les fonctionnalités clés de GestRes Pro, que je vais "
        "illustrer avec la société de démonstration <b>CleanPro Services</b> — une société de "
        "nettoyage fictive préconfigurée dans la base de données.",
        STYLE_CORPS))
    e.append(Spacer(1, 0.4*cm))

    foncs = [
        ("a", "Authentification sécurisée",
         "L'écran de connexion valide les identifiants via bcrypt (rounds=12). Un token de session "
         "est généré avec secrets.token_hex(32). Trois tentatives échouées verrouillent le compte."),
        ("b", "Tableau de bord",
         "À la connexion, l'administrateur accède à un tableau de bord affichant en temps réel : "
         "le nombre de ressources actives, les affectations en cours, les contrats en attente de "
         "signature, et les dernières actions du journal d'audit."),
        ("c", "Gestion des ressources",
         "Création, modification, suppression et archivage de ressources. Chaque ressource est "
         "typée (matériel, véhicule, compte…), possède un état (disponible, affecté, en maintenance, "
         "hors service) et un numéro de série unique. La vue propose des filtres avancés par type, "
         "état, et recherche textuelle."),
        ("d", "Gestion des affectations",
         "Un employé peut se voir affecter une ou plusieurs ressources. L'affectation enregistre "
         "la date de début, la date de fin prévue, et génère automatiquement un contrat PDF. "
         "Chaque retour de ressource est tracé dans le journal d'audit."),
        ("e", "Génération et signature de contrats PDF",
         "À chaque affectation, un contrat PDF est généré avec ReportLab. L'employé peut le "
         "signer électroniquement depuis l'application. La signature est calculée en SHA-256 : "
         "hash_contenu + données_signataire + horodatage ISO. La vérification d'intégrité est "
         "possible à tout moment."),
        ("f", "Journal d'audit complet",
         "Chaque action (connexion, création, modification, suppression, signature) est enregistrée "
         "avec : utilisateur, action, table cible, ancienne valeur, nouvelle valeur, timestamp. "
         "La rétention est de 5 ans (AUDIT_LOG_RETENTION_DAYS=1825) conformément au RGPD."),
        ("g", "Gestion multi-entreprise",
         "Le super administrateur peut créer plusieurs espaces entreprise (validation du SIRET "
         "par algorithme de Luhn). Chaque espace est totalement isolé. Les administrateurs n'ont "
         "accès qu'aux données de leur propre société."),
        ("h", "Maintenance et conformité RGPD",
         "Un module de maintenance permet la purge automatique des données expirées, l'anonymisation "
         "pour le droit à l'oubli, et la sauvegarde locale de la base de données. La rétention "
         "par défaut des données personnelles est de 3 ans (DEFAULT_RETENTION_DAYS=1095)."),
    ]
    for lettre, titre, desc in foncs:
        e.append(KeepTogether([
            Paragraph(f"<b>{lettre})</b>  {titre}", STYLE_SOUS_SECTION),
            Paragraph(desc, STYLE_CORPS),
            Spacer(1, 0.2*cm),
        ]))

    e.append(Spacer(1, 0.3*cm))
    e.append(Paragraph("Données de démonstration — CleanPro Services", STYLE_SECTION))
    e.append(hr())
    demo = [
        ["Élément", "Détail"],
        ["Société",         "CleanPro Services — SIRET 73282932000074"],
        ["Adresse",         "12 rue des Lilas, Paris 13e"],
        ["Administrateur",  "Marie Dupont (responsable@cleanpro.test / Responsable1!)"],
        ["Employés",        "4 employés avec affectations et contrats signés"],
        ["Ressources",      "20 ressources (7 types différents)"],
        ["Affectations",    "11 affectations actives"],
        ["Contrats",        "11 contrats PDF signés électroniquement"],
    ]
    rows = []
    for i, row in enumerate(demo):
        st = s("C", fontSize=9.5, fontName="Helvetica-Bold" if i == 0 else "Helvetica",
               textColor=BLANC if i == 0 else colors.black, leading=14)
        rows.append([Paragraph(c, st) for c in row])
    t = Table(rows, colWidths=[5*cm, 12*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), BLEU_FONCE),
        ("BACKGROUND", (0,1), (-1,1), BLEU_CLAIR),
        ("BACKGROUND", (0,2), (-1,2), BLANC),
        ("BACKGROUND", (0,3), (-1,3), BLEU_CLAIR),
        ("BACKGROUND", (0,4), (-1,4), BLANC),
        ("BACKGROUND", (0,5), (-1,5), BLEU_CLAIR),
        ("BACKGROUND", (0,6), (-1,6), BLANC),
        ("BACKGROUND", (0,7), (-1,7), BLEU_CLAIR),
        ("BOX",        (0,0), (-1,-1), 0.8, BLEU_MOYEN),
        ("INNERGRID",  (0,0), (-1,-1), 0.3, GRIS_BORD),
        ("TOPPADDING",    (0,0), (-1,-1), 7),
        ("BOTTOMPADDING", (0,0), (-1,-1), 7),
        ("LEFTPADDING",   (0,0), (-1,-1), 8),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
    ]))
    e.append(t)
    e.append(Spacer(1, 0.4*cm))

    e.append(note_box("≈ 5 min",
        "Faire la démonstration live pendant cette section (ouvrir l'appli).",
        "Montrer dans l'ordre : connexion admin → dashboard → liste ressources → une affectation → un contrat PDF → le journal d'audit.",
        "Si une fonctionnalité ne fonctionne pas en démo, rester calme et décrire le comportement attendu.",
        "Identifiants demo : responsable@cleanpro.test / Responsable1!",
        "Super admin : superadmin@gestres.test / SuperAdmin1!"))
    e.append(PageBreak())
    return e


def section_05():
    e = []
    e.append(titre_section_box("05", "Sécurité et conformité RGPD", "≈ 3 min"))
    e.append(Spacer(1, 0.5*cm))

    e.append(Paragraph(
        "La sécurité et la conformité réglementaire ont été des priorités absolues dans la "
        "conception de GestRes Pro, pas des fonctionnalités ajoutées en dernier lieu.",
        STYLE_CORPS))
    e.append(Spacer(1, 0.3*cm))

    e.append(Paragraph("Mesures de sécurité techniques", STYLE_SECTION))
    e.append(hr())
    secu = [
        ("Hachage bcrypt rounds=12",
         "Chaque mot de passe est haché avec bcrypt au facteur de coût 12. Même en cas de fuite "
         "de la base de données, les mots de passe restent protégés."),
        ("Zéro SQL brut",
         "Toutes les requêtes passent par l'ORM SQLAlchemy. Il est structurellement impossible "
         "d'effectuer une injection SQL."),
        ("Sanitisation des entrées",
         "La fonction sanitize_input() nettoie tous les champs texte. La validation de force de "
         "mot de passe vérifie majuscules, chiffres et caractères spéciaux."),
        ("Intégrité des contrats SHA-256",
         "Chaque contrat signé produit une empreinte SHA-256 : hash_contenu + données_signataire "
         "+ horodatage ISO. La falsification d'un contrat est détectable immédiatement."),
        ("Tokens de session sécurisés",
         "secrets.token_hex(32) génère 32 octets d'entropie cryptographique par session. "
         "Aucun token prédictible."),
        ("Validation SIRET (Luhn)",
         "L'algorithme de Luhn vérifie la validité mathématique du numéro SIRET, avec un garde "
         "explicite contre les SIRET composés de zéros."),
    ]
    for titre, desc in secu:
        e.append(Paragraph(f"<b>→ {titre}</b>", STYLE_SOUS_SECTION))
        e.append(Paragraph(desc, STYLE_CORPS))
        e.append(Spacer(1, 0.1*cm))

    e.append(Spacer(1, 0.3*cm))
    e.append(Paragraph("Conformité RGPD / CNIL", STYLE_SECTION))
    e.append(hr())
    rgpd = [
        "Minimisation des données : seules les informations nécessaires sont collectées.",
        "Rétention configurable : 3 ans pour les données personnelles (DEFAULT_RETENTION_DAYS=1095), "
        "5 ans pour les journaux d'audit (AUDIT_LOG_RETENTION_DAYS=1825).",
        "Droit à l'oubli : anonymisation des données de l'utilisateur via le module maintenance.py "
        "(remplacement du nom et de l'email par des valeurs anonymisées).",
        "Journal d'accès : chaque consultation et modification de données personnelles est tracée.",
        "Stockage local uniquement : aucune donnée n'est transmise vers des serveurs tiers.",
        "Intégrité des contrats : la signature SHA-256 garantit la non-répudiation.",
    ]
    for r in rgpd:
        e.append(Paragraph(f"• {r}", STYLE_BULLET))

    e.append(Spacer(1, 0.4*cm))
    e.append(note_box("≈ 3 min",
        "Si le jury demande pourquoi bcrypt et pas SHA-256 pour les mots de passe : 'bcrypt est "
        "volontairement lent et intègre un sel automatique, contrairement à SHA-256 qui est rapide et sans sel'.",
        "Si question sur le RGPD : mentionner l'article 5 (principes) et l'article 17 (droit à l'effacement).",
        "Montrer le code de security.py si possible pour prouver la rigueur."))
    e.append(PageBreak())
    return e


def section_06():
    e = []
    e.append(titre_section_box("06", "Tests et qualité logicielle", "≈ 3 min"))
    e.append(Spacer(1, 0.5*cm))

    e.append(Paragraph(
        "La qualité du code est assurée par une suite de <b>155 tests pytest</b> répartis "
        "sur 3 fichiers de tests, couvrant les modèles, les contrôleurs et les utilitaires de sécurité.",
        STYLE_CORPS))
    e.append(Spacer(1, 0.4*cm))

    e.append(Paragraph("Organisation des tests", STYLE_SECTION))
    e.append(hr())
    tests = [
        ["Fichier",             "Contenu",                            "Portée"],
        ["test_models.py",      "Tests des 10 modèles SQLAlchemy",    "Création, contraintes, relations"],
        ["test_controllers.py", "Tests des 6 contrôleurs",            "CRUD, authentification, permissions"],
        ["test_security.py",    "Tests des utilitaires de sécurité",  "Hachage, validation, sanitisation"],
        ["conftest.py",         "Fixture SQLite in-memory (tests)",   "Isolation totale — BDD PostgreSQL de prod jamais touchée"],
    ]
    rows = []
    for i, row in enumerate(tests):
        st = s("C", fontSize=9.5, fontName="Helvetica-Bold" if i == 0 else "Helvetica",
               textColor=BLANC if i == 0 else colors.black, leading=14)
        rows.append([Paragraph(c, st) for c in row])
    t = Table(rows, colWidths=[4.5*cm, 7*cm, 5.5*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), BLEU_FONCE),
        ("BACKGROUND", (0,1), (-1,1), BLEU_CLAIR),
        ("BACKGROUND", (0,2), (-1,2), BLANC),
        ("BACKGROUND", (0,3), (-1,3), BLEU_CLAIR),
        ("BACKGROUND", (0,4), (-1,4), BLANC),
        ("BOX",        (0,0), (-1,-1), 0.8, BLEU_MOYEN),
        ("INNERGRID",  (0,0), (-1,-1), 0.3, GRIS_BORD),
        ("TOPPADDING",    (0,0), (-1,-1), 7),
        ("BOTTOMPADDING", (0,0), (-1,-1), 7),
        ("LEFTPADDING",   (0,0), (-1,-1), 8),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
    ]))
    e.append(t)
    e.append(Spacer(1, 0.4*cm))

    e.append(Paragraph("Stratégie d'isolation — conftest.py", STYLE_SOUS_SECTION))
    e.append(Paragraph(
        "Le fichier conftest.py met en place une fixture autouse qui redirige tous les accès "
        "à la base de données vers une instance SQLite <b>in-memory</b>. Cela signifie que les "
        "155 tests s'exécutent sans jamais toucher database.db, garantissant une reproductibilité "
        "et une isolation parfaites. Le moteur est patché dans trois modules simultanément : "
        "base_module.engine, tests.test_controllers.engine, et tests.test_models.engine.",
        STYLE_CORPS))
    e.append(Spacer(1, 0.3*cm))

    e.append(Paragraph("Exemple de commande d'exécution", STYLE_SOUS_SECTION))
    e.append(Paragraph("python -m pytest tests/ -v", STYLE_CODE))
    e.append(Spacer(1, 0.2*cm))
    e.append(Paragraph("python -m pytest tests/test_security.py -v", STYLE_CODE))
    e.append(Spacer(1, 0.4*cm))

    e.append(Paragraph("Bug découvert et corrigé grâce aux tests", STYLE_SOUS_SECTION))
    e.append(Paragraph(
        "Un test a mis en évidence un bug dans la validation SIRET : le numéro "
        "'00000000000000' passait la validation de l'algorithme de Luhn car la somme de zéros "
        "est un multiple de 10. Un garde explicite a été ajouté dans security.py pour rejeter "
        "les SIRET composés uniquement de zéros.",
        STYLE_CORPS))
    e.append(Spacer(1, 0.4*cm))

    e.append(note_box("≈ 3 min",
        "Lancer les tests en live si le temps le permet : python -m pytest tests/ -v",
        "Si le jury demande le taux de couverture : les tests couvrent 100% des chemins critiques (auth, contrats, sécurité).",
        "Insister sur l'isolation in-memory : 'mes tests ne polluent jamais la base de données de production'."))
    e.append(PageBreak())
    return e


def section_07():
    e = []
    e.append(titre_section_box("07", "Difficultés rencontrées et solutions apportées", "≈ 3 min"))
    e.append(Spacer(1, 0.5*cm))

    e.append(Paragraph(
        "Tout projet de développement comporte des obstacles techniques. Voici les principaux "
        "défis que j'ai rencontrés et comment je les ai résolus.",
        STYLE_CORPS))
    e.append(Spacer(1, 0.4*cm))

    difficultes = [
        ("Gestion des permissions multi-rôles",
         "Défi : implémenter un système de permissions granulaire sans dupliquer la logique "
         "dans chaque vue.",
         "Solution : centralisation dans config.py avec un dictionnaire de rôles → liste de "
         "permissions. Chaque contrôleur vérifie les permissions via une méthode utilitaire "
         "unique, réduisant le code dupliqué."),
        ("Isolation des tests",
         "Défi : les premiers tests modifiaient la base de données réelle, rendant les suites "
         "de tests non reproductibles.",
         "Solution : création de conftest.py avec une fixture autouse qui substitue le moteur "
         "SQLAlchemy par une instance SQLite in-memory, patchée dans tous les modules concernés."),
        ("Génération de contrats PDF",
         "Défi : remplir un formulaire PDF officiel tout en insérant des pages personnalisées, "
         "avec gestion des polices et des images dont les noms contiennent des apostrophes.",
         "Solution : utilisation de PyMuPDF pour remplir le formulaire existant (wipe + réécriture "
         "précise des zones), et de ReportLab pour générer les pages complémentaires. Les images "
         "avec apostrophe sont chargées via stream=bytes et non via filename."),
        ("Intégrité des signatures de contrats",
         "Défi : garantir qu'un contrat signé ne peut pas être modifié sans que cela soit détecté.",
         "Solution : calcul d'une empreinte SHA-256 combinant le hash du contenu, les données "
         "du signataire et un horodatage ISO. La vérification compare l'empreinte stockée avec "
         "un recalcul à la demande."),
        ("Validation SIRET robuste",
         "Défi : l'algorithme de Luhn acceptait '00000000000000' comme SIRET valide.",
         "Solution : ajout d'un garde explicite avant le calcul de Luhn pour rejeter tout SIRET "
         "ne contenant que des zéros. Ce bug a été détecté grâce aux tests unitaires."),
    ]
    for i, (titre, defi, solution) in enumerate(difficultes):
        e.append(KeepTogether([
            Paragraph(f"<b>Difficulté {i+1} — {titre}</b>", STYLE_SOUS_SECTION),
            Paragraph(f"<font color='#CC3300'><b>Problème :</b></font> {defi[len('Défi : '):]}", STYLE_CORPS),
            Paragraph(f"<font color='#1E7D45'><b>Solution :</b></font> {solution[len('Solution : '):]}", STYLE_CORPS),
            Spacer(1, 0.2*cm),
        ]))

    e.append(Spacer(1, 0.2*cm))
    e.append(note_box("≈ 3 min",
        "Raconter chaque difficulté comme une histoire : 'j'ai d'abord essayé X, ça n'a pas marché parce que Y, alors j'ai fait Z'.",
        "Les difficultés montrent la maturité technique — ne pas les minimiser.",
        "Si le jury pose des questions techniques précises sur une solution, répondre sereinement : toutes les solutions sont dans le code."))
    e.append(PageBreak())
    return e


def section_08():
    e = []
    e.append(titre_section_box("08", "Bilan et compétences BTS SIO développées", "≈ 2 min"))
    e.append(Spacer(1, 0.5*cm))

    e.append(Paragraph("Ce que j'ai appris et développé", STYLE_SECTION))
    e.append(hr())
    e.append(Paragraph(
        "Ce projet m'a permis de développer des compétences transversales couvrant l'intégralité "
        "du référentiel BTS SIO SLAM :",
        STYLE_CORPS))
    e.append(Spacer(1, 0.3*cm))

    competences = [
        ("Conception et modélisation",
         "Analyse du besoin, diagrammes UML (cas d'utilisation, classes, séquences), "
         "modélisation de la base de données avec 10 tables et contraintes de clés étrangères."),
        ("Développement et architecture",
         "Application du pattern MVC sur un projet de ~5 000 lignes, utilisation d'un ORM "
         "professionnel (SQLAlchemy 2.0), développement d'interfaces graphiques Qt (PySide6)."),
        ("Sécurité applicative",
         "Hachage bcrypt, tokens sécurisés, validation stricte des entrées, élimination de "
         "toute injection SQL, intégrité SHA-256 des documents."),
        ("Qualité et tests",
         "155 tests automatisés pytest, isolation via fixtures in-memory, détection et "
         "correction de bugs réels grâce aux tests."),
        ("Conformité réglementaire",
         "Intégration native du RGPD : minimisation, rétention, anonymisation, journaux d'accès."),
        ("Documentation technique",
         "Rédaction du dossier E6, du tableau de synthèse E5, et des annexes officielles."),
    ]
    for comp, desc in competences:
        e.append(Paragraph(f"<b>→ {comp}</b>", STYLE_SOUS_SECTION))
        e.append(Paragraph(desc, STYLE_CORPS))
        e.append(Spacer(1, 0.1*cm))

    e.append(Spacer(1, 0.4*cm))
    e.append(Paragraph("Perspectives d'évolution", STYLE_SOUS_SECTION))
    evolutions = [
        "Version web avec FastAPI + React pour un accès multi-poste",
        "Notifications par e-mail lors des échéances de ressources",
        "Tableau de bord analytique avec graphiques (matplotlib / Chart.js)",
        "Export des journaux d'audit en format CSV / Excel",
        "Intégration d'une API SIRET officielle pour la vérification automatique",
    ]
    for ev in evolutions:
        e.append(Paragraph(f"• {ev}", STYLE_BULLET))
    e.append(Spacer(1, 0.5*cm))

    # Conclusion
    e.append(hr(BLEU_FONCE, 2))
    conclu = Table([[
        Paragraph(
            "En conclusion, GestRes Pro est une application professionnelle, sécurisée et "
            "documentée qui répond à un besoin réel. Ce projet m'a permis de mettre en pratique "
            "l'ensemble des compétences du BTS SIO SLAM dans un contexte exigeant. "
            "Je suis maintenant disponible pour répondre à vos questions.",
            s("Conclu", fontSize=11, fontName="Helvetica",
              textColor=BLANC, leading=18, alignment=TA_CENTER)),
    ]], colWidths=[17*cm])
    conclu.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), BLEU_FONCE),
        ("TOPPADDING",    (0,0), (-1,-1), 20),
        ("BOTTOMPADDING", (0,0), (-1,-1), 20),
        ("LEFTPADDING",   (0,0), (-1,-1), 20),
        ("RIGHTPADDING",  (0,0), (-1,-1), 20),
    ]))
    e.append(conclu)
    e.append(Spacer(1, 0.4*cm))

    e.append(note_box("≈ 2 min",
        "Garder la conclusion courte et directe.",
        "Sourire, regarder le jury, poser les mains à plat sur la table.",
        "Phrase clé finale : 'GestRes Pro est un projet dont je suis fier, car il est le reflet "
        "de ce que j'ai appris pendant ces deux années.'",
        "Attendre les questions sans montrer de stress — toutes les réponses sont dans le code."))
    e.append(PageBreak())
    return e


def page_questions():
    e = []
    t = Table([[
        Paragraph("Questions & Réponses",
                  s("QR", fontSize=30, fontName="Helvetica-Bold",
                    textColor=BLANC, alignment=TA_CENTER, leading=38)),
    ]], colWidths=[17*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), BLEU_FONCE),
        ("TOPPADDING",    (0,0), (-1,-1), 40),
        ("BOTTOMPADDING", (0,0), (-1,-1), 40),
    ]))
    e.append(t)
    e.append(Spacer(1, 0.8*cm))

    e.append(Paragraph("Questions fréquentes et réponses préparées", STYLE_SECTION))
    e.append(hr())

    qa = [
        ("Pourquoi PostgreSQL et pas SQLite ou MySQL ?",
         "PostgreSQL a été choisi pour répondre aux critères E6 : contraintes d'intégrité avancées, "
         "triggers PL/pgSQL (audit automatique, cohérence des statuts), vues métier, fonctions RGPD "
         "intégrées côté base. SQLite a servi en phase de prototypage initial, mais la migration vers "
         "PostgreSQL permet un déploiement multi-poste et une conformité complète. "
         "Les tests conservent SQLite in-memory pour rester rapides et isolés — c'est une stratégie "
         "délibérée, pas un résidu."),
        ("Comment garantissez-vous la conformité RGPD en pratique ?",
         "Trois mécanismes concrets : (1) module maintenance.py avec anonymisation et purge "
         "automatique selon les délais légaux, (2) journal d'audit tracant chaque accès aux "
         "données personnelles, (3) stockage 100% local sans transfert vers des tiers."),
        ("Pourquoi PySide6 et pas une appli web ?",
         "Le cahier des charges demandait une application de bureau autonome, utilisable "
         "sans réseau. PySide6 offre une expérience native, des performances supérieures "
         "pour les opérations sur la base de données, et une distribution simplifiée."),
        ("Comment fonctionne la signature électronique ?",
         "Ce n'est pas une signature cryptographique au sens légal (eIDAS), mais une "
         "empreinte d'intégrité SHA-256 qui garantit que le contrat n'a pas été modifié "
         "après signature. Elle combine le hash du contenu, l'identité du signataire, "
         "et un horodatage ISO non modifiable."),
        ("Avez-vous pensé aux cas d'erreur ?",
         "Oui — chaque contrôleur gère les exceptions SQLAlchemy, les vues affichent des "
         "messages d'erreur explicites, et les 155 tests couvrent les cas limites et les "
         "erreurs intentionnelles (mauvais mot de passe, SIRET invalide, etc.)."),
    ]
    for q, r in qa:
        e.append(KeepTogether([
            Paragraph(f"<b>Q : {q}</b>",
                      s("Q", fontSize=11, fontName="Helvetica-Bold",
                        textColor=BLEU_FONCE, leading=16, spaceBefore=10)),
            Paragraph(f"R : {r}", STYLE_CORPS),
            Spacer(1, 0.3*cm),
        ]))
    return e


# ── Assemblage ────────────────────────────────────────────────────────────────
def build_pdf():
    os.makedirs("docs", exist_ok=True)
    doc = SimpleDocTemplate(
        OUTPUT,
        pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2.2*cm, bottomMargin=2.2*cm,
        title="Présentation GestRes Pro — BTS SIO E6 2026",
        author="CAMARA Ibrahim",
        subject="Présentation orale projet BTS SIO SLAM",
    )

    story = []
    story += page_couverture()
    story += section_01()
    story += section_02()
    story += section_03()
    story += section_04()
    story += section_05()
    story += section_06()
    story += section_07()
    story += section_08()
    story += page_questions()

    doc.build(story)
    print(f"✓ PDF généré : {OUTPUT}")


if __name__ == "__main__":
    build_pdf()
