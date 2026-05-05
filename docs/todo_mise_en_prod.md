# TODO — Mise en production GestRes Pro
**Projet** : GestRes Pro — Gestion de ressources d'entreprise
**Auteur** : CAMARA Ibrahim
**Date** : Mars 2026

---

## Légende

- 🔴 **BLOQUANT** — L'app ne peut pas être livrée sans ça
- 🟠 **IMPORTANT** — À faire avant démo / présentation BTS
- 🟡 **AMÉLIORATION** — Peut être fait en phase 2 post-livraison

---

## 🔴 BLOQUANT — Vues manquantes (l'app est vide)

Tous les boutons de la sidebar et les actions rapides du dashboard affichent
un simple message "Fonctionnalité à venir". Les contrôleurs existent et fonctionnent
(ils sont testés à 100%), mais aucune vue n'est connectée.

### 1. `src/views/users_view.py` — À créer

**Ce que ça doit faire :**
- Tableau avec tous les utilisateurs (nom, email, rôle, entreprise, statut actif/inactif)
- Boutons : Créer, Modifier, Désactiver (soft delete), Réinitialiser mot de passe
- Filtre par entreprise, recherche par nom/email
- Formulaire de création/édition avec validation en temps réel

**Contrôleur à appeler :**
```python
from src.controllers.user_controller import user_controller

user_controller.get_all_users()
user_controller.get_all_users(company_id=x)
user_controller.create_user(email, password, first_name, last_name, role_id, company_id)
user_controller.update_user(user_id, ...)
user_controller.delete_user(user_id)
user_controller.reset_password(user_id, new_password)
user_controller.get_all_roles()
```

**Branchement dans `dashboard_view.py` :**
```python
# Ligne 439 — remplacer :
self.btn_users.clicked.connect(lambda: self._show_coming_soon("Gestion des utilisateurs"))
# Par :
self.btn_users.clicked.connect(lambda: self.navigate_to.emit("users"))
```

---

### 2. `src/views/companies_view.py` — À créer

**Ce que ça doit faire :**
- Tableau des entreprises (nom, SIRET formaté, adresse, nb utilisateurs, nb ressources, statut)
- Boutons : Créer, Modifier, Désactiver
- Validation SIRET en temps réel dans le formulaire
- Stats par entreprise (utilisateurs actifs, ressources disponibles)

**Contrôleur à appeler :**
```python
from src.controllers.company_controller import company_controller

company_controller.get_all_companies()
company_controller.get_all_companies(include_inactive=True)
company_controller.create_company(name, siret, address)
company_controller.update_company(company_id, ...)
company_controller.delete_company(company_id)
company_controller.get_company_stats(company_id)
```

**Branchement dans `dashboard_view.py` :**
```python
# Ligne 440 — remplacer :
self.btn_companies.clicked.connect(lambda: self._show_coming_soon("Gestion des entreprises"))
# Par :
self.btn_companies.clicked.connect(lambda: self.navigate_to.emit("companies"))
```

---

### 3. `src/controllers/resource_controller.py` + `src/views/resources_view.py` — À créer

**Le contrôleur n'existe pas encore.** Il faut le créer en suivant le même
pattern que `user_controller.py` et `company_controller.py`.

**Méthodes à implémenter dans le contrôleur :**
```python
class ResourceController:
    def get_all_resources(self, company_id=None, status=None)  # filtres
    def get_resource_by_id(self, resource_id)
    def create_resource(self, company_id, resource_type_id, name, serial_number, custom_data)
    def update_resource(self, resource_id, name=None, status=None, serial_number=None)
    def delete_resource(self, resource_id)  # soft delete via is_active ou status="retired"
    def get_all_resource_types(self, company_id)
    def create_resource_type(self, company_id, name, description, custom_fields)
```

**Statuts disponibles** (déjà dans `config.py`) :
```python
RESOURCE_STATUS = {
    "available": "Disponible",
    "assigned": "Affectée",
    "maintenance": "En maintenance",
    "retired": "Retirée"
}
```

**La vue doit afficher :**
- Tableau avec filtres par type, statut, entreprise
- Formulaire de création avec champs personnalisés dynamiques
  (les champs personnalisés sont en JSON dans `resource_type.custom_fields`)

---

### 4. `src/controllers/assignment_controller.py` + `src/views/assignments_view.py` — À créer

**Le contrôleur n'existe pas encore.**

**Méthodes à implémenter :**
```python
class AssignmentController:
    def get_all_assignments(self, company_id=None, status="active")
    def get_assignments_by_user(self, user_id)
    def get_assignments_by_resource(self, resource_id)
    def create_assignment(self, resource_id, user_id, assigned_by, start_date, notes)
    def close_assignment(self, assignment_id, end_date)   # retour ressource
    def cancel_assignment(self, assignment_id)
```

**Effets de bord importants :**
Quand une affectation est créée → mettre `resource.status = "assigned"`
Quand une affectation est fermée/annulée → remettre `resource.status = "available"`
Ces deux opérations doivent être dans la même transaction.

**Statuts** (dans `config.py`) :
```python
ASSIGNMENT_STATUS = {
    "active": "Active",
    "returned": "Retournée",
    "cancelled": "Annulée"
}
```

---

### 5. `src/controllers/contract_controller.py` + `src/views/contracts_view.py` — À créer

**Le contrôleur n'existe pas encore.**

**Méthodes à implémenter :**
```python
class ContractController:
    def get_contracts_by_assignment(self, assignment_id)
    def generate_contract(self, assignment_id, content_template)  # crée le contrat + hash
    def sign_contract(self, contract_id, signer_data)             # appelle contract.sign()
    def verify_contract_integrity(self, contract_id)              # appelle contract.verify_integrity()
    def export_contract_pdf(self, contract_id, output_path)       # utilise reportlab
```

**Le modèle `Contract` a déjà toute la logique :**
```python
# src/models/contract.py — déjà implémenté
Contract.compute_hash(content)       # SHA-256 du contenu
contract.verify_integrity()          # vérifie que le contenu n'a pas changé
contract.sign(signer_data)           # appose la signature + hash
contract.is_signed                   # property booléenne
```

**Pour la génération PDF :** `reportlab` est déjà dans `requirements.txt`.
Utiliser `reportlab.pdfgen.canvas` ou `reportlab.platypus` pour générer
et stocker le chemin dans `contract.pdf_path`.

---

### 6. `src/views/logs_view.py` — À créer

**Ce que ça doit faire :**
- Tableau des logs d'audit avec filtres : date, action, utilisateur, table
- Actions disponibles déjà logguées : LOGIN, LOGOUT, LOGIN_FAILED, CREATE, UPDATE, DELETE, PASSWORD_CHANGE, PASSWORD_RESET
- Bouton export CSV ou TXT
- Accès réservé aux admins (déjà géré dans `dashboard_view.py` ligne 478)

**Requête de base :**
```python
from src.models.audit_log import AuditLog
from src.models.base import get_session

with get_session() as session:
    logs = session.query(AuditLog).order_by(AuditLog.created_at.desc()).all()
```

---

### 7. Navigation dans `main_window.py` — À compléter

Le `QStackedWidget` actuel ne gère que deux écrans (login + dashboard).
Il faut étendre la navigation pour gérer les vues métier.

**Approche recommandée — étendre le stack ou imbriquer dans le dashboard :**

**Option A** (plus simple) : imbriquer un `QStackedWidget` dans la zone de contenu
du dashboard. La sidebar reste fixe, seul le contenu central change.

**Option B** : ajouter toutes les vues au stack principal de `main_window.py` et
connecter le signal `navigate_to` du dashboard.

Le signal `navigate_to = Signal(str)` existe déjà dans `DashboardView` (ligne 160).
Il n'est juste pas connecté.

---

## 🟠 IMPORTANT — Avant démo BTS

### 8. Vérification des permissions côté contrôleur

Actuellement, `user_controller.py` et `company_controller.py` ne vérifient pas
si l'utilisateur connecté a le droit d'effectuer l'opération. Seule l'UI masque
les boutons. Si quelqu'un appelle le contrôleur directement, il n'y a pas de garde.

**À ajouter en début de chaque méthode sensible :**
```python
# Exemple dans user_controller.py — create_user()
from src.controllers.auth_controller import auth_controller

def create_user(self, ...):
    if not auth_controller.has_permission("manage_users"):
        return False, "Permission refusée", None
    # ... reste du code
```

**Permissions déjà définies dans `config.py` :**
```python
"admin": ["view_resources", "manage_resources", "view_users", "manage_users",
          "view_logs", "generate_contracts", "view_assignments", "manage_assignments"]
"employee": ["view_own_resources", "view_own_assignments", "sign_contracts", "view_own_history"]
```

---

### 9. Supprimer l'email par défaut dans la boîte de dialogue initiale

**Fichier :** `src/views/main_window.py` ligne 81

```python
# Actuellement — expose un email par défaut visible dans l'UI :
email, ok = QInputDialog.getText(..., "admin@entreprise.com")

# Corriger :
email, ok = QInputDialog.getText(..., "")
```

---

### 10. Purge automatique des logs d'audit (conformité RGPD)

Les constantes existent dans `config.py` mais aucun code ne les utilise.

**Créer une fonction utilitaire dans `src/utils/` :**
```python
# src/utils/maintenance.py
from datetime import datetime, timedelta, timezone
from src.models.base import get_session
from src.models.audit_log import AuditLog
import config

def purge_expired_logs():
    cutoff = datetime.now(timezone.utc) - timedelta(days=config.AUDIT_LOG_RETENTION_DAYS)
    with get_session() as session:
        session.query(AuditLog).filter(AuditLog.created_at < cutoff).delete()
        session.commit()
```

**L'appeler au démarrage de l'app** dans `main.py`, ou programmer une vérification
périodique avec `QTimer` dans `main_window.py`.

---

### 11. Séparer `requirements.txt` prod / dev

```
# requirements.txt (prod uniquement)
PySide6>=6.6.0
SQLAlchemy>=2.0.0
bcrypt>=4.1.0
reportlab>=4.0.0
python-dateutil>=2.8.0

# requirements-dev.txt (dev + tests)
-r requirements.txt
pytest>=8.0.0
pytest-cov>=4.0.0
```

`pytest` ne doit pas être installé sur une machine de production.

---

### 12. Gestion des erreurs inattendues dans les vues

Les vues n'ont pas de `try/except` global. Si une requête BDD échoue
de manière inattendue (disque plein, base corrompue), l'app plantera sans message.

**Exemple à appliquer dans toutes les vues qui lisent la BDD :**
```python
try:
    data = user_controller.get_all_users()
    self._populate_table(data)
except Exception as e:
    QMessageBox.critical(self, "Erreur", f"Impossible de charger les données : {e}")
```

---

## 🟡 AMÉLIORATION — Phase 2

### 13. Sauvegarde automatique de la base de données

La base est un fichier SQLite local. Sans sauvegarde, une suppression accidentelle
ou une panne disque fait tout perdre.

**Implémentation simple :**
```python
# src/utils/backup.py
import shutil
from datetime import datetime
from pathlib import Path
import config

def create_backup():
    backup_dir = config.BASE_DIR / "backups"
    backup_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = backup_dir / f"database_{timestamp}.db"
    shutil.copy2(config.DATABASE_PATH, dest)
    # Garder uniquement les 10 dernières sauvegardes
    backups = sorted(backup_dir.glob("database_*.db"))
    for old in backups[:-10]:
        old.unlink()
```

Appeler au démarrage dans `main.py`.

---

### 14. Anonymisation RGPD — droit à l'oubli

Le modèle `User` a `is_active` (soft delete) mais pas d'anonymisation.
Le RGPD exige qu'on puisse effacer les données personnelles d'un utilisateur
sans casser les relations (logs d'audit, affectations historiques).

**À ajouter dans `user_controller.py` :**
```python
def anonymize_user(self, user_id: int) -> Tuple[bool, str]:
    with get_session() as session:
        user = session.query(User).filter_by(id=user_id).first()
        if not user:
            return False, "Utilisateur non trouvé"
        user.email = f"anonymized_{user_id}@deleted.local"
        user.first_name = None
        user.last_name = None
        user.password_hash = "ANONYMIZED"
        user.is_active = False
        session.commit()
        return True, "Données personnelles supprimées"
```

---

### 15. Tests de l'interface utilisateur

Les 155 tests actuels couvrent uniquement les modèles, contrôleurs et utilitaires.
Les vues PySide6 ne sont pas testées.

**Pour les vues, utiliser `pytest-qt` :**
```bash
pip install pytest-qt
```

```python
# Exemple de test de vue
def test_login_empty_fields(qtbot):
    from src.views.login_view import LoginView
    view = LoginView()
    qtbot.addWidget(view)
    view.email_input.clear()
    view.password_input.clear()
    qtbot.mouseClick(view.login_button, Qt.MouseButton.LeftButton)
    assert view.error_label.isVisible()
```

---

### 16. Icône d'application et packaging

Pour distribuer l'app en `.app` (macOS) ou `.exe` (Windows) :

```bash
pip install pyinstaller

# macOS
pyinstaller --windowed --onefile --name "GestRes Pro" main.py

# Avec icône personnalisée
pyinstaller --windowed --onefile --icon=assets/icon.icns --name "GestRes Pro" main.py
```

Créer un dossier `assets/` avec `icon.icns` (macOS) et `icon.ico` (Windows).

---

## Récapitulatif par priorité

| # | Tâche | Priorité | Fichier(s) concerné(s) |
|---|---|---|---|
| 1 | Vue utilisateurs | 🔴 BLOQUANT | `src/views/users_view.py` (à créer) |
| 2 | Vue entreprises | 🔴 BLOQUANT | `src/views/companies_view.py` (à créer) |
| 3 | Contrôleur + vue ressources | 🔴 BLOQUANT | `src/controllers/resource_controller.py` + `src/views/resources_view.py` (à créer) |
| 4 | Contrôleur + vue affectations | 🔴 BLOQUANT | `src/controllers/assignment_controller.py` + `src/views/assignments_view.py` (à créer) |
| 5 | Contrôleur + vue contrats | 🔴 BLOQUANT | `src/controllers/contract_controller.py` + `src/views/contracts_view.py` (à créer) |
| 6 | Vue journaux d'audit | 🔴 BLOQUANT | `src/views/logs_view.py` (à créer) |
| 7 | Navigation complète | 🔴 BLOQUANT | `src/views/main_window.py` + `src/views/dashboard_view.py` |
| 8 | Permissions côté contrôleur | 🟠 IMPORTANT | `src/controllers/user_controller.py`, `company_controller.py` |
| 9 | Supprimer email par défaut | 🟠 IMPORTANT | `src/views/main_window.py` ligne 81 |
| 10 | Purge logs RGPD | 🟠 IMPORTANT | `src/utils/maintenance.py` (à créer) |
| 11 | Séparer requirements prod/dev | 🟠 IMPORTANT | `requirements.txt` + `requirements-dev.txt` |
| 12 | Gestion erreurs vues | 🟠 IMPORTANT | Toutes les vues |
| 13 | Sauvegarde BDD auto | 🟡 AMÉLIORATION | `src/utils/backup.py` (à créer) |
| 14 | Anonymisation RGPD | 🟡 AMÉLIORATION | `src/controllers/user_controller.py` |
| 15 | Tests UI (pytest-qt) | 🟡 AMÉLIORATION | `tests/test_views.py` (à créer) |
| 16 | Packaging `.app` / `.exe` | 🟡 AMÉLIORATION | `main.py` + `assets/` |

---

## Ce qui est déjà prêt pour la prod

| Composant | État |
|---|---|
| Modèles SQLAlchemy (8 tables) | ✅ Complet + 52 tests |
| AuthController (login/logout/sessions) | ✅ Complet + 26 tests |
| UserController (CRUD + rôles) | ✅ Complet + 18 tests |
| CompanyController (CRUD + stats) | ✅ Complet + 17 tests |
| Sécurité (bcrypt, tokens, validation) | ✅ Complet + 40 tests |
| Audit logging (toutes les actions) | ✅ Actif sur tous les contrôleurs |
| Écran de connexion | ✅ Fonctionnel |
| Tableau de bord + stats | ✅ Fonctionnel |
| Configuration initiale (1er super admin) | ✅ Fonctionnel |
