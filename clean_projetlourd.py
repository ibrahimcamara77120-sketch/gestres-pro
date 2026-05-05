"""
Nettoie Annex PROJETLOURD.pdf :
  - Supprime les pages vides (< 3 mots)
  - Corrige l'ancien contenu (SOCIÉTÉ TEST, @.test)
  - Sauvegarde → docs/newannex.pdf
"""
import fitz, shutil

SRC = "/Users/camaraibrahim/PycharmProjects/PythonProject/docs/Annex PROJETLOURD.pdf"
OUT = "/Users/camaraibrahim/PycharmProjects/PythonProject/docs/newannex.pdf"
TTF = "/System/Library/Fonts/Supplemental/Arial.ttf"


def wipe(page, x0, y0, x1, y1):
    page.draw_rect(fitz.Rect(x0, y0, x1, y1),
                   color=(1, 1, 1), fill=(1, 1, 1), width=0)


def T(page, x, y, text, size=8):
    page.insert_text((x, y), text,
                     fontsize=size, fontname="au", fontfile=TTF, color=(0, 0, 0))


doc = fitz.open(SRC)

# ── Identifier les pages à conserver ─────────────────────────────────────────
keep = []
for i in range(doc.page_count):
    words = doc[i].get_text().strip().split()
    if len(words) <= 2:
        print(f"  Page {i + 1} supprimée (vide : {repr(doc[i].get_text().strip()[:20])})")
    else:
        keep.append(i)

# ── Corriger page 2 (index 1) ─────────────────────────────────────────────────
# Bloc Portfolio + Données de test (y ≈ 75-100)
p2 = doc[1]
wipe(p2, 50, 73, 562, 102)
T(p2, 53, 86,  "Portfolio : https://ib-camara.vercel.app/", size=8)
T(p2, 53, 99,
  "Données de test : seed_test_company.py — CleanPro Services"
  " · superadmin@gestres.fr / SuperAdmin1!"
  " · responsable@cleanpro.fr / Responsable1!",
  size=7.5)

# ── Corriger page 6 (index 5) ─────────────────────────────────────────────────
p6 = doc[5]

# En-tête : "(suite page 4 / données de test)" → "(suite page 4)"
wipe(p6, 27, 62, 562, 88)
T(p6, 30, 80,
  "ANNEXE VII-1-B — CAMARA Ibrahim — N° 2545812845 — (suite page 4)",
  size=7.5)

# Label box : "Données de test — [SOCIÉTÉ TEST] CleanPro Services..."
wipe(p6, 32, 86, 562, 101)
T(p6, 35, 98,
  "Données de test — CleanPro Services (société de nettoyage fictive)",
  size=8)

# Label identifiants : "(données de test)" → retiré
wipe(p6, 32, 454, 562, 469)
T(p6, 35, 465, "Identifiants de connexion", size=8)

# Emails @.test → @.fr
wipe(p6, 32, 476, 562, 562)
T(p6, 35, 487, "Super Admin  :  superadmin@gestres.fr    /  SuperAdmin1!", size=8)
T(p6, 35, 500, "Admin        :  responsable@cleanpro.fr  /  Responsable1!", size=8)
T(p6, 35, 513, "Employé 1    :  employe1@cleanpro.fr     /  Employe001!", size=8)
T(p6, 35, 526, "Employé 2    :  employe2@cleanpro.fr     /  Employe002!", size=8)
T(p6, 35, 539, "Employé 3    :  employe3@cleanpro.fr     /  Employe003!", size=8)
T(p6, 35, 552, "Employé 4    :  employe4@cleanpro.fr     /  Employe004!", size=8)

# ── Supprimer les pages vides ─────────────────────────────────────────────────
doc.select(keep)

# ── Sauvegarder ───────────────────────────────────────────────────────────────
tmp = OUT + "_tmp.pdf"
doc.save(tmp, garbage=4, deflate=True)
total = doc.page_count
doc.close()
shutil.move(tmp, OUT)
print(f"\nnewannex.pdf — {total} pages propres")
