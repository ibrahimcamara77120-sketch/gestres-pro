# AUDIT — GestRes Pro
Date : 2026-06-03 | Auditeur : Claude Code

---

## 1. Architecture & Stack réelle

| Couche | Technologie |
|---|---|
| Langage | Python 3.14 |
| GUI | PySide6 (Qt for Python) |
| Base de données | PostgreSQL via SQLAlchemy ORM |
| Hachage | bcrypt (10 rounds) |
| PDF | reportlab |
| Pattern | MVC strict |

```
PythonProject/
├── main.py                  # Point d'entrée
├── config.py                # Variables d'environnement, rôles, statuts
├── database.db              # (ignoré — app utilise PostgreSQL)
├── src/
│   ├── models/              # SQLAlchemy ORM
│   │   ├── base.py          # Engine, SessionLocal, get_session()
│   │   ├── user.py          # User, Role
│   │   ├── company.py       # Company
│   │   ├── resource.py      # Resource
│   │   ├── resource_type.py # ResourceType
│   │   ├── assignment.py    # Assignment
│   │   ├── contract.py      # Contract
│   │   └── audit_log.py     # AuditLog, Session
│   ├── controllers/         # Logique métier
│   │   ├── auth_controller.py
│   │   ├── user_controller.py
│   │   ├── company_controller.py
│   │   ├── resource_controller.py
│   │   ├── assignment_controller.py
│   │   └── contract_controller.py
│   ├── views/               # UI PySide6
│   │   ├── main_window.py
│   │   ├── login_view.py
│   │   ├── dashboard_view.py
│   │   ├── users_view.py
│   │   ├── companies_view.py
│   │   ├── resources_view.py
│   │   ├── assignments_view.py
│   │   ├── contracts_view.py
│   │   ├── logs_view.py
│   │   ├── setup_wizard.py
│   │   ├── styles.py
│   │   └── widgets/data_table.py
│   └── utils/
│       ├── security.py      # bcrypt, tokens, validation
│       ├── validators.py    # Validation générique
│       ├── backup.py        # pg_dump automatique
│       └── maintenance.py   # Purge logs/sessions expirées
└── tests/
```

---

## 2. État des modules

| Module | Vue | Contrôleur | État | Notes |
|---|---|---|---|---|
| Authentification | login_view ✅ | auth_controller ✅ | ✅ Fonctionnel | try/except + finally sur bouton |
| Tableau de bord | dashboard_view ✅ | — | ✅ Fonctionnel | Stats, navigation par rôle |
| Utilisateurs | users_view ✅ | user_controller ✅ | ✅ Fonctionnel | CRUD complet |
| Entreprises | companies_view ✅ | company_controller ✅ | ✅ Fonctionnel | Super Admin uniquement |
| Ressources | resources_view ✅ | resource_controller ✅ | ✅ Fonctionnel | Vue filtrée employé ✅ |
| Affectations | assignments_view ✅ | assignment_controller ✅ | ✅ Fonctionnel | Vue filtrée employé ✅ |
| Contrats | contracts_view ⚠️ | contract_controller ✅ | ⚠️ Partiel | Bug ligne 205 + pas de filtre employé |
| Journaux | logs_view ✅ | — | ✅ Fonctionnel | Export CSV, 500 derniers logs |
| Déconnexion | dashboard_view ✅ | auth_controller ✅ | ✅ Fonctionnel | Bouton visible en sidebar |

---

## 3. Bugs identifiés

### 🔴 BLOQUANTS

Aucun bug bloquant sur les parcours principaux.

### 🟠 MAJEURS

| # | Fichier | Ligne | Description | Impact |
|---|---|---|---|---|
| M-1 | contracts_view.py | 205 | `self.name_input = QTextEdit.__class__.__mro__` — ligne morte (écrasée ligne 207), mais code incohérent. | Aucun à l'exécution car écrasé immédiatement, mais risque de confusion |
| M-2 | contracts_view.py | — | Vue Contrats non filtrée pour les employés — ils voient tous les contrats de l'entreprise, pas seulement les leurs | Incohérence de rôle |
| M-3 | assignments_view.py | ~42 | `AssignmentFormDialog` propose tous les utilisateurs y compris le super admin dans le dropdown bénéficiaire | Logique métier incorrecte |
| M-4 | Base de données | — | **0 affectation** en base → les employés voient des écrans vides à la démo | Démo non fonctionnelle pour employés |

### 🟡 MINEURS

| # | Fichier | Description |
|---|---|---|
| m-1 | resources_view.py | Le filtre "Entreprise" du dropdown (admin) convertit company_id en str pour comparer — fonctionne mais fragile |
| m-2 | auth_controller.py | `_log_failed_login()` ouvre une session imbriquée à l'intérieur de `with get_session()` — fonctionne mais 2 connexions simultanées inutiles |
| m-3 | assignments_view.py | La clôture d'affectation ne met pas à jour la vue Ressources ouverte en parallèle |

---

## 4. Cohérence des rôles

### Permissions en base

| Rôle | Permissions |
|---|---|
| super_admin | `["all"]` |
| admin | `view_resources, manage_resources, view_users, manage_users, view_logs, generate_contracts, view_assignments, manage_assignments` |
| employee | `view_own_resources, view_own_assignments, sign_contracts, view_own_history` |

### Menus visibles par rôle

| Menu | Super Admin | Admin | Employé |
|---|---|---|---|
| Tableau de bord | ✅ | ✅ | ✅ |
| Utilisateurs | ✅ | ✅ | ❌ caché |
| Entreprises | ✅ | ❌ caché | ❌ caché |
| Ressources | ✅ (tout) | ✅ (tout) | ✅ (ses ressources) |
| Affectations | ✅ (tout) | ✅ (tout) | ✅ (ses affectations) |
| Contrats | ✅ | ✅ | ✅ ⚠️ voit tout (bug M-2) |
| Journaux d'audit | ✅ | ✅ | ❌ caché |
| Déconnexion | ✅ | ✅ | ✅ |

### Incohérence identifiée

- **Employé → Contrats** : l'employé a la permission `sign_contracts` et voit l'onglet "Contrats", mais la vue ne filtre pas ses contrats → il voit tous les contrats de l'entreprise. À corriger.
- **AssignmentFormDialog** : liste tous les users actifs sans exclure le super_admin (qui n'a pas de company_id). À corriger.

---

## 5. État des données de démo

| Table | Enregistrements |
|---|---|
| companies | 1 (CleanPro Nettoyage) |
| resource_types | 4 |
| resources | 20 |
| users | 5 (1 super_admin, 1 admin, 3 employees) |
| assignments | **0** ← problème démo |
| contracts | 0 |
| audit_logs | quelques-uns (logins) |

**Problème** : sans affectation, les employés verront des tableaux vides. Il faut créer des affectations de test.

---

## 6. Plan d'action priorisé

### P0 — Données de démo (immédiat, 5 min)
- Créer 3 affectations test (une ressource par employé)

### P1 — Bug ligne 205 contracts_view.py (2 min)
- Supprimer la ligne morte

### P2 — Filtre contrats pour employé (15 min)
- Adapter `ContractsView` comme `ResourcesView` : si employé → ne montrer que ses contrats

### P3 — Dropdown bénéficiaire sans super_admin (5 min)
- Filtrer `AssignmentFormDialog.user_combo` pour exclure les super_admin

---

## 7. Ce qui n'a PAS été modifié (fonctionne)

- Login / Logout ✅
- Toute la gestion des ressources ✅
- Toute la gestion des utilisateurs ✅
- Toute la gestion des entreprises ✅
- Les journaux d'audit ✅
- La génération de PDF ✅
- La sécurité (bcrypt, tokens, lockout) ✅
