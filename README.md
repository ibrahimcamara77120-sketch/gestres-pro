# GestRes Pro — Application de Gestion de Ressources

Application de bureau Python (PySide6) développée dans le cadre du BTS SIO.

---

## Télécharger et lancer l'application

> Aucune installation de Python requise — l'exécutable est autonome.

1. Allez dans l'onglet **[Releases](../../releases/latest)**
2. Téléchargez le fichier correspondant à votre système :

| Système | Fichier à télécharger |
|---------|----------------------|
| Windows | `GestRes-Pro-Windows.exe` |
| macOS   | `GestRes-Pro-macOS` |
| Linux   | `GestRes-Pro-Linux` |

3. Double-cliquez pour lancer

> **macOS** : si un message "développeur non identifié" apparaît → clic droit → Ouvrir

---

## Fonctionnalités

- Authentification sécurisée (bcrypt)
- Tableau de bord analytique
- Gestion des ressources (CRUD complet)
- Gestion des contrats et affectations
- Génération de rapports PDF (ReportLab)
- Sauvegarde automatique de la base de données

## Technologies

- **Python 3.11** — langage principal
- **PySide6** — interface graphique
- **SQLAlchemy** — ORM base de données SQLite
- **ReportLab** — génération de PDF

## Lancer depuis le code source

```bash
git clone https://github.com/ibrahimcamara77120-sketch/gestres-pro
cd gestres-pro
pip install -r requirements.txt
python main.py
```
