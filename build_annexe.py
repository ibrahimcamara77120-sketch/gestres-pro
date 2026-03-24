"""
Reconstruction complète de l'Annexe VII-1-B BTS SIO — GestRes Pro
CAMARA Ibrahim — N° 2545812845 — SESSION 2026
"""
import os, shutil
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, Frame, Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY

# ── Polices ──────────────────────────────────────────────────────────────────
TTF = "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"
pdfmetrics.registerFont(TTFont("AU",  TTF))
pdfmetrics.registerFont(TTFont("AUB", TTF))   # on utilise Helvetica-Bold pour le gras

# ── Constantes ───────────────────────────────────────────────────────────────
W, H  = A4                  # 595.28 x 841.89 pt
LM    = 10 * mm             # marge gauche
RM    = W - 10 * mm         # marge droite
TW    = RM - LM             # largeur utile ≈ 538 pt

DOCS  = "/Users/camaraibrahim/PycharmProjects/PythonProject/docs"
OUT   = os.path.join(DOCS, "newannex_rebuilt.pdf")

# ── Helpers de bas niveau ────────────────────────────────────────────────────
def yt(mm_top):           return H - mm_top * mm
def yb(mm_top, h_mm):     return H - (mm_top + h_mm) * mm   # bas du rectangle

def draw_rect(c, x, y_top, w, h_mm, lw=0.5, fill=None):
    c.setLineWidth(lw)
    bot = yb(y_top, h_mm)
    if fill is not None:
        c.setFillColor(fill); c.rect(x, bot, w, h_mm*mm, stroke=1, fill=1); c.setFillColor(colors.black)
    else:
        c.rect(x, bot, w, h_mm*mm, stroke=1, fill=0)

def hl(c, y_mm, x0=None, x1=None, lw=0.4):
    c.setLineWidth(lw); c.line(x0 or LM, yt(y_mm), x1 or RM, yt(y_mm))

def vl(c, x, y0_mm, y1_mm, lw=0.4):
    c.setLineWidth(lw); c.line(x, yt(y0_mm), x, yt(y1_mm))

def T(c, x, y_mm, s, fn="Helvetica", sz=8):
    c.setFont(fn, sz); c.drawString(x, yt(y_mm), s)

def TC(c, y_mm, s, fn="Helvetica", sz=8):
    c.setFont(fn, sz); c.drawCentredString(W/2, yt(y_mm), s)

def TR(c, x, y_mm, s, fn="Helvetica", sz=8):
    c.setFont(fn, sz); c.drawRightString(x, yt(y_mm), s)

def checkbox(c, x, y_mm, checked=False, sz=5.5):
    c.setLineWidth(0.5); y = yt(y_mm)
    c.rect(x, y - 1, sz, sz, stroke=1, fill=0)
    if checked:
        c.setLineWidth(1.0)
        c.line(x+0.5, y+sz-2.5, x+sz-0.5, y-0.5)
        c.line(x+0.5, y-0.5, x+sz-0.5, y+sz-2.5)
        c.setLineWidth(0.5)

def flow(c, x, y_top, w_pt, h_mm, text, fn="AU", sz=7.5, ld=9.5, pad=1.5, color=colors.black):
    """Texte enroulé dans une zone rectangulaire."""
    style = ParagraphStyle("s", fontName=fn, fontSize=sz, leading=ld,
                           textColor=color, spaceAfter=2, spaceBefore=0)
    frame = Frame(x + pad*mm, yb(y_top, h_mm) + pad*mm,
                  w_pt - 2*pad*mm, h_mm*mm - 2*pad*mm,
                  leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    story = []
    for line in text.strip().split("\n"):
        line = line.replace("&","&amp;").replace("<","&lt;")
        if line.strip():
            story.append(Paragraph(line, style))
        else:
            story.append(Spacer(1, 3))
    frame.addFromList(story, c)

def labeled_box(c, y_top, h_mm, label, content, fn_c="AU", sz_c=7.5, ld_c=9.5, lw=0.7):
    """Encadré avec label en italique en haut + contenu enroulé."""
    draw_rect(c, LM, y_top, TW, h_mm, lw=lw)
    # Ligne séparatrice label/contenu (à 5mm du haut)
    hl(c, y_top + 5, x0=LM, x1=RM, lw=0.4)
    # Label
    T(c, LM + 1.5*mm, y_top + 3.8, label, fn="Helvetica-Oblique", sz=7)
    # Contenu
    flow(c, LM, y_top + 5, TW, h_mm - 5, content, fn=fn_c, sz=sz_c, ld=ld_c)


# ════════════════════════════════════════════════════════════════════════════
# PAGE 1 — RECTO
# ════════════════════════════════════════════════════════════════════════════
c = canvas.Canvas(OUT, pagesize=A4)

# ── En-tête encadré ─────────────────────────────────────────────────────────
draw_rect(c, LM, 10, TW, 10, lw=1.0, fill=colors.Color(0.92,0.92,0.92))
T(c, LM + 3*mm, 17, "BTS SERVICES INFORMATIQUES AUX ORGANISATIONS",
  fn="Helvetica-Bold", sz=9)
TR(c, RM - 3*mm, 17, "SESSION 2026", fn="Helvetica-Bold", sz=9)

# ── Sous-titres formulaire ───────────────────────────────────────────────────
T(c, LM, 23.5,
  "ANNEXE VII-1-B : Fiche descriptive de réalisation professionnelle (recto)",
  fn="Helvetica", sz=8)
T(c, LM, 28,
  "Épreuve E6 - Conception et développement d'applications (option SLAM)",
  fn="Helvetica-Oblique", sz=7.5)

# ── Titre section ────────────────────────────────────────────────────────────
hl(c, 30.5, lw=0.8)
TC(c, 34.5, "DESCRIPTION D'UNE RÉALISATION PROFESSIONNELLE",
   fn="Helvetica-Bold", sz=9)
hl(c, 36, lw=0.8)

# ── Ligne identité (N° réal | Nom | N° candidat) ────────────────────────────
draw_rect(c, LM, 37, TW, 8, lw=0.6)
vl(c, LM + TW*0.20, 37, 45)
vl(c, LM + TW*0.60, 37, 45)
T(c, LM+2*mm, 42, "N° réalisation :  1", sz=7.5)
T(c, LM + TW*0.20 + 2*mm, 42, "Nom, prénom :  CAMARA Ibrahim", fn="AU", sz=7.5)
T(c, LM + TW*0.60 + 2*mm, 42, "N° candidat :  2545812845", sz=7.5)

# ── Ligne épreuve / CCF / date ───────────────────────────────────────────────
draw_rect(c, LM, 45, TW, 8, lw=0.6)
vl(c, LM + TW*0.38, 45, 53)
vl(c, LM + TW*0.72, 45, 53)

checkbox(c, LM + 2*mm, 50)
T(c, LM + 9*mm, 50, "Épreuve ponctuelle", sz=7.5)

checkbox(c, LM + TW*0.38 + 2*mm, 50, checked=True)
T(c, LM + TW*0.38 + 9*mm, 50, "Contrôle en cours de formation (CCF)", fn="AU", sz=7.5)

T(c, LM + TW*0.72 + 2*mm, 50, "Date :", sz=7.5)
T(c, LM + TW*0.72 + 13*mm, 50, "24 / 03 / 2026", sz=7.5)

# ── Organisation ────────────────────────────────────────────────────────────
labeled_box(c, 53, 11,
    "Organisation support de la réalisation professionnelle",
    "Digital School of Paris - IEF2I",
    fn_c="AU", sz_c=9, ld_c=11)

# ── Intitulé ─────────────────────────────────────────────────────────────────
labeled_box(c, 64, 12,
    "Intitulé de la réalisation professionnelle",
    "GestRes Pro — Application desktop de gestion des ressources d'entreprise",
    fn_c="AU", sz_c=9, ld_c=11)

# ── Période / Lieu / Modalité ────────────────────────────────────────────────
draw_rect(c, LM, 76, TW, 9, lw=0.6)
vl(c, LM + TW*0.42, 76, 85)
vl(c, LM + TW*0.72, 76, 85)

T(c, LM+2*mm, 81.5, "Période de réalisation :", sz=7)
T(c, LM+33*mm, 81.5, "09/2024 au 05/2026", fn="AU", sz=7.5)

T(c, LM + TW*0.42 + 2*mm, 81.5, "Lieu :", sz=7)
T(c, LM + TW*0.42 + 10*mm, 81.5, "Digital School de Paris - IEF2I", fn="AU", sz=7)

T(c, LM + TW*0.72 + 2*mm, 80, "Modalité :", sz=7)
checkbox(c, LM + TW*0.72 + 2*mm, 84, checked=True)
T(c, LM + TW*0.72 + 9.5*mm, 84, "Seul(e)", sz=7)
checkbox(c, LM + TW*0.72 + 22*mm, 84)
T(c, LM + TW*0.72 + 29.5*mm, 84, "En équipe", sz=7)

# ── Compétences ──────────────────────────────────────────────────────────────
draw_rect(c, LM, 85, TW, 18, lw=0.7)
hl(c, 90, x0=LM, x1=RM, lw=0.4)
T(c, LM+1.5*mm, 88.8, "Compétences travaillées", fn="Helvetica-Oblique", sz=7)

checkbox(c, LM+2*mm, 95, checked=True)
T(c, LM+9.5*mm, 95, "Concevoir et développer une solution applicative", fn="AU", sz=7.5)

checkbox(c, LM+2*mm, 99, checked=True)
T(c, LM+9.5*mm, 99, "Assurer la maintenance corrective ou évolutive d'une solution applicative", fn="AU", sz=7.5)

checkbox(c, LM+2*mm, 103, checked=True)
T(c, LM+9.5*mm, 103, "Gérer les données", fn="AU", sz=7.5)

# ── Conditions de réalisation ────────────────────────────────────────────────
labeled_box(c, 103, 40,
    "Conditions de réalisation\u00b9  (ressources fournies, résultats attendus)",
    "Contexte : Les entreprises gèrent leurs ressources (matériel IT, comptes numériques, véhicules, badges) "
    "via Excel ou papier, engendrant perte de traçabilité et non-conformité RGPD. GestRes Pro centralise, "
    "sécurise et trace le cycle de vie complet.\n"
    "\n"
    "Ressources fournies : Python 3.14, PySide6 ≥ 6.6.0, SQLAlchemy 2.0 / SQLite 3, bcrypt 4.1 (cost 12), "
    "ReportLab 4.0, python-dateutil, cahier des charges (entretiens), documentation RGPD/CNIL, "
    "PyCharm Professional, Git/GitHub.\n"
    "\n"
    "Résultats attendus : App desktop MVC — auth bcrypt+SHA-256 (sessions 8h) — 3 rôles (permissions JSON) — "
    "CRUD + validation SIRET (Luhn) — cycle de vie 4 statuts — contrats PDF + SHA-256 verify_integrity() — "
    "logs d'audit (old/new JSON) — conformité RGPD — 155 tests pytest.",
    sz_c=7.5, ld_c=9.5)

# ── Description des ressources ───────────────────────────────────────────────
labeled_box(c, 143, 53,
    "Description des ressources documentaires, matérielles et logicielles utilisées\u00b2",
    "Langages & frameworks : Python 3.14 — PySide6 ≥ 6.6.0 / Qt for Python (GUI desktop native)\n"
    "ORM & BDD : SQLAlchemy ≥ 2.0.0 (zéro SQL brut) — SQLite 3 (database.db local)\n"
    "Sécurité : bcrypt ≥ 4.1.0 (rounds=12) — SHA-256 (tokens session + intégrité contrats) — "
    "secrets.token_hex(32) — validate_siret Luhn 14 chiffres (rejet SIRET nuls, bug corrigé 03/2026)\n"
    "PDF : reportlab ≥ 4.0.0 (SimpleDocTemplate A4, Paragraph, Table, HRFlowable)\n"
    "Tests : pytest — 3 fichiers, 155 tests — conftest.py (SQLite in-memory, isolation totale, "
    "database.db jamais modifié pendant pytest)\n"
    "Environnement : PyCharm Professional — Git/GitHub — macOS Darwin 24.1.0 (Python 3.14)\n"
    "Packaging : PyInstaller → livrable .app autonome macOS\n"
    "Documentation : docs/ du dépôt — portfolio : https://ib-camara.vercel.app/",
    sz_c=7.5, ld_c=9.5)

# ── Modalités d'accès ────────────────────────────────────────────────────────
labeled_box(c, 196, 35,
    "Modalités d'accès aux productions\u00b3 et à leur documentation\u2074",
    "Lancement : source .venv/bin/activate && python main.py\n"
    "(Super Admin créé automatiquement au 1er démarrage si aucun compte n'existe)\n"
    "\n"
    "Tests : python -m pytest tests/ -v   (155 tests, SQLite in-memory, isolation totale)\n"
    "\n"
    "Code source & docs : dépôt GitHub (en cours de mise en ligne)\n"
    "Portfolio : https://ib-camara.vercel.app/\n"
    "Livrable : .app macOS autonome via PyInstaller — dossier /docs/ du dépôt",
    sz_c=7.5, ld_c=9.5)

# ── Notes de bas de page ─────────────────────────────────────────────────────
hl(c, 231, lw=0.6)
fn_style = ParagraphStyle("fn", fontName="AU", fontSize=6, leading=8, spaceAfter=2)
fn_frame = Frame(LM, yb(231, 57), TW, 57*mm,
                 leftPadding=0, rightPadding=0, topPadding=2, bottomPadding=0)
footnotes = [
    Paragraph(
        "\u00b9 En référence aux conditions de réalisation et ressources nécessaires du bloc "
        "« Conception et développement d'applications » prévues dans le référentiel de certification du BTS SIO.",
        fn_style),
    Spacer(1, 2),
    Paragraph(
        "\u00b2 Les réalisations professionnelles sont élaborées dans un environnement technologique "
        "conforme à l'annexe II.E du référentiel du BTS SIO.",
        fn_style),
    Spacer(1, 2),
    Paragraph(
        "\u00b3 Conformément au référentiel du BTS SIO : « Dans tous les cas, les candidats doivent se munir "
        "des outils et ressources techniques nécessaires au déroulement de l'épreuve. Ils sont seuls "
        "responsables de la disponibilité et de la mise en œuvre de ces outils et ressources. La circulaire "
        "nationale d'organisation précise les conditions matérielles de déroulement des interrogations et les "
        "pénalités à appliquer aux candidats qui ne se seraient pas munis des éléments nécessaires. »",
        fn_style),
    Spacer(1, 2),
    Paragraph(
        "\u2074 Lien vers la documentation complète, précisant et décrivant, si cela n'a été fait au verso "
        "de la fiche, la réalisation professionnelle, par exemples service fourni par la réalisation, "
        "interfaces utilisateurs, description des classes ou de la base de données.",
        fn_style),
]
fn_frame.addFromList(footnotes, c)

# Numéro de page
TC(c, 289, "1", fn="Helvetica", sz=8)

c.showPage()

# ════════════════════════════════════════════════════════════════════════════
# PAGE 2 — VERSO (descriptif principal)
# ════════════════════════════════════════════════════════════════════════════

# En-tête
draw_rect(c, LM, 10, TW, 10, lw=1.0, fill=colors.Color(0.92,0.92,0.92))
T(c, LM + 3*mm, 17, "BTS SERVICES INFORMATIQUES AUX ORGANISATIONS",
  fn="Helvetica-Bold", sz=9)
TR(c, RM - 3*mm, 17, "SESSION 2026", fn="Helvetica-Bold", sz=9)

T(c, LM, 23.5,
  "ANNEXE VII-1-B : Fiche descriptive de réalisation professionnelle (verso, éventuellement pages suivantes)",
  fn="Helvetica", sz=8)
T(c, LM, 28,
  "Épreuve E6 - Conception et développement d'applications (option SLAM)",
  fn="Helvetica-Oblique", sz=7.5)

hl(c, 30, lw=0.8)

# Label section descriptif
draw_rect(c, LM, 30, TW, 6, lw=0.5, fill=colors.Color(0.95,0.95,0.95))
T(c, LM+2*mm, 35,
  "Descriptif de la réalisation professionnelle, y compris les productions réalisées et schémas explicatifs",
  fn="Helvetica-Oblique", sz=7.5)

# ── Contenu verso ────────────────────────────────────────────────────────────
# Introduction
labeled_box(c, 36, 20,
    "Présentation générale",
    "GestRes Pro est une application desktop Python 3.14 / PySide6 centralisant la gestion des ressources "
    "d'entreprise (matériel informatique, comptes numériques, véhicules, badges d'accès) avec 3 niveaux de "
    "rôles (Super Admin, Admin, Employé), génération de contrats PDF signés électroniquement et journal "
    "d'audit conforme RGPD.",
    sz_c=7.8, ld_c=10)

# Architecture MVC
labeled_box(c, 56, 88,
    "Architecture MVC",
    "src/models/  (10 modèles SQLAlchemy)\n"
    "  · user.py          — User [email, password_hash bcrypt, is_active, last_login]\n"
    "                        + Role [name, permissions JSON]\n"
    "  · company.py       — Company [nom, SIRET Luhn, adresse, is_active]\n"
    "  · resource_type.py — ResourceType [custom_fields JSON par entreprise]\n"
    "  · resource.py      — Resource [statut 4 états, serial_number unique, custom_data JSON,\n"
    "                        is_available, current_assignment]\n"
    "  · assignment.py    — Assignment [resource_id, user_id, assigned_by,\n"
    "                        start_date, end_date, duration_days, status]\n"
    "  · contract.py      — Contract [content_hash SHA-256, sign(),\n"
    "                        verify_integrity(), pdf_path, signed_at, signature_hash]\n"
    "  · audit_log.py     — AuditLog [action, table_name, record_id,\n"
    "                        old_values JSON, new_values JSON, ip_address]\n"
    "                        + Session [token_hash SHA-256, expires_at = now+8h]\n"
    "\n"
    "src/controllers/  (6 contrôleurs)\n"
    "  · auth_controller       — login / logout / create_user / change_password /\n"
    "                            create_initial_super_admin\n"
    "                            (normalisation email lower().strip() ici, pas dans le modèle)\n"
    "  · company_controller    — CRUD entreprises + validation SIRET (algorithme Luhn 14 chiffres)\n"
    "  · resource_controller   — CRUD ressources + types, gestion des statuts\n"
    "  · assignment_controller — create_assignment / close_assignment / cancel_assignment\n"
    "  · contract_controller   — generate / sign / verify_contract / export_pdf (ReportLab)\n"
    "  · user_controller       — CRUD utilisateurs + rôles\n"
    "\n"
    "src/views/  (10 vues PySide6)\n"
    "  login, main_window, dashboard, users, companies, resources,\n"
    "  assignments, contracts, logs + widgets/data_table.py (tableau paginé réutilisable)\n"
    "\n"
    "src/utils/\n"
    "  · security.py    — hash_password, verify_password, generate_token, hash_token SHA-256,\n"
    "                     validate_password_strength, validate_email, validate_siret Luhn,\n"
    "                     sanitize_input (strip + suppression caractères de contrôle)\n"
    "  · backup.py      — sauvegardes automatiques de database.db\n"
    "  · maintenance.py — purge RGPD : données expirées + sessions périmées\n"
    "\n"
    "config.py : BCRYPT_ROUNDS=12 · SESSION_DURATION_HOURS=8 · PASSWORD_MIN_LENGTH=8\n"
    "            DEFAULT_RETENTION_DAYS=1095 (3 ans) · AUDIT_LOG_RETENTION_DAYS=1825 (5 ans)",
    sz_c=7.2, ld_c=9)

# Tables
labeled_box(c, 144, 75,
    "Tables principales (10 tables SQLite)",
    "roles          : super_admin=[\"all\"], admin=[\"view_resources\",\"manage_resources\",\"view_users\",\n"
    "                 \"manage_users\",\"view_logs\",\"generate_contracts\",\"view_assignments\",\n"
    "                 \"manage_assignments\"], employee=[\"view_own_resources\",\"view_own_assignments\",\n"
    "                 \"sign_contracts\",\"view_own_history\"]   →  1:N vers users\n"
    "users          : email (lower+strip), password_hash bcrypt, is_active, last_login\n"
    "                 →  N:1 vers roles / companies\n"
    "companies      : nom, SIRET (Luhn 14 chiffres), adresse   →  1:N vers users/resource_types/resources\n"
    "resource_types : custom_fields JSON par entreprise   →  1:N vers resources\n"
    "resources      : statut (available/assigned/maintenance/retired), serial_number unique,\n"
    "                 custom_data JSON, is_available   →  1:N vers assignments\n"
    "assignments    : resource_id, user_id, assigned_by, start_date, end_date, duration_days\n"
    "                 →  1:N vers contracts\n"
    "contracts      : content_hash SHA-256, is_signed, signed_at, signature_hash, pdf_path\n"
    "                 →  N:1 vers assignments\n"
    "audit_logs     : action, table_name, record_id, old_values JSON, new_values JSON, ip_address\n"
    "                 →  N:1 vers users\n"
    "sessions       : token_hash = SHA-256(secrets.token_hex(32)), expires_at = now + 8h\n"
    "                 →  N:1 vers users",
    sz_c=7.2, ld_c=9)

TC(c, 289, "2", fn="Helvetica", sz=8)
c.showPage()

# ════════════════════════════════════════════════════════════════════════════
# PAGE 3 — Fonctionnalités a → h
# ════════════════════════════════════════════════════════════════════════════

draw_rect(c, LM, 10, TW, 10, lw=1.0, fill=colors.Color(0.92,0.92,0.92))
T(c, LM + 3*mm, 17, "BTS SERVICES INFORMATIQUES AUX ORGANISATIONS",
  fn="Helvetica-Bold", sz=9)
TR(c, RM - 3*mm, 17, "SESSION 2026", fn="Helvetica-Bold", sz=9)
T(c, LM, 23.5, "ANNEXE VII-1-B — CAMARA Ibrahim — N° 2545812845 — (suite page 3 / fonctionnalités)", sz=8)
hl(c, 26, lw=0.6)

labeled_box(c, 26, 257,
    "Fonctionnalités de l'application",
    "a) Authentification & sessions\n"
    "   login() vérifie email (lower+strip) + bcrypt  →  génère token secrets.token_hex(32) haché SHA-256,\n"
    "   expiration 8h stockée en base. LOGIN / LOGIN_FAILED tracés dans audit_logs.\n"
    "   Déconnexion propre : suppression token en base + log LOGOUT.\n"
    "   Méthodes : is_super_admin(), is_admin(), has_permission().\n"
    "\n"
    "b) Rôles & permissions\n"
    "   Super Admin [\"all\"] → accès total.   Admin → 8 permissions.   Employé → 4 permissions.\n"
    "   Vérification via Role.has_permission() : \"all\" in perms OR permission in perms.\n"
    "\n"
    "c) Ressources & types\n"
    "   Types personnalisables par entreprise (custom_fields JSON). CRUD : sanitize_input() sur toutes les\n"
    "   entrées, serial_number unique vérifié. Suppression logique (status→retired, bloquée si affectée).\n"
    "   Cycle de vie : available → assigned → maintenance → retired. Propriété current_assignment.\n"
    "\n"
    "d) Affectations\n"
    "   Vérification resource.is_available avant création. assigned_by toujours tracé.\n"
    "   close_assignment → returned + ressource→available.\n"
    "   cancel_assignment → cancelled + ressource→available.\n"
    "   Calcul auto duration_days. Filtrage par statut / utilisateur / entreprise.\n"
    "\n"
    "e) Contrats PDF\n"
    "   generate_contract() construit le contenu texte + content_hash = SHA-256.\n"
    "   verify_integrity() recompute et compare le hash.\n"
    "   sign() : signature_hash = SHA-256(content_hash:signer_data:signed_at.isoformat()).\n"
    "   export_pdf() ReportLab A4 : sections, tableau des parties, pied de page avec hash[:16].\n"
    "   Signature bloquée si l'intégrité du contrat est compromise.\n"
    "\n"
    "f) Logs d'audit\n"
    "   AuditLog.log(action, user_id, table_name, record_id, old_values JSON, new_values JSON, ip_address)\n"
    "   appelé sur chaque opération.\n"
    "   Actions : CREATE / UPDATE / DELETE / LOGIN / LOGIN_FAILED / LOGOUT / PASSWORD_CHANGE.\n"
    "   Interface filtrable par date, utilisateur ou action. Export des rapports.\n"
    "\n"
    "g) Sécurité & RGPD\n"
    "   SQLAlchemy ORM exclusivement (zéro injection SQL). sanitize_input() sur toutes les entrées.\n"
    "   validate_siret : Luhn 14 chiffres + rejet des SIRET nuls\n"
    "   (bug corrigé 03/2026 : SIRET «00000000000000» passait 0 % 10 = 0 — garde ajoutée).\n"
    "   Rétention : 3 ans données (1095 j), 5 ans logs (1825 j). Purge auto (maintenance.py).\n"
    "   Sauvegardes automatiques (backup.py). Anonymisation (droit à l'oubli). Export données personnelles.\n"
    "\n"
    "h) Tests — 155 pytest\n"
    "   · test_models.py       : unitaires — 10 modèles, relations, propriétés, SHA-256\n"
    "   · test_controllers.py  : intégration — connexion, affectation, génération contrat, rôles\n"
    "   · test_security.py     : hash_password, verify_password, validate_password/email/siret,\n"
    "                            sanitize_input, generate_token\n"
    "   · conftest.py          : isolation totale via SQLite in-memory — patche base_module.engine\n"
    "                            ET les références directes engine importées dans les modules de test\n"
    "                            → database.db jamais modifié pendant une session pytest.",
    sz_c=7.4, ld_c=9.3)

TC(c, 289, "3", fn="Helvetica", sz=8)
c.showPage()

# ════════════════════════════════════════════════════════════════════════════
# PAGE 4 — Données de test
# ════════════════════════════════════════════════════════════════════════════

draw_rect(c, LM, 10, TW, 10, lw=1.0, fill=colors.Color(0.92,0.92,0.92))
T(c, LM + 3*mm, 17, "BTS SERVICES INFORMATIQUES AUX ORGANISATIONS",
  fn="Helvetica-Bold", sz=9)
TR(c, RM - 3*mm, 17, "SESSION 2026", fn="Helvetica-Bold", sz=9)
T(c, LM, 23.5, "ANNEXE VII-1-B — CAMARA Ibrahim — N° 2545812845 — (suite page 4 / données de test)", sz=8)
hl(c, 26, lw=0.6)

labeled_box(c, 26, 120,
    "Données de test — [SOCIÉTÉ TEST] CleanPro Services (société de nettoyage fictive)",
    "Objectif : valider l'application sur un cas métier réaliste avant la présentation.\n"
    "\n"
    "Société      : [SOCIÉTÉ TEST] CleanPro Services\n"
    "               SIRET : 732 829 320 00074 — 12 rue des Lilas, Paris 13e\n"
    "\n"
    "Utilisateurs (5) :\n"
    "  · Marie Dupont      — Responsable d'agence (rôle : admin)\n"
    "  · Karim Benali      — Agent de nettoyage (rôle : employee)\n"
    "  · Fatou Diallo      — Agente de nettoyage (rôle : employee)\n"
    "  · Lucas Martin      — Agent polyvalent (rôle : employee)\n"
    "  · Amina Traoré      — Agente de nettoyage (rôle : employee)\n"
    "\n"
    "Types de ressources (7) :\n"
    "  Balai · Serpillère · Essuie-tout · Seau & Chariot · Produit nettoyant ·\n"
    "  Équipement de protection individuelle (EPI) · Aspirateur\n"
    "\n"
    "Ressources matérielles (20) :\n"
    "  Balais à franges/brosse/plat microfibre, serpillères coton/microfibre, têtes de vadrouille,\n"
    "  chariots de nettoyage avec essoreuse, seaux double compartiment, rouleaux essuie-tout,\n"
    "  détergents, désinfectants, dégraissants, gants nitrile M/L, tablier imperméable,\n"
    "  lunettes de protection, aspirateurs industriels.\n"
    "\n"
    "Affectations actives (11) :\n"
    "  Chaque agent dispose de ses ressources attitrées avec date de début et notes de remise.\n"
    "\n"
    "Contrats (11) :\n"
    "  Un contrat numérique généré, signé électroniquement et exporté en PDF pour chaque\n"
    "  affectation active — vérification d'intégrité SHA-256 sur chaque contrat.\n"
    "\n"
    "Script : seed_test_company.py — génère l'ensemble des données en une seule commande.",
    sz_c=7.8, ld_c=10)

# Identifiants de connexion
labeled_box(c, 146, 40,
    "Identifiants de connexion (données de test)",
    "Super Admin  :  superadmin@gestres.test    /  SuperAdmin1!\n"
    "Admin        :  responsable@cleanpro.test  /  Responsable1!\n"
    "Employé 1    :  employe1@cleanpro.test     /  Employe001!\n"
    "Employé 2    :  employe2@cleanpro.test     /  Employe002!\n"
    "Employé 3    :  employe3@cleanpro.test     /  Employe003!\n"
    "Employé 4    :  employe4@cleanpro.test     /  Employe004!",
    sz_c=8, ld_c=10.5)

TC(c, 289, "4", fn="Helvetica", sz=8)
c.showPage()

# ════════════════════════════════════════════════════════════════════════════
# PAGE 5 — Capture d'écran
# ════════════════════════════════════════════════════════════════════════════
import fitz as _fitz
_src = _fitz.open(os.path.join(DOCS, "newannex.pdf"))
# Chercher la page avec la capture (dernière page)
_sc_page = _src[_src.page_count - 1]
_sc_pix  = _sc_page.get_pixmap(matrix=_fitz.Matrix(1.5, 1.5), alpha=False)
_sc_bytes = _sc_pix.tobytes("png")
_src.close()

c.drawImage.__doc__  # check available
from reportlab.lib.utils import ImageReader
from io import BytesIO
_img_reader = ImageReader(BytesIO(_sc_bytes))
c.drawImage(_img_reader, 0, 0, W, H, preserveAspectRatio=True, anchor='c')

# En-tête léger
c.setFont("Helvetica", 7); c.setFillColor(colors.white)
c.drawString(LM, H - 8*mm, "ANNEXE VII-1-B — GestRes Pro — CAMARA Ibrahim — Capture d'écran")
c.setFillColor(colors.black)
TC(c, 289, "5", fn="Helvetica", sz=8)
c.showPage()

# ── Sauvegarder ──────────────────────────────────────────────────────────────
c.save()
shutil.move(OUT, os.path.join(DOCS, "newannex.pdf"))
print("✅  newannex.pdf reconstruit — 5 pages")
