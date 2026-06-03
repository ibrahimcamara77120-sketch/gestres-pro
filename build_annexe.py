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

def labeled_box(c, y_top, h_mm, label, content, fn_c="AU", sz_c=7.5, ld_c=9.5, lw=0.7,
                x=None, w=None):
    """Encadré avec label en italique en haut + contenu enroulé."""
    _x = x if x is not None else LM
    _w = w if w is not None else TW
    draw_rect(c, _x, y_top, _w, h_mm, lw=lw)
    # Ligne séparatrice label/contenu (à 5mm du haut)
    hl(c, y_top + 5, x0=_x, x1=_x + _w, lw=0.4)
    # Label
    T(c, _x + 1.5*mm, y_top + 3.8, label, fn="Helvetica-Oblique", sz=7)
    # Contenu
    flow(c, _x, y_top + 5, _w, h_mm - 5, content, fn=fn_c, sz=sz_c, ld=ld_c)


# ════════════════════════════════════════════════════════════════════════════
# PAGE 1 — RECTO  (calé sur coordonnées Annexe 9 officielle)
# ════════════════════════════════════════════════════════════════════════════
c = canvas.Canvas(OUT, pagesize=A4)

# Constantes formulaire officiel (pt)
LM_F = 49          # bord gauche
RM_F = 546         # bord droit
TW_F = RM_F - LM_F  # 497 pt

# Positions y (mm depuis le haut) converties depuis pt ÷ 2.835
YH1  = 19.4   # haut en-tête
YH2  = 41.5   # bas en-tête
YF1  = 43.9   # 1ère ligne formulaire
YR1  = 54.2   # après "DESCRIPTION / N° réalisation"
YR2  = 62.3   # après "Nom / N° candidat"
YR3  = 71.4   # après "Épreuve / CCF / Date"
YR4  = 80.7   # après "Organisation"
YR5  = 89.8   # après "Intitulé"
YR6  = 103.5  # après "Période / Lieu / Modalité"
YR7  = 124.7  # après "Compétences"
YR8  = 154.0  # après "Conditions de réalisation"
YR9  = 211.2  # après "Description des ressources"
YR10 = 231.6  # bas zone formulaire (après "Modalités")
YFN  = 237.7  # ligne séparatrice notes bas de page

# ── En-tête grisé ────────────────────────────────────────────────────────
draw_rect(c, LM_F, YH1, TW_F, YH2 - YH1, lw=0.8,
          fill=colors.Color(0.92, 0.92, 0.92))
TC(c, YH1 + 7,  "BTS SERVICES INFORMATIQUES AUX ORGANISATIONS",
   fn="Helvetica-Bold", sz=9)
TR(c, RM_F - 2*mm, YH1 + 7, "SESSION 2026", fn="Helvetica-Bold", sz=9)
TC(c, YH1 + 15,
   "ANNEXE VII-1-B : Fiche descriptive de réalisation professionnelle (recto)",
   fn="Helvetica", sz=8)
TC(c, YH1 + 21,
   "Épreuve E6 - Conception et développement d'applications (option SLAM)",
   fn="Helvetica-Oblique", sz=7.5)

# ── Bordures verticales du formulaire ─────────────────────────────────────
vl(c, LM_F, YF1, YR10)
vl(c, RM_F, YF1, YR10)

# ── Lignes horizontales (coordonnées exactes Annexe 9) ────────────────────
for _y in [YF1, YR1, YR2, YR3, YR4, YR5, YR6, YR7, YR8, YR9, YR10]:
    hl(c, _y, x0=LM_F, x1=RM_F, lw=0.6)

# ── Diviseurs verticaux ───────────────────────────────────────────────────
vl(c, 445.5, YF1, YR1)      # N° réalisation
vl(c, 410.5, YR1, YR3)      # Nom / N° candidat

# ── Rangée 1 : DESCRIPTION / N° réalisation ───────────────────────────────
_ym = YF1 + (YR1 - YF1) / 2 + 1.5
TC(c, _ym, "DESCRIPTION D'UNE RÉALISATION PROFESSIONNELLE",
   fn="Helvetica-Bold", sz=8)
T(c, 448, _ym, "N° réalisation :  1", fn="AU", sz=7.5)

# ── Rangée 2 : Nom / N° candidat ──────────────────────────────────────────
_ym = YR1 + (YR2 - YR1) / 2 + 1.5
T(c, LM_F + 2*mm, _ym, "Nom, prénom :  CAMARA Ibrahim", fn="AU", sz=8)
T(c, 413, _ym, "N° candidat :  2545812845", fn="AU", sz=8)

# ── Rangée 3 : Épreuve / CCF / Date ──────────────────────────────────────
_x1 = LM_F + TW_F * 0.38
_x2 = LM_F + TW_F * 0.72
vl(c, _x1, YR2, YR3)
vl(c, _x2, YR2, YR3)
_ym = YR2 + (YR3 - YR2) / 2 + 1.5
checkbox(c, LM_F + 2*mm, _ym)
T(c, LM_F + 9*mm, _ym, "Épreuve ponctuelle", sz=7.5)
checkbox(c, _x1 + 2*mm, _ym, checked=True)
T(c, _x1 + 9*mm, _ym, "Contrôle en cours de formation (CCF)", fn="AU", sz=7.5)
T(c, _x2 + 2*mm, _ym, "Date :  24 / 03 / 2026", fn="AU", sz=7.5)

# ── Rangée 4 : Organisation ───────────────────────────────────────────────
T(c, LM_F + 1.5*mm, YR3 + 3.5,
  "Organisation support de la réalisation professionnelle",
  fn="Helvetica-Oblique", sz=7)
T(c, LM_F + 2*mm, YR3 + 7.5, "Digital School de Paris - IEF2I", fn="AU", sz=8.5)

# ── Rangée 5 : Intitulé ───────────────────────────────────────────────────
T(c, LM_F + 1.5*mm, YR4 + 3.5,
  "Intitulé de la réalisation professionnelle",
  fn="Helvetica-Oblique", sz=7)
T(c, LM_F + 2*mm, YR4 + 7.5,
  "GestRes Pro \u2014 Application desktop de gestion des ressources d\u2019entreprise",
  fn="AU", sz=8.5)

# ── Rangée 6 : Période / Lieu / Modalité ─────────────────────────────────
_xp = LM_F + TW_F * 0.42
_xm = LM_F + TW_F * 0.72
vl(c, _xp, YR5, YR6)
vl(c, _xm, YR5, YR6)
T(c, LM_F + 1.5*mm, YR5 + 3.5, "Période de réalisation :", fn="Helvetica-Oblique", sz=7)
T(c, LM_F + 2*mm,   YR5 + 9,   "09 / 2024  au  05 / 2026", fn="AU", sz=7.5)
T(c, _xp + 1.5*mm,  YR5 + 3.5, "Lieu :", fn="Helvetica-Oblique", sz=7)
T(c, _xp + 2*mm,    YR5 + 9,   "Digital School de Paris - IEF2I", fn="AU", sz=7)
T(c, _xm + 1.5*mm,  YR5 + 3,   "Modalité :", fn="Helvetica-Oblique", sz=7)
checkbox(c, _xm + 2*mm, YR5 + 9, checked=True)
T(c, _xm + 9*mm,    YR5 + 9,   "Seul(e)", sz=7)
checkbox(c, _xm + 22*mm, YR5 + 9)
T(c, _xm + 29*mm,   YR5 + 9,   "En équipe", sz=7)

# ── Rangée 7 : Compétences ────────────────────────────────────────────────
hl(c, YR6 + 5, x0=LM_F, x1=RM_F, lw=0.4)
T(c, LM_F + 1.5*mm, YR6 + 3.5, "Compétences travaillées",
  fn="Helvetica-Oblique", sz=7)
_yc = YR6 + 9
checkbox(c, LM_F + 2*mm, _yc, checked=True)
T(c, LM_F + 9*mm, _yc, "Concevoir et développer une solution applicative",
  fn="AU", sz=7.5)
_yc += 5
checkbox(c, LM_F + 2*mm, _yc, checked=True)
T(c, LM_F + 9*mm, _yc,
  "Assurer la maintenance corrective ou évolutive d\u2019une solution applicative",
  fn="AU", sz=7.5)
_yc += 5
checkbox(c, LM_F + 2*mm, _yc, checked=True)
T(c, LM_F + 9*mm, _yc, "Gérer les données", fn="AU", sz=7.5)

# ── Rangée 8 : Conditions de réalisation ─────────────────────────────────
labeled_box(c, YR7, YR8 - YR7,
    "Conditions de r\u00e9alisation\u00b9  (ressources fournies, r\u00e9sultats attendus)",
    "Contexte : Les entreprises g\u00e8rent leurs ressources (mat\u00e9riel IT, comptes, v\u00e9hicules, "
    "badges) via Excel ou papier, engendrant perte de tra\u00e7abilit\u00e9 et non-conformit\u00e9 RGPD. "
    "GestRes Pro centralise, s\u00e9curise et trace le cycle de vie complet.\n"
    "Ressources : Python 3.14 \u00b7 PySide6 \u2265 6.6.0 \u00b7 SQLAlchemy 2.0 / PostgreSQL \u00b7 "
    "bcrypt 4.1 \u00b7 ReportLab 4.0 \u00b7 PyCharm Professional \u00b7 Git/GitHub.\n"
    "R\u00e9sultats attendus : App MVC \u2014 auth bcrypt+SHA-256 (sessions 8h) \u2014 3 r\u00f4les "
    "(permissions JSON) \u2014 CRUD + validation SIRET (Luhn) \u2014 contrats PDF + SHA-256 "
    "verify_integrity() \u2014 logs d\u2019audit \u2014 conformit\u00e9 RGPD \u2014 155 tests pytest.",
    sz_c=7.5, ld_c=9.5, x=LM_F, w=TW_F)

# ── Rangée 9 : Description des ressources ────────────────────────────────
labeled_box(c, YR8, YR9 - YR8,
    "Description des ressources documentaires, mat\u00e9rielles et logicielles utilis\u00e9es\u00b2",
    "Langages & frameworks : Python 3.14 \u2014 PySide6 \u2265 6.6.0 / Qt for Python (GUI desktop native)\n"
    "ORM & BDD : SQLAlchemy \u2265 2.0.0 (z\u00e9ro SQL brut) \u2014 PostgreSQL (psycopg2, URL postgresql+psycopg2://)\n"
    "S\u00e9curit\u00e9 : bcrypt \u2265 4.1.0 (rounds=12) \u2014 SHA-256 (tokens session + int\u00e9grit\u00e9 contrats) \u2014 "
    "secrets.token_hex(32) \u2014 validate_siret Luhn 14 chiffres (rejet SIRET nuls, bug corrig\u00e9 03/2026)\n"
    "PDF : reportlab \u2265 4.0.0 (SimpleDocTemplate A4, Paragraph, Table, HRFlowable)\n"
    "Tests : pytest \u2014 3 fichiers, 155 tests \u2014 conftest.py (SQLite in-memory, isolation totale, "
    "database.db jamais modifi\u00e9 pendant pytest)\n"
    "Environnement : PyCharm Professional \u2014 Git/GitHub \u2014 macOS Darwin 24.1.0 (Python 3.14)\n"
    "Packaging : PyInstaller \u2192 livrable .app autonome macOS\n"
    "Documentation : docs/ du d\u00e9p\u00f4t \u2014 portfolio : https://ib-camara.vercel.app/",
    sz_c=7.5, ld_c=9.5, x=LM_F, w=TW_F)

# ── Rangée 10 : Modalités d'accès ────────────────────────────────────────
labeled_box(c, YR9, YR10 - YR9,
    "Modalit\u00e9s d\u2019acc\u00e8s aux productions\u00b3 et \u00e0 leur documentation\u2074",
    "Lancement : source .venv/bin/activate && python main.py\n"
    "Tests : python -m pytest tests/ -v  (155 tests, SQLite in-memory, isolation totale)\n"
    "Code source & docs : d\u00e9p\u00f4t GitHub \u2014 Portfolio : https://ib-camara.vercel.app/",
    sz_c=7.5, ld_c=9.5, x=LM_F, w=TW_F)

# ── Notes de bas de page ─────────────────────────────────────────────────
hl(c, YFN, x0=57, x1=201, lw=0.6)
fn_style = ParagraphStyle("fn", fontName="AU", fontSize=6, leading=7.5, spaceAfter=1.5)
fn_frame = Frame(LM_F, yb(YFN, 842/mm - YFN - 2), TW_F, (842/mm - YFN - 4)*mm,
                 leftPadding=0, rightPadding=0, topPadding=2, bottomPadding=0)
footnotes = [
    Paragraph(
        "\u00b9 En r\u00e9f\u00e9rence aux conditions de r\u00e9alisation et ressources n\u00e9cessaires du bloc "
        "\u00ab\u202fConception et d\u00e9veloppement d\u2019applications\u202f\u00bb pr\u00e9vues dans le r\u00e9f\u00e9rentiel BTS SIO.",
        fn_style),
    Spacer(1, 2),
    Paragraph(
        "\u00b2 Les r\u00e9alisations professionnelles sont \u00e9labor\u00e9es dans un environnement technologique "
        "conforme \u00e0 l\u2019annexe II.E du r\u00e9f\u00e9rentiel du BTS SIO.",
        fn_style),
    Spacer(1, 2),
    Paragraph(
        "\u00b3 Conform\u00e9ment au r\u00e9f\u00e9rentiel BTS SIO : \u00ab Dans tous les cas, les candidats doivent se "
        "munir des outils et ressources techniques n\u00e9cessaires au d\u00e9roulement de l\u2019\u00e9preuve. \u00bb",
        fn_style),
    Spacer(1, 2),
    Paragraph(
        "\u2074 Lien vers la documentation compl\u00e8te, pr\u00e9cisant et d\u00e9crivant, si cela n\u2019a \u00e9t\u00e9 fait "
        "au verso de la fiche, la r\u00e9alisation professionnelle.",
        fn_style),
]
fn_frame.addFromList(footnotes, c)

TC(c, 289, "1", fn="Helvetica", sz=8)
c.showPage()

# ════════════════════════════════════════════════════════════════════════════
# PAGE 2 — VERSO  (calé sur coordonnées Annexe 9 officielle)
# ════════════════════════════════════════════════════════════════════════════

# Constantes PAGE 2 (même LM_F/RM_F/TW_F que page 1)
YP2_H1 = 19.4   # haut en-tête
YP2_H2 = 46.1   # bas en-tête  (130.5pt / 2.835)
YP2_C1 = 48.5   # haut zone contenu (137.5pt / 2.835)
YP2_C2 = 240.2  # bas zone contenu  (680.5pt / 2.835)

# ── En-tête grisé ────────────────────────────────────────────────────────
draw_rect(c, LM_F, YP2_H1, TW_F, YP2_H2 - YP2_H1, lw=0.8,
          fill=colors.Color(0.92, 0.92, 0.92))
TC(c, YP2_H1 + 7,  "BTS SERVICES INFORMATIQUES AUX ORGANISATIONS",
   fn="Helvetica-Bold", sz=9)
TR(c, RM_F - 2*mm, YP2_H1 + 7, "SESSION 2026", fn="Helvetica-Bold", sz=9)
TC(c, YP2_H1 + 15,
   "ANNEXE VII-1-B : Fiche descriptive de r\u00e9alisation professionnelle",
   fn="Helvetica", sz=8)
TC(c, YP2_H1 + 21,
   "(verso, \u00e9ventuellement pages suivantes)",
   fn="Helvetica", sz=8)
TC(c, YP2_H1 + 27,
   "\u00c9preuve E6 - Conception et d\u00e9veloppement d\u2019applications (option SLAM)",
   fn="Helvetica-Oblique", sz=7.5)

# ── Zone contenu unique (Descriptif) ─────────────────────────────────────
draw_rect(c, LM_F, YP2_C1, TW_F, YP2_C2 - YP2_C1, lw=0.8)
hl(c, YP2_C1 + 5, x0=LM_F, x1=RM_F, lw=0.4)
T(c, LM_F + 1.5*mm, YP2_C1 + 3.8,
  "Descriptif de la r\u00e9alisation professionnelle, y compris les productions r\u00e9alis\u00e9es et sch\u00e9mas explicatifs",
  fn="Helvetica-Oblique", sz=7)

# ── Contenu : Présentation + Architecture + Tables ────────────────────────
flow(c, LM_F, YP2_C1 + 5, TW_F, YP2_C2 - YP2_C1 - 5,
    "Pr\u00e9sentation g\u00e9n\u00e9rale\n"
    "GestRes Pro est une application desktop Python 3.14 / PySide6 centralisant la gestion des ressources "
    "d\u2019entreprise (mat\u00e9riel informatique, comptes num\u00e9riques, v\u00e9hicules, badges d\u2019acc\u00e8s) avec 3 niveaux de "
    "r\u00f4les (Super Admin, Admin, Employ\u00e9), g\u00e9n\u00e9ration de contrats PDF sign\u00e9s \u00e9lectroniquement et journal "
    "d\u2019audit conforme RGPD.\n"
    "\n"
    "Architecture MVC\n"
    "src/models/  (10 mod\u00e8les SQLAlchemy)\n"
    "  \u00b7 user.py          \u2014 User [email, password_hash bcrypt, is_active, last_login]\n"
    "                        + Role [name, permissions JSON]\n"
    "  \u00b7 company.py       \u2014 Company [nom, SIRET Luhn, adresse, is_active]\n"
    "  \u00b7 resource_type.py \u2014 ResourceType [custom_fields JSON par entreprise]\n"
    "  \u00b7 resource.py      \u2014 Resource [statut 4 \u00e9tats, serial_number unique, custom_data JSON,\n"
    "                        is_available, current_assignment]\n"
    "  \u00b7 assignment.py    \u2014 Assignment [resource_id, user_id, assigned_by,\n"
    "                        start_date, end_date, duration_days, status]\n"
    "  \u00b7 contract.py      \u2014 Contract [content_hash SHA-256, sign(),\n"
    "                        verify_integrity(), pdf_path, signed_at, signature_hash]\n"
    "  \u00b7 audit_log.py     \u2014 AuditLog [action, table_name, record_id,\n"
    "                        old_values JSON, new_values JSON, ip_address]\n"
    "                        + Session [token_hash SHA-256, expires_at = now+8h]\n"
    "\n"
    "src/controllers/  (6 contr\u00f4leurs)\n"
    "  \u00b7 auth_controller       \u2014 login / logout / create_user / change_password /\n"
    "                            create_initial_super_admin\n"
    "  \u00b7 company_controller    \u2014 CRUD entreprises + validation SIRET (Luhn 14 chiffres)\n"
    "  \u00b7 resource_controller   \u2014 CRUD ressources + types, gestion des statuts\n"
    "  \u00b7 assignment_controller \u2014 create_assignment / close_assignment / cancel_assignment\n"
    "  \u00b7 contract_controller   \u2014 generate / sign / verify_contract / export_pdf (ReportLab)\n"
    "  \u00b7 user_controller       \u2014 CRUD utilisateurs + r\u00f4les\n"
    "\n"
    "src/views/  (10 vues PySide6)\n"
    "  login, main_window, dashboard, users, companies, resources,\n"
    "  assignments, contracts, logs + widgets/data_table.py (tableau pagin\u00e9 r\u00e9utilisable)\n"
    "\n"
    "src/utils/\n"
    "  \u00b7 security.py    \u2014 hash_password, verify_password, generate_token, hash_token SHA-256,\n"
    "                     validate_password_strength, validate_email, validate_siret Luhn,\n"
    "                     sanitize_input (strip + suppression caract\u00e8res de contr\u00f4le)\n"
    "  \u00b7 backup.py      \u2014 sauvegardes automatiques de la base PostgreSQL\n"
    "  \u00b7 maintenance.py \u2014 purge RGPD : donn\u00e9es expir\u00e9es + sessions p\u00e9rim\u00e9es\n"
    "\n"
    "config.py : BCRYPT_ROUNDS=12 \u00b7 SESSION_DURATION_HOURS=8 \u00b7 PASSWORD_MIN_LENGTH=8\n"
    "            DEFAULT_RETENTION_DAYS=1095 (3 ans) \u00b7 AUDIT_LOG_RETENTION_DAYS=1825 (5 ans)\n"
    "\n"
    "Tables principales (10 tables PostgreSQL)\n"
    "roles          : super_admin=[\u00aball\u00bb], admin=[8 permissions], employee=[4 permissions]   \u21921:N users\n"
    "users          : email (lower+strip), password_hash bcrypt, is_active, last_login\n"
    "                 \u2192 N:1 roles / companies\n"
    "companies      : nom, SIRET (Luhn 14 chiffres), adresse   \u2192 1:N users/resource_types/resources\n"
    "resource_types : custom_fields JSON par entreprise   \u2192 1:N resources\n"
    "resources      : statut (available/assigned/maintenance/retired), serial_number unique,\n"
    "                 custom_data JSON, is_available   \u2192 1:N assignments\n"
    "assignments    : resource_id, user_id, assigned_by, start_date, end_date, duration_days\n"
    "                 \u2192 1:N contracts\n"
    "contracts      : content_hash SHA-256, is_signed, signed_at, signature_hash, pdf_path\n"
    "audit_logs     : action, table_name, record_id, old_values JSON, new_values JSON, ip_address\n"
    "sessions       : token_hash = SHA-256(secrets.token_hex(32)), expires_at = now + 8h",
    fn="AU", sz=7.2, ld=9)

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
T(c, LM, 23.5, "ANNEXE VII-1-B — CAMARA Ibrahim — N° 2545812845 — (suite page 4)", sz=8)
hl(c, 26, lw=0.6)

labeled_box(c, 26, 120,
    "Données de test — CleanPro Services (société de nettoyage fictive)",
    "Objectif : valider l'application sur un cas métier réaliste avant la présentation.\n"
    "\n"
    "Société      : CleanPro Services\n"
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
    "Identifiants de connexion",
    "Super Admin  :  superadmin@gestres.fr    /  SuperAdmin1!\n"
    "Admin        :  responsable@cleanpro.fr  /  Responsable1!\n"
    "Employé 1    :  employe1@cleanpro.fr     /  Employe001!\n"
    "Employé 2    :  employe2@cleanpro.fr     /  Employe002!\n"
    "Employé 3    :  employe3@cleanpro.fr     /  Employe003!\n"
    "Employé 4    :  employe4@cleanpro.fr     /  Employe004!",
    sz_c=8, ld_c=10.5)

TC(c, 289, "4", fn="Helvetica", sz=8)
c.showPage()

# ════════════════════════════════════════════════════════════════════════════
# PAGE 5 — Capture d'écran
# ════════════════════════════════════════════════════════════════════════════
from reportlab.lib.utils import ImageReader
_img_reader = ImageReader(
    "/Users/camaraibrahim/PycharmProjects/PythonProject/docs/"
    "Capture d\u2019\u00e9cran 2026-03-24 \u00e0 11.56.36.png")
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
