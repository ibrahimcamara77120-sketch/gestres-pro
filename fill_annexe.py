import fitz
import shutil

ORIG  = ("/Users/camaraibrahim/Downloads/"
         "9 - ANNEXE VII - EPREUVE E6 PRATIQUE OPTION A ET OPTION B - BTS SIO 2026.docx.pdf")
BUILD = "/Users/camaraibrahim/PycharmProjects/PythonProject/docs/newannex.pdf"
OUT   = "/Users/camaraibrahim/PycharmProjects/PythonProject/docs/newannex.pdf"
TTF   = "/System/Library/Fonts/Supplemental/Arial.ttf"

doc = fitz.open(ORIG)
p1, p2 = doc[0], doc[1]


def wipe(page, x0, y0, x1, y1):
    page.draw_rect(fitz.Rect(x0, y0, x1, y1),
                   color=(1, 1, 1), fill=(1, 1, 1), width=0)


def T(page, x, y, text, size=9):
    page.insert_text((x, y), text,
                     fontsize=size, fontname="au", fontfile=TTF, color=(0, 0, 0))


def TB(page, x0, y0, x1, y1, text, size=8.5, align=0):
    rc = page.insert_textbox(
        fitz.Rect(x0, y0, x1, y1), text,
        fontsize=size, fontname="au", fontfile=TTF,
        color=(0, 0, 0), align=align
    )
    return rc


def check(page, x, y, size=9):
    wipe(page, x - 1, y - size - 1, x + size + 1, y + 1)
    r = fitz.Rect(x, y - size + 1, x + size - 1, y)
    page.draw_rect(r, color=(0, 0, 0), width=0.6)
    w = size - 2
    h = size - 2
    bx, by = x + 1, y - size + 2
    p1_ = fitz.Point(bx + w * 0.15, by + h * 0.55)
    p2_ = fitz.Point(bx + w * 0.40, by + h * 0.80)
    p3_ = fitz.Point(bx + w * 0.85, by + h * 0.10)
    page.draw_line(p1_, p2_, color=(0, 0, 0), width=0.8)
    page.draw_line(p2_, p3_, color=(0, 0, 0), width=0.8)


# page 1

T(p1, 522, 146, "1", size=10)

wipe(p1, 50, 155, 408, 173)
T(p1, 51, 168, "Nom, pr\u00e9nom :  CAMARA Ibrahim", size=10)

check(p1, 385, 194, size=10)

check(p1, 122, 285, size=10)

wipe(p1, 50, 242, 543, 255)
T(p1, 51, 252,
  "GestRes Pro \u2014 Syst\u00e8me de gestion de ressources d'entreprise",
  size=9)

rc6 = TB(p1, 52, 369, 543, 434,
         "Projet développé seul dans le cadre du BTS SIO option SLAM (épreuve E6) "
         "— année scolaire 2025-2026.\n"
         "Environnement technique : Python 3.14 · PySide6 (Qt 6) · SQLite / "
         "SQLAlchemy ORM · bcrypt · ReportLab · python-dateutil · pytest.\n"
         "IDE : PyCharm Professional · Contrôle de version : Git / GitHub.\n"
         "Résultat attendu : application desktop de gestion de ressources "
         "d'entreprise (matérielles et numériques), sécurisée (RGPD), "
         "testée (155 tests automatisés) et documentée.",
         size=8.4)
if rc6 < 0:
    print(f"  Conditions : débordement ({rc6:.0f} pt)")

rc7 = TB(p1, 52, 452, 543, 596,
         "Langages & frameworks : Python 3.14 · PySide6 6.x (Qt for Python) "
         "· SQLAlchemy 2.x ORM · SQLite 3.\n"
         "Sécurité : bcrypt (hachage mots de passe) · secrets.token_hex (sessions) "
         "· hashlib SHA-256 (intégrité des contrats).\n"
         "Génération de documents : ReportLab (PDF contrats — dépendance production).\n"
         "Tests : pytest 8.x — 155 tests unitaires et d'intégration, base SQLite "
         "en mémoire isolée (conftest.py autouse fixture).\n"
         "Outils : Git / GitHub · PyCharm Professional (IDE) · VS Code.\n"
         "Matériel : MacBook Pro — macOS Sequoia 15.1 — développement local, "
         "base SQLite fichier (database.db).\n"
         "Documentation : CLAUDE.md · FEATURES.md · INSTALLATION.md "
         "· docs/rapport_tests.md · docs/tableau_synthese_e5.xlsx.",
         size=8.4)
if rc7 < 0:
    print(f"  Description ressources : débordement ({rc7:.0f} pt)")

rc8 = TB(p1, 52, 612, 543, 655,
         "Dépôt GitHub : github.com/camaraibrahim/gestres-pro "
         "(code source, tests, documentation).\n"
         "Portfolio : https://ib-camara.vercel.app/\n"
         "Données de test : seed_test_company.py — [SOCIÉTÉ TEST] CleanPro Services "
         "· superadmin@gestres.test / SuperAdmin1! "
         "· responsable@cleanpro.test / Responsable1!",
         size=7.6)
if rc8 < 0:
    print(f"  Modalités d'accès : débordement ({rc8:.0f} pt)")


# page 2

rc2 = TB(p2, 52, 153, 543, 677,
         "Présentation générale\n"
         "GestRes Pro est une application desktop (Python / PySide6) permettant à "
         "des entreprises de gérer le cycle de vie complet de leurs ressources : "
         "création, affectation aux employés, génération de contrats PDF signés "
         "numériquement, audit et traçabilité RGPD.\n\n"

         "Architecture MVC\n"
         "• Modèles (src/models/) : 10 tables SQLAlchemy — User, Role, Company, "
         "Resource, ResourceType, Assignment, Contract, AuditLog, Session — "
         "clés étrangères, triggers d'audit automatiques.\n"
         "• Contrôleurs (src/controllers/) : AuthController, CompanyController, "
         "UserController, ResourceController, AssignmentController, "
         "ContractController — logique métier isolée, aucun SQL direct.\n"
         "• Vues (src/views/) : fenêtres PySide6 (QMainWindow, QDialog, QTableWidget) "
         "— login, dashboard, ressources, affectations, contrats. Interface sobre "
         "et professionnelle : palette navy/bleu corporate, polices standard "
         "(Segoe UI/Arial), sans emoji, arrondis réduits — centralisée dans styles.py.\n"
         "• Sécurité (src/utils/security.py) : bcrypt, tokens SHA-256, "
         "validation SIRET (Luhn), validation email, sanitisation des entrées.\n\n"

         "Fonctionnalités\n"
         "a) Authentification & sessions : login bcrypt + token secrets.token_hex(32) "
         "haché SHA-256, expiration configurable, déconnexion propre.\n"
         "b) Gestion des entreprises (super-admin) : création espace société, "
         "validation SIRET (algorithme de Luhn), statistiques ressources.\n"
         "c) Types de ressources personnalisables : champs custom JSON "
         "(texte, nombre, booléen, date) définis par type.\n"
         "d) Gestion des ressources : CRUD complet, numéro de série unique, "
         "données custom, statut (disponible / affecté).\n"
         "e) Affectations : assignation ressource ↔ employé avec dates, notes, "
         "historique complet.\n"
         "f) Contrats PDF : génération ReportLab, signature SHA-256, export PDF, "
         "vérification d'intégrité.\n"
         "g) Sécurité & RGPD : logs d'audit automatiques, anonymisation "
         "(droit à l'oubli), sauvegardes automatiques (backups/).\n"
         "h) Tests automatisés : 155 tests pytest, base SQLite en mémoire isolée "
         "(conftest.py autouse), jamais d'impact sur la base de production.\n\n"

         "Données de test — [SOCIÉTÉ TEST] CleanPro Services\n"
         "Société fictive de nettoyage professionnel (SIRET 73282932000074) "
         "générée via seed_test_company.py.\n"
         "• 5 utilisateurs (1 admin + 4 employés) · 7 types de ressources "
         "· 20 ressources matérielles (balais, serpillères, chariots, aspirateurs, "
         "EPI, produits nettoyants).\n"
         "• 11 affectations actives · 11 contrats signés (SHA-256) et exportés en PDF.\n"
         "• Validation complète de tous les modules sur un cas métier réaliste "
         "avant la présentation E6.",
         size=8.3)
if rc2 < 0:
    print(f"  Verso page 2 : débordement ({rc2:.0f} pt)")


# pages 3-5 depuis build_annexe.py
extra = fitz.open(BUILD)
doc.insert_pdf(extra, from_page=2, to_page=4)
extra.close()


tmp = OUT + "_tmp.pdf"
doc.save(tmp, garbage=4, deflate=True)
total = len(doc)
doc.close()
shutil.move(tmp, OUT)
print(f"newannex.pdf — {total} pages")
