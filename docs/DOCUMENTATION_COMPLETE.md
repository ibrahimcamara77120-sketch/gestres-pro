# GestRes Pro — Documentation complète de A à Z

**Auteur : CAMARA Ibrahim — BTS SIO SLAM 2026**  
**Projet : Application de gestion de ressources d'entreprise**  
**Date : Juin 2026**

---

> 📖 Ce document explique **tout** ce qui a été fait dans ce projet : les outils utilisés, comment le code est organisé, ce que fait chaque fichier, chaque fonction, chaque table. Il est écrit pour que tu puisses relire ton propre projet et l'expliquer à n'importe qui.

---

## Table des matières

1. [Vue d'ensemble du projet](#1-vue-densemble-du-projet)
2. [Stack technique — Les outils utilisés](#2-stack-technique--les-outils-utilisés)
3. [Architecture MVC — Comment le code est organisé](#3-architecture-mvc--comment-le-code-est-organisé)
4. [La base de données PostgreSQL](#4-la-base-de-données-postgresql)
5. [Les Modèles SQLAlchemy](#5-les-modèles-sqlalchemy-srcmodels)
6. [La sécurité](#6-la-sécurité-srcutilssecuritypy)
7. [Les Contrôleurs](#7-les-contrôleurs-srccontrollers)
8. [Les Vues PySide6](#8-les-vues-pyside6-srcviews)
9. [Les utilitaires](#9-les-utilitaires-srcutils)
10. [Les Tests](#10-les-tests-tests)
11. [La configuration](#11-la-configuration-configpy--env)
12. [Le démarrage de l'application](#12-le-démarrage-de-lapplication-mainpy)
13. [Conformité RGPD](#13-conformité-rgpd)
14. [Glossaire](#14-glossaire)

---

## 1. Vue d'ensemble du projet

### 🎯 Ce qu'est GestRes Pro

GestRes Pro est une **application de bureau** (desktop) qui permet à une entreprise de gérer et de suivre l'ensemble de ses ressources (ordinateurs, téléphones, véhicules, badges, comptes logiciels, etc.) : qui les utilise, depuis quand, avec un contrat signé, et un historique complet de chaque mouvement.

### 🔴 Le problème qu'il résout

Dans une entreprise, le service informatique doit savoir en permanence :
- Quel employé utilise quel ordinateur ?
- Ce MacBook Pro a-t-il été rendu ?
- Qui a eu accès à ce compte logiciel ?
- Y a-t-il un contrat signé pour cette attribution ?

Sans outil dédié, tout ça se fait dans des tableaux Excel qui sont souvent perdus, pas à jour, ou non sécurisés. GestRes Pro centralise tout ça dans une application sécurisée avec base de données.

### 👥 Les 3 types d'utilisateurs

| Rôle | Nom affiché | Ce qu'il peut faire |
|------|-------------|---------------------|
| `super_admin` | Super Administrateur | Tout : créer les espaces entreprise, configurer les types de ressources, créer tous les comptes |
| `admin` | Administrateur Entreprise | Gérer les ressources, utilisateurs, affectations, contrats et logs de son entreprise |
| `employee` | Employé | Voir ses propres ressources affectées, consulter son historique, signer ses contrats |

### ✅ Liste des fonctionnalités

- 🔐 Authentification sécurisée (email + mot de passe bcrypt) avec blocage après 5 tentatives
- 👥 Gestion des utilisateurs (CRUD + rôles + désactivation)
- 🏢 Gestion multi-entreprises (chaque entreprise est cloisonnée)
- 🖥️ Gestion des ressources avec types personnalisables et champs libres
- 📋 Affectations ressource ↔ utilisateur avec dates et notes
- 📄 Génération et signature de contrats avec intégrité SHA-256
- 📊 Journal d'audit complet (qui a fait quoi, quand, depuis quelle IP)
- 💾 Sauvegarde automatique PostgreSQL (pg_dump) au démarrage
- 🧹 Purge automatique des sessions expirées et logs anciens (RGPD)
- 🔍 Filtres et recherche dans toutes les listes
- 🎨 Interface graphique moderne avec design indigo/violet

---

## 2. Stack technique — Les outils utilisés

### 🐍 Python 3.14

**Ce que c'est :** Le langage de programmation principal. Python est simple à lire, très populaire en entreprise et dispose d'une immense bibliothèque d'outils.

**Pourquoi ce choix :** Python est au programme du BTS SIO SLAM, il est rapide à développer, et la communauté est immense. La version 3.14 apporte des améliorations de performance.

**Comment il est utilisé :** Tout le code de l'application (modèles, contrôleurs, vues, utilitaires, tests) est écrit en Python.

---

### 🖥️ PySide6 (Qt for Python)

**Ce que c'est :** Une bibliothèque qui permet de créer des applications avec une interface graphique (fenêtres, boutons, tableaux, formulaires). C'est le binding Python officiel du framework Qt.

**Pourquoi ce choix :** Qt est un framework de niveau professionnel utilisé en entreprise (Tesla, Adobe, etc.). PySide6 est la version officielle maintenue par Qt Company. Il permet de créer des applications qui ressemblent à de vraies applications desktop.

**Comment il est utilisé :** Toutes les vues sont des widgets PySide6 :
```python
# src/views/login_view.py — exemple
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PySide6.QtCore import Signal

class LoginView(QWidget):
    login_successful = Signal()  # signal émis quand la connexion réussit
```

---

### 🗄️ SQLAlchemy 2.0 (ORM)

**Ce que c'est :** Un ORM (Object-Relational Mapper). En clair : un outil qui te permet d'écrire du Python au lieu d'écrire du SQL brut pour parler à la base de données.

**Pourquoi ce choix :** SQLAlchemy évite les injections SQL (une faille de sécurité majeure), rend le code plus lisible, et permet de changer de base de données (SQLite, PostgreSQL, MySQL) sans réécrire tout le code.

**Comment il est utilisé :**
```python
# Exemple dans src/controllers/user_controller.py
# Au lieu d'écrire : SELECT * FROM users WHERE email = 'test@test.com'
# On écrit :
user = session.query(User).filter_by(email="test@test.com").first()
```

---

### 🐘 PostgreSQL 16

**Ce que c'est :** Un système de gestion de bases de données relationnelles (SGBD) professionnel, open source, reconnu dans l'industrie depuis plus de 25 ans.

**Pourquoi ce choix :** PostgreSQL est utilisé par des millions d'entreprises (Instagram, Spotify, Skype). Il supporte les transactions, les triggers, les vues, les fonctions stockées, les contraintes avancées — tout ce dont ce projet a besoin. SQLite aurait été insuffisant pour un projet en production car il ne supporte pas plusieurs connexions simultanées.

**Comment il est utilisé :** La base `gestres_pro` tourne en local sur le port 5432. L'application s'y connecte via le fichier `.env`.

---

### 🔌 psycopg2-binary

**Ce que c'est :** Le pilote (driver) Python pour PostgreSQL. C'est le "traducteur" entre SQLAlchemy et PostgreSQL.

**Pourquoi ce choix :** C'est le driver PostgreSQL le plus utilisé en Python, recommandé par SQLAlchemy. La version `-binary` inclut tout ce qu'il faut sans compilation.

**Comment il est utilisé :** Dans `config.py`, l'URL de connexion spécifie explicitement ce driver :
```python
DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
```

---

### 🔐 bcrypt

**Ce que c'est :** Un algorithme de hachage de mots de passe. Il transforme un mot de passe en une chaîne illisible et impossible à reconstituer.

**Pourquoi ce choix :** bcrypt est l'algorithme recommandé par l'ANSSI (l'agence nationale de cybersécurité française) pour stocker les mots de passe. Contrairement à MD5 ou SHA-256 (qui sont rapides), bcrypt est volontairement lent, ce qui rend les attaques par force brute impossibles en pratique.

**Comment il est utilisé :**
```python
# src/utils/security.py
import bcrypt
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt(rounds=12)  # 12 rounds = très sécurisé
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")
```

---

### 🌍 python-dotenv

**Ce que c'est :** Une bibliothèque qui lit un fichier `.env` et charge les variables dans l'environnement Python.

**Pourquoi ce choix :** On ne met jamais les mots de passe dans le code source (qui peut être partagé sur GitHub). Le fichier `.env` reste local sur ta machine et n'est jamais commité.

**Comment il est utilisé :**
```python
# config.py
from dotenv import load_dotenv
load_dotenv(BASE_DIR / ".env")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
```

---

### 📄 reportlab

**Ce que c'est :** Une bibliothèque Python pour générer des fichiers PDF.

**Pourquoi ce choix :** C'est la bibliothèque PDF la plus mature et complète en Python. Elle permet de créer des PDFs professionnels avec mise en page, tableaux, images.

**Comment il est utilisé :** Dans le contrôleur de contrats (`src/controllers/contract_controller.py`) pour générer les contrats d'affectation en PDF.

---

### 🧪 pytest

**Ce que c'est :** Le framework de tests automatisés le plus utilisé en Python. Il permet d'écrire des tests qui vérifient que le code fonctionne correctement.

**Pourquoi ce choix :** pytest est simple, puissant, et affiche des rapports clairs. Il est le standard de l'industrie Python pour les tests.

**Comment il est utilisé :** 155 tests couvrent la sécurité, les modèles et les contrôleurs :
```bash
python -m pytest tests/ -v  # lance tous les tests
```

---

## 3. Architecture MVC — Comment le code est organisé

### 🏗️ Qu'est-ce que le MVC ?

MVC signifie **Modèle - Vue - Contrôleur**. C'est une façon d'organiser le code en 3 parties qui ont chacune un rôle précis.

**Analogie simple** : Pense à un restaurant.
- Le **Modèle** = la cuisine et les ingrédients (les données brutes)
- Le **Contrôleur** = le serveur (il prend la commande, va chercher ce qu'il faut en cuisine, et l'apporte)
- La **Vue** = la salle du restaurant (ce que le client voit)

### 📁 Organisation des dossiers

```
PythonProject/
│
├── main.py                    ← Point d'entrée (démarre l'app)
├── config.py                  ← Configuration globale (BDD, constantes)
├── .env                       ← Credentials (NON commité)
├── .env.example               ← Template des credentials (commité)
├── requirements.txt           ← Liste des dépendances
├── database_setup.sql         ← Script SQL complet PostgreSQL
│
├── src/
│   ├── models/                ← MODÈLE : les tables/données
│   │   ├── base.py            ← Connexion BDD + session
│   │   ├── user.py            ← Table users + roles
│   │   ├── company.py         ← Table companies
│   │   ├── resource.py        ← Table resources
│   │   ├── resource_type.py   ← Table resource_types
│   │   ├── assignment.py      ← Table assignments
│   │   ├── contract.py        ← Table contracts
│   │   └── audit_log.py       ← Tables audit_logs + sessions
│   │
│   ├── controllers/           ← CONTRÔLEUR : la logique métier
│   │   ├── auth_controller.py     ← Connexion, sessions, permissions
│   │   ├── user_controller.py     ← CRUD utilisateurs
│   │   ├── company_controller.py  ← CRUD entreprises
│   │   ├── resource_controller.py ← CRUD ressources
│   │   ├── assignment_controller.py ← Gestion affectations
│   │   └── contract_controller.py   ← Génération contrats
│   │
│   ├── views/                 ← VUE : l'interface graphique
│   │   ├── styles.py          ← Palette de couleurs + styles CSS
│   │   ├── main_window.py     ← Fenêtre principale
│   │   ├── login_view.py      ← Écran de connexion
│   │   ├── dashboard_view.py  ← Tableau de bord + sidebar
│   │   ├── users_view.py      ← Page gestion utilisateurs
│   │   ├── resources_view.py  ← Page gestion ressources
│   │   ├── companies_view.py  ← Page gestion entreprises
│   │   ├── assignments_view.py ← Page affectations
│   │   ├── contracts_view.py  ← Page contrats
│   │   ├── logs_view.py       ← Page journaux d'audit
│   │   └── widgets/
│   │       └── data_table.py  ← Composant tableau réutilisable
│   │
│   └── utils/                 ← Utilitaires transversaux
│       ├── security.py        ← Hachage, tokens, validations
│       ├── backup.py          ← Sauvegarde automatique
│       ├── maintenance.py     ← Purge sessions/logs
│       └── validators.py      ← Classes de validation
│
├── tests/                     ← Tests automatisés
│   ├── conftest.py            ← Configuration des tests
│   ├── test_security.py       ← 40 tests sécurité
│   ├── test_models.py         ← 52 tests modèles
│   └── test_controllers.py    ← 63 tests contrôleurs
│
└── docs/                      ← Documentation
    └── DOCUMENTATION_COMPLETE.md  ← Ce fichier
```

### 🔄 Comment les 3 couches communiquent

Voici un exemple concret : l'utilisateur clique sur "Se connecter".

```
VUE (login_view.py)
  ↓ appelle
CONTRÔLEUR (auth_controller.py → login())
  ↓ interroge
MODÈLE (user.py → session.query(User).filter_by(email=...))
  ↓ lit dans
BASE DE DONNÉES (PostgreSQL → table users)
  ↑ retourne l'objet User
CONTRÔLEUR
  ↑ retourne (True, "Bienvenue, Ibrahim!")
VUE
  ↑ émet le signal login_successful → affiche le dashboard
```

**Pourquoi cette architecture ?**
- Chaque partie peut évoluer indépendamment (changer la vue sans toucher à la logique)
- Plus facile à tester (on teste le contrôleur sans l'interface graphique)
- Code plus propre et maintenable

---

## 4. La base de données PostgreSQL

### 4.1 Pourquoi PostgreSQL et pas SQLite

| Critère | SQLite | PostgreSQL |
|---------|--------|------------|
| Connexions simultanées | 1 seule | Jusqu'à 50 (configuré dans ce projet) |
| Taille maximale | ~281 To théorique mais limité en pratique | Illimitée |
| Triggers et fonctions | Limités | Complets (PL/pgSQL) |
| Niveau professionnel | Non | Oui |
| Utilisé en production | Rarement (mobile/embed) | Instagram, Spotify, etc. |
| Droits utilisateurs | Non | Oui (gestion fine) |

SQLite était utilisé au début du projet (version locale), mais a été migré vers PostgreSQL pour répondre aux critères E6 BTS et pour avoir une architecture client-serveur réelle.

---

### 4.2 Les 10 tables

#### Table `roles`
**À quoi ça sert :** Stocke les 3 rôles du système (super_admin, admin, employee).

| Colonne | Type | Rôle |
|---------|------|------|
| `id` | SERIAL (auto) | Identifiant unique |
| `name` | VARCHAR(50) | Nom technique du rôle (`super_admin`, `admin`, `employee`) |
| `permissions` | TEXT | Liste JSON des permissions : `["all"]` ou `["view_resources", "manage_users", ...]` |

**Contrainte :** `CHECK (name IN ('super_admin', 'admin', 'employee'))` — empêche d'insérer n'importe quoi comme rôle.

**Relations :** Un rôle est lié à plusieurs utilisateurs (1 rôle → N users).

---

#### Table `companies`
**À quoi ça sert :** Chaque entreprise cliente a son propre espace cloisonné. Les ressources et utilisateurs d'une entreprise ne sont pas visibles par une autre.

| Colonne | Type | Rôle |
|---------|------|------|
| `id` | SERIAL | Identifiant unique |
| `name` | VARCHAR(100) | Nom de l'entreprise |
| `siret` | VARCHAR(14) | Numéro SIRET (optionnel, validé avec algorithme de Luhn) |
| `address` | TEXT | Adresse postale |
| `created_at` | TIMESTAMPTZ | Date de création (avec fuseau horaire) |
| `is_active` | BOOLEAN | `TRUE` = active, `FALSE` = désactivée (soft delete) |

**Contrainte :** `CHECK (siret ~ '^\d{14}$')` — le SIRET doit être exactement 14 chiffres.

---

#### Table `users`
**À quoi ça sert :** Stocke tous les comptes utilisateurs. Le mot de passe n'est JAMAIS stocké en clair.

| Colonne | Type | Rôle |
|---------|------|------|
| `id` | SERIAL | Identifiant unique |
| `email` | VARCHAR(100) | Adresse email (unique) |
| `password_hash` | VARCHAR(255) | Hash bcrypt du mot de passe (jamais le mot de passe en clair) |
| `first_name` | VARCHAR(50) | Prénom |
| `last_name` | VARCHAR(50) | Nom de famille |
| `role_id` | INTEGER | Référence vers la table `roles` (clé étrangère) |
| `company_id` | INTEGER | Référence vers la table `companies` (NULL pour super_admin) |
| `is_active` | BOOLEAN | Compte actif ou désactivé (jamais supprimé physiquement) |
| `created_at` | TIMESTAMPTZ | Date de création |
| `last_login` | TIMESTAMPTZ | Date de la dernière connexion (mis à jour par trigger) |

**Contrainte email :** `CHECK (email ~ '^[^@]+@[^@]+\.[^@]+$')` — doit ressembler à une adresse email.

**Relations :** Un user appartient à 1 rôle et 1 entreprise. Il peut avoir N affectations, N sessions, N logs d'audit.

---

#### Table `resource_types`
**À quoi ça sert :** Définit les catégories de ressources configurables par chaque entreprise. Ex: "Ordinateur portable", "Téléphone", "Véhicule".

| Colonne | Type | Rôle |
|---------|------|------|
| `id` | SERIAL | Identifiant unique |
| `company_id` | INTEGER | Entreprise propriétaire |
| `name` | VARCHAR(100) | Nom du type (ex: "Ordinateur portable") |
| `description` | TEXT | Description optionnelle |
| `custom_fields` | TEXT | JSON définissant des champs supplémentaires (ex: `[{"name":"ram","label":"RAM"}]`) |

---

#### Table `resources`
**À quoi ça sert :** Une ressource = un objet physique ou numérique géré (un MacBook Pro précis, un badge X, etc.).

| Colonne | Type | Rôle |
|---------|------|------|
| `id` | SERIAL | Identifiant unique |
| `company_id` | INTEGER | Entreprise propriétaire |
| `resource_type_id` | INTEGER | Type de la ressource |
| `name` | VARCHAR(100) | Nom descriptif (ex: "MacBook Pro 14 - Ibrahim") |
| `serial_number` | VARCHAR(100) | Numéro de série (unique, optionnel) |
| `status` | VARCHAR(20) | État actuel : `available`, `assigned`, `maintenance`, `retired` |
| `custom_data` | TEXT | JSON avec données spécifiques (ex: `{"ram":"16GB","storage":"512GB"}`) |
| `purchase_date` | DATE | Date d'achat |
| `end_of_life_date` | DATE | Date de fin de vie prévue |
| `created_at` | TIMESTAMPTZ | Date d'ajout dans le système |

**Contrainte statut :** `CHECK (status IN ('available', 'assigned', 'maintenance', 'retired'))` — 4 états possibles seulement.

**Important :** Le statut est mis à jour **automatiquement** par un trigger quand une affectation est créée ou clôturée.

---

#### Table `assignments`
**À quoi ça sert :** Enregistre qu'une ressource est attribuée à un utilisateur pour une période donnée.

| Colonne | Type | Rôle |
|---------|------|------|
| `id` | SERIAL | Identifiant unique |
| `resource_id` | INTEGER | La ressource affectée |
| `user_id` | INTEGER | L'utilisateur qui reçoit la ressource |
| `assigned_by` | INTEGER | L'admin qui a fait l'affectation |
| `start_date` | TIMESTAMPTZ | Date de début |
| `end_date` | TIMESTAMPTZ | Date de fin (NULL si encore active) |
| `status` | VARCHAR(20) | `active`, `returned`, `cancelled` |
| `notes` | TEXT | Notes libres |

**Contrainte :** `CHECK (end_date IS NULL OR end_date >= start_date)` — la fin ne peut pas être avant le début.

---

#### Table `contracts`
**À quoi ça sert :** Chaque affectation peut générer un contrat. Le contrat est stocké avec une empreinte SHA-256 pour garantir qu'il n'a pas été modifié après signature.

| Colonne | Type | Rôle |
|---------|------|------|
| `id` | SERIAL | Identifiant unique |
| `assignment_id` | INTEGER | L'affectation concernée |
| `content` | TEXT | Contenu textuel du contrat |
| `content_hash` | VARCHAR(64) | SHA-256 du contenu (pour vérifier l'intégrité) |
| `generated_at` | TIMESTAMPTZ | Date de génération |
| `signed_at` | TIMESTAMPTZ | Date de signature (NULL si non signé) |
| `signature_hash` | VARCHAR(64) | Hash de la signature |
| `pdf_path` | VARCHAR(255) | Chemin vers le PDF généré |

**Contrainte intégrité :** `CHECK ((signed_at IS NULL) = (signature_hash IS NULL))` — soit les deux sont NULL (non signé), soit les deux ont une valeur (signé).

---

#### Table `audit_logs`
**À quoi ça sert :** Trace toutes les actions importantes dans l'application : connexions, créations, modifications, suppressions.

| Colonne | Type | Rôle |
|---------|------|------|
| `id` | SERIAL | Identifiant unique |
| `user_id` | INTEGER | Qui a fait l'action (peut être NULL) |
| `action` | VARCHAR(50) | Type d'action : `LOGIN`, `LOGOUT`, `LOGIN_FAILED`, `CREATE`, `UPDATE`, `DELETE`, `PASSWORD_CHANGE`, `PASSWORD_RESET` |
| `table_name` | VARCHAR(50) | Sur quelle table (ex: `users`, `resources`) |
| `record_id` | INTEGER | L'ID de l'enregistrement concerné |
| `old_values` | TEXT | JSON des anciennes valeurs (avant modification) |
| `new_values` | TEXT | JSON des nouvelles valeurs (après modification) |
| `ip_address` | VARCHAR(45) | Adresse IP de l'utilisateur |
| `created_at` | TIMESTAMPTZ | Quand ça s'est passé |

---

#### Table `sessions`
**À quoi ça sert :** Stocke les sessions actives des utilisateurs connectés. Quand tu te connectes, une session est créée avec un token chiffré. Quand tu te déconnectes, elle est supprimée.

| Colonne | Type | Rôle |
|---------|------|------|
| `id` | SERIAL | Identifiant unique |
| `user_id` | INTEGER | L'utilisateur connecté |
| `token_hash` | VARCHAR(64) | SHA-256 du token de session (jamais le token en clair) |
| `created_at` | TIMESTAMPTZ | Quand la session a été créée |
| `expires_at` | TIMESTAMPTZ | Quand la session expire (8h après création) |

---

#### Table `journal_modifications`
**À quoi ça sert :** C'est un journal bas niveau géré par les **triggers PostgreSQL** (pas par l'application Python). Il enregistre automatiquement chaque INSERT, UPDATE, DELETE sur les tables sensibles, en capturant les données avant et après avec JSONB.

| Colonne | Type | Rôle |
|---------|------|------|
| `id` | BIGSERIAL | Identifiant unique (BIGSERIAL = peut aller très haut) |
| `table_name` | VARCHAR(50) | La table modifiée |
| `operation` | VARCHAR(10) | `INSERT`, `UPDATE` ou `DELETE` |
| `record_id` | INTEGER | ID de l'enregistrement modifié |
| `old_data` | JSONB | Données complètes avant modification |
| `new_data` | JSONB | Données complètes après modification |
| `pg_user` | VARCHAR(100) | L'utilisateur PostgreSQL qui a fait l'opération |
| `created_at` | TIMESTAMPTZ | Horodatage automatique |

---

### 4.3 Les contraintes d'intégrité

Une contrainte est une règle que PostgreSQL applique automatiquement et qui refuse toute donnée invalide.

**Clé étrangère (FOREIGN KEY / FK) :** Empêche d'insérer un `user_id` dans `assignments` si cet utilisateur n'existe pas dans `users`. C'est comme un lien entre deux tables.

```sql
-- Si on essaie d'affecter une ressource à user_id=999 qui n'existe pas → ERREUR
resource_id INTEGER NOT NULL REFERENCES resources(id)
```

**Contrainte CHECK :** Valide une valeur selon une règle logique.
```sql
-- Le statut ne peut être QUE l'une de ces 4 valeurs
CONSTRAINT chk_resources_status CHECK (status IN ('available', 'assigned', 'maintenance', 'retired'))
```

**Contrainte UNIQUE :** Interdit les doublons sur une colonne.
```sql
-- Deux utilisateurs ne peuvent pas avoir le même email
email VARCHAR(100) NOT NULL UNIQUE
```

---

### 4.4 Les 13 index

Un index est comme l'index d'un livre : au lieu de lire toutes les pages pour trouver un mot, tu vas directement à la bonne page. Sans index, PostgreSQL parcourt toute la table ligne par ligne.

| Index | Table | Colonne | Pourquoi |
|-------|-------|---------|----------|
| `idx_users_email` | users | email | La connexion cherche toujours par email |
| `idx_users_company` | users | company_id | Filtrer les users par entreprise |
| `idx_users_role` | users | role_id | Filtrer les users par rôle |
| `idx_resources_company` | resources | company_id | Afficher les ressources d'une entreprise |
| `idx_resources_status` | resources | status | Filtrer par statut (disponible, affectée...) |
| `idx_assignments_resource` | assignments | resource_id | Historique d'une ressource |
| `idx_assignments_user` | assignments | user_id | Affectations d'un utilisateur |
| `idx_assignments_status` | assignments | status | Filtrer les affectations actives |
| `idx_audit_logs_user` | audit_logs | user_id | Journal d'un utilisateur |
| `idx_audit_logs_date` | audit_logs | created_at | Filtrer les logs par date |
| `idx_sessions_user` | sessions | user_id | Sessions d'un user |
| `idx_sessions_expires` | sessions | expires_at | Purger les sessions expirées |
| `idx_journal_table` | journal_modifications | table_name, created_at | Audit par table et date |

---

### 4.5 Les 5 vues SQL

Une vue SQL est une requête sauvegardée. On l'interroge comme une table mais elle combine plusieurs tables automatiquement.

#### `v_ressources_disponibles`
**Retourne :** Toutes les ressources dont le statut est `available`, avec le nom de leur type et leur entreprise.  
**Cas d'usage :** Afficher rapidement les ressources disponibles à l'affectation.

#### `v_affectations_actives`
**Retourne :** Toutes les affectations en cours avec : nom de la ressource, nom de l'utilisateur, email, qui a fait l'affectation, depuis combien de temps.  
**Cas d'usage :** Tableau de bord des affectations en cours.

#### `v_tableau_de_bord`
**Retourne :** Par entreprise : nombre d'utilisateurs actifs, total ressources, disponibles, affectées, en maintenance, affectations actives, contrats signés.  
**Cas d'usage :** Les statistiques du tableau de bord principal.

#### `v_historique_ressources`
**Retourne :** L'historique complet de chaque ressource — qui l'a eue, quand, avec quel contrat.  
**Cas d'usage :** Voir toute la vie d'un équipement.

#### `v_activite_utilisateurs`
**Retourne :** Pour chaque utilisateur actif : son rôle, entreprise, date de dernière connexion, nombre d'actions dans les 30 derniers jours.  
**Cas d'usage :** Surveiller l'activité des comptes.

---

### 4.6 Les 4 fonctions PL/pgSQL

PL/pgSQL est le langage de programmation intégré à PostgreSQL. Les fonctions s'exécutent directement dans la base de données.

#### `fn_anonymize_user(user_id INTEGER)`
**Ce qu'elle fait :** Anonymise toutes les données personnelles d'un utilisateur pour respecter le droit à l'oubli RGPD. Elle remplace email, prénom, nom par des valeurs neutres et supprime ses sessions.  
**Comment l'appeler :**
```sql
SELECT fn_anonymize_user(42);  -- anonymise l'utilisateur n°42
```

#### `fn_purge_sessions_expirees()`
**Ce qu'elle fait :** Supprime toutes les sessions dont la date d'expiration est dépassée. Retourne le nombre de sessions supprimées.  
**Comment l'appeler :**
```sql
SELECT fn_purge_sessions_expirees();  -- retourne ex: 15
```

#### `fn_stats_entreprise(company_id INTEGER)`
**Ce qu'elle fait :** Retourne un tableau de statistiques (ressources totales, disponibles, affectations actives, contrats signés, utilisateurs actifs) pour une entreprise donnée.  
**Comment l'appeler :**
```sql
SELECT * FROM fn_stats_entreprise(1);
-- indicateur            | valeur
-- Ressources totales    | 42
-- Ressources disponibles| 28
-- ...
```

#### `fn_ressources_fin_de_vie(jours INTEGER DEFAULT 90)`
**Ce qu'elle fait :** Retourne les ressources dont la date de fin de vie arrive dans les `jours` prochains jours. Très utile pour anticiper les remplacements.  
**Comment l'appeler :**
```sql
SELECT * FROM fn_ressources_fin_de_vie(30);  -- dans les 30 prochains jours
```

---

### 4.7 Les 8 triggers

Un trigger est un code qui s'exécute automatiquement quand quelque chose se passe dans la base (INSERT, UPDATE, DELETE). Pas besoin d'y penser dans le code Python — la base le fait toute seule.

| Trigger | Table | Quand | Ce qu'il fait |
|---------|-------|-------|---------------|
| `trg_audit_users` | users | Après INSERT/UPDATE/DELETE | Écrit dans `journal_modifications` ce qui a changé |
| `trg_audit_resources` | resources | Après INSERT/UPDATE/DELETE | Idem pour les ressources |
| `trg_audit_assignments` | assignments | Après INSERT/UPDATE/DELETE | Idem pour les affectations |
| `trg_audit_companies` | companies | Après INSERT/UPDATE/DELETE | Idem pour les entreprises |
| `trg_resource_status` | assignments | Avant INSERT/UPDATE | Met le statut de la ressource à `assigned` quand une affectation active est créée, ou à `available` quand elle est clôturée |
| `trg_check_availability` | assignments | Avant INSERT | Bloque l'affectation si la ressource n'est pas disponible (statut ≠ `available`) |
| `trg_session_created` | sessions | Après INSERT | Met à jour `last_login` de l'utilisateur automatiquement |

> 💡 **Exemple concret du trigger `trg_resource_status` :**  
> Quand l'admin crée une affectation pour le MacBook Pro → le trigger change automatiquement le statut du MacBook Pro de `available` à `assigned`. Pas besoin de faire ça dans le code Python, la base le gère.

---

### 4.8 Les droits utilisateur (gestres_user)

Dans la base de données, l'application utilise l'utilisateur `gestres_user` et non le superuser (`postgres`). Pourquoi ?

- 🔐 **Principe du moindre privilège** : si l'application est compromise, l'attaquant ne peut pas faire `DROP DATABASE` ou créer de nouveaux utilisateurs PostgreSQL.
- `gestres_user` a le droit de : SELECT, INSERT, UPDATE, DELETE sur toutes les tables
- `gestres_user` n'a **pas** le droit de : créer des tables, supprimer la base, créer d'autres utilisateurs

```sql
-- Ce que gestres_user peut faire
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO gestres_user;

-- Ce qu'il NE peut PAS faire (pas de SUPERUSER, pas de CREATEDB)
CREATE USER gestres_user WITH PASSWORD '...' NOSUPERUSER NOCREATEDB NOCREATEROLE LOGIN;
```

---

## 5. Les Modèles SQLAlchemy (`src/models/`)

### 5.1 Qu'est-ce qu'un ORM et pourquoi c'est important

Un ORM (Object-Relational Mapper) fait la traduction entre le monde Python (des objets) et le monde SQL (des tables).

**Sans ORM** (dangereux !) :
```python
# Injection SQL possible si email contient des caractères malveillants !
cursor.execute(f"SELECT * FROM users WHERE email = '{email}'")
```

**Avec SQLAlchemy ORM** (sécurisé) :
```python
# SQLAlchemy échappe automatiquement les paramètres → injection SQL impossible
user = session.query(User).filter_by(email=email).first()
```

L'ORM protège aussi de la faille la plus courante du web : **l'injection SQL**.

---

### 5.2 `base.py` — Le moteur de connexion

**Fichier :** `src/models/base.py`

#### Le moteur (engine)
```python
engine = create_engine(
    config.DATABASE_URL,  # "postgresql+psycopg2://user:pwd@host:port/db"
    echo=False,           # ne pas afficher le SQL dans la console
    pool_size=5,          # garder 5 connexions ouvertes en permanence
    max_overflow=10,      # accepter jusqu'à 10 connexions supplémentaires si besoin
    pool_pre_ping=True,   # tester si la connexion est encore valide avant de l'utiliser
)
```

**Pool de connexions :** Au lieu d'ouvrir une nouvelle connexion à PostgreSQL à chaque requête (lent), on garde un "pool" de connexions prêtes. Comme un vestiaire avec des casiers déjà ouverts.

**`pool_pre_ping=True` :** Si la connexion PostgreSQL a été coupée (redémarrage serveur, timeout), SQLAlchemy teste automatiquement si la connexion est encore vivante avant de l'utiliser, et en crée une nouvelle si besoin.

#### La session (contextmanager)
```python
@contextmanager
def get_session() -> SASession:
    session = SessionLocal()
    try:
        yield session          # donne la session au code appelant
    except Exception:
        session.rollback()     # si erreur → annule tout (transaction)
        raise
    finally:
        session.close()        # ferme toujours la session, même si erreur
```

**Comment l'utiliser :**
```python
with get_session() as session:
    user = session.query(User).filter_by(id=1).first()
    # si une erreur se produit ici → session.rollback() automatique
# session fermée automatiquement à la sortie du "with"
```

**`init_db()` :** Appelée au démarrage dans `main.py`. Elle crée toutes les tables dans PostgreSQL si elles n'existent pas, puis insère les 3 rôles par défaut.

---

### 5.3 Les modèles détaillés

#### `user.py` — Utilisateurs et Rôles

**Classe `Role` :**
- Représente un rôle système (super_admin, admin, employee)
- `get_permissions()` → retourne la liste Python des permissions depuis le JSON stocké en base
- `has_permission(permission)` → retourne `True` si le rôle a cette permission (ou si la permission `"all"` est présente)

**Classe `User` :**
- `full_name` (propriété) → retourne "Prénom Nom", ou juste le prénom, ou l'email si les deux sont vides
- `has_permission(permission)` → délègue au rôle associé
- Relations : appartient à 1 `Role`, 1 `Company`. A N `Assignment`, N `Session`, N `AuditLog`.

---

#### `company.py` — Entreprises

Représente un espace entreprise. Chaque entreprise possède ses propres utilisateurs, ressources et types de ressources.

- `is_active` = `False` → entreprise désactivée (soft delete, les données restent)
- Cascade `all, delete-orphan` sur les users, resource_types et resources : si l'entreprise est supprimée en base, tout ce qui lui appartient est supprimé aussi.

---

#### `resource.py` — Ressources

- `get_custom_data()` / `set_custom_data(dict)` : lit/écrit les données JSON du champ `custom_data`
- `is_available` (propriété) : retourne `True` si `status == "available"`
- `current_assignment` (propriété) : retourne l'affectation active actuelle ou `None`

---

#### `resource_type.py` — Types de ressources

- `get_custom_fields()` / `set_custom_fields(list)` : les champs personnalisés sont stockés en JSON. Ex : `[{"name": "ram", "type": "string", "label": "RAM"}]`

---

#### `assignment.py` — Affectations

- `is_active` (propriété) : `True` si `status == "active"`
- `duration_days` (propriété) : calcule le nombre de jours de l'affectation (de `start_date` à `end_date` ou à maintenant si encore active)

---

#### `contract.py` — Contrats

- `compute_hash(content)` (méthode statique) : calcule le SHA-256 d'un texte
- `verify_integrity()` : vérifie que le contenu du contrat n'a pas été modifié en comparant le hash stocké avec un recalcul
- `sign(signer_data)` : signe le contrat en enregistrant la date et en calculant un hash de signature
- `is_signed` (propriété) : `True` si `signed_at` et `signature_hash` sont remplis

---

#### `audit_log.py` — Logs et Sessions

**Classe `AuditLog` :**
- `AuditLog.log(action, user_id, table_name, ...)` : méthode de classe pour créer facilement un log
- `get_old_values()` / `get_new_values()` : désérialise le JSON des valeurs

**Classe `Session` :**
- `is_expired` (propriété) : compare `expires_at` avec l'heure actuelle
- `is_valid` (propriété) : inverse de `is_expired`

---

## 6. La sécurité (`src/utils/security.py`)

### 🔐 `hash_password(password)`

bcrypt ne stocke jamais le mot de passe. Il le transforme en une chaîne comme :
`$2b$12$LQv3c1yqBWVH...` — impossible à lire, impossible à inverser.

```python
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt(rounds=12)  # génère un "sel" aléatoire
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")
```

**Pourquoi 12 rounds ?** Chaque round double le temps de calcul. À 12 rounds, bcrypt met environ 200ms pour hasher un mot de passe — imperceptible pour un humain, mais catastrophique pour un attaquant qui doit en essayer des millions.

**Pourquoi un "sel" (salt) ?** Sans sel, deux utilisateurs avec le même mot de passe auraient le même hash — un attaquant pourrait créer un dictionnaire. Avec le sel aléatoire, même "123456" donne un hash différent à chaque fois.

---

### ✅ `verify_password(password, password_hash)`

```python
def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
```

bcrypt peut vérifier si un mot de passe correspond à son hash **sans jamais déchiffrer le hash**. C'est la magie de l'algorithme.

---

### 🎲 `generate_token()`

```python
def generate_token() -> str:
    return secrets.token_hex(32)  # 32 octets = 64 caractères hexadécimaux
```

`secrets` (module Python) génère des nombres vraiment aléatoires (pas prévisibles comme `random`). 32 octets = 256 bits = virtuellement impossible à deviner.

---

### 🔒 `hash_token(token)`

```python
def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
```

Le token de session n'est jamais stocké en clair dans la base. Si quelqu'un vole la base de données, il ne peut pas utiliser les tokens. Dans la base, on stocke `SHA-256(token)`, et pour vérifier, on recalcule `SHA-256` du token reçu et on compare.

---

### ⏰ `generate_session_expiry()`

```python
def generate_session_expiry() -> datetime:
    return datetime.now(timezone.utc) + timedelta(hours=config.SESSION_DURATION_HOURS)
# SESSION_DURATION_HOURS = 8 dans config.py
```

Une session expire 8h après sa création. Configurable dans `config.py`.

---

### 💪 `validate_password_strength(password)`

Vérifie 5 règles :
1. Au moins 8 caractères (`PASSWORD_MIN_LENGTH = 8`)
2. Au moins une majuscule : `re.search(r"[A-Z]", password)`
3. Au moins une minuscule : `re.search(r"[a-z]", password)`
4. Au moins un chiffre : `re.search(r"\d", password)`
5. Au moins un caractère spécial : `re.search(r"[!@#$%^&*(),.?\":{}|<>]", password)`

Retourne `(True, [])` si valide, `(False, ["liste des erreurs"])` sinon.

---

### 📧 `validate_email(email)`

```python
pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
return bool(re.match(pattern, email))
```

Regex qui vérifie qu'il y a : une partie locale, un `@`, un domaine, un `.`, une extension d'au moins 2 lettres.

---

### 🏢 `validate_siret(siret)`

Le SIRET est un identifiant d'établissement français à 14 chiffres. Sa validité se vérifie avec l'**algorithme de Luhn** :

1. Pour chaque chiffre en position paire (0, 2, 4...) → multiplier par 2, si > 9 → soustraire 9
2. Additionner tous les chiffres
3. Si le total est divisible par 10 → SIRET valide

```python
total = 0
for i, digit in enumerate(siret):
    d = int(digit)
    if i % 2 == 0:
        d *= 2
        if d > 9:
            d -= 9
    total += d
return total % 10 == 0
```

---

### 🧹 `sanitize_input(text)`

```python
def sanitize_input(text: str | None) -> str | None:
    if text is None:
        return None
    text = text.strip()  # supprime espaces en début/fin
    text = "".join(char for char in text if char >= " " or char in "\n\t")  # supprime caractères de contrôle
    return text if text else None
```

Supprime les caractères de contrôle (`\x00`, `\x01`...) qui pourraient causer des problèmes ou être utilisés dans des attaques.

---

## 7. Les Contrôleurs (`src/controllers/`)

### 7.1 Rôle des contrôleurs

Le contrôleur est le "cerveau" de l'application. Il :
1. Reçoit une demande de la vue ("créer cet utilisateur")
2. Valide les données
3. Vérifie les permissions
4. Interagit avec la base via les modèles
5. Écrit un log d'audit
6. Retourne un résultat à la vue

Les contrôleurs ne savent pas comment s'affiche l'interface. Les vues ne savent pas comment la base fonctionne. C'est l'isolation MVC.

---

### 7.2 `auth_controller.py` en détail

**Fichier :** `src/controllers/auth_controller.py`

#### La méthode `login(email, password)`

Voici les étapes dans l'ordre :

```
1. Vérifier que email et password ne sont pas vides
2. Vérifier si le compte est bloqué (rate limiting)
3. Chercher l'utilisateur par email dans la base
4. Si introuvable → enregistrer l'échec + retourner erreur générique
5. Vérifier si le compte est actif (is_active = True)
6. Vérifier le mot de passe avec bcrypt
7. Si mauvais mot de passe → enregistrer l'échec
8. Réinitialiser le compteur d'échecs
9. Générer un token de session (64 caractères hexadécimaux)
10. Hasher le token et le stocker en base (table sessions)
11. Mettre à jour last_login
12. Écrire un log d'audit (action="LOGIN")
13. Charger l'utilisateur avec son rôle (joinedload)
14. Stocker en mémoire (self._current_user, self._session_token)
15. Retourner (True, "Bienvenue, Ibrahim!")
```

#### Le rate limiting (anti brute force)

```python
_MAX_ATTEMPTS = 5      # 5 tentatives maximum
_LOCKOUT_MINUTES = 15  # blocage 15 minutes

# Dans __init__ :
self._failed_attempts: dict = {}
# Format : {"email@test.com": {"count": 3, "since": datetime(...)}}
```

Quand un utilisateur échoue 5 fois, son email est bloqué 15 minutes. Si les 15 minutes passent, le compteur se remet à zéro automatiquement.

#### Le singleton `auth_controller`

À la fin du fichier :
```python
auth_controller = AuthController()  # instance unique créée une seule fois
```

Tous les modules importent **la même instance** :
```python
from src.controllers.auth_controller import auth_controller
```

Ainsi, quand Ibrahim se connecte, `auth_controller._current_user` est défini globalement dans toute l'application. N'importe quel contrôleur peut appeler `auth_controller.current_user` pour savoir qui est connecté.

#### `has_permission(permission)` / `is_admin()` / `is_super_admin()`

```python
def has_permission(self, permission: str) -> bool:
    if not self.is_authenticated:
        return False
    return self._current_user.has_permission(permission)  # délègue au modèle User → Role
```

---

### 7.3 `user_controller.py` — CRUD utilisateurs

**CRUD** = Create, Read, Update, Delete (les 4 opérations de base d'une base de données).

```python
# Guard de permission en tête de chaque méthode sensible
def create_user(self, ...) -> Tuple[bool, str, Optional[int]]:
    if not auth_controller.has_permission("manage_users"):
        return False, "Permission refusée", None
    # ... reste du code
```

La méthode `_format_user()` convertit un objet SQLAlchemy `User` en dictionnaire Python simple, ce qui est plus facile à manipuler dans les vues.

---

### 7.4 `company_controller.py` — CRUD entreprises

- `create_company()` : réservé au **super_admin** uniquement (guard `is_super_admin()`)
- `delete_company()` : réservé au super_admin ET vérifie qu'il n'y a plus d'utilisateurs actifs avant de désactiver
- `get_company_stats()` : retourne les compteurs (users, ressources, disponibles) pour les stats du dashboard
- La méthode `_format_siret()` formate le SIRET avec des espaces : `"732 829 320 00074"`

---

### 7.5 `resource_controller.py` — CRUD ressources

- `create_resource()` : appelle `sanitize_input()` sur le nom et le numéro de série
- `delete_resource()` : ne supprime pas physiquement — passe le statut à `retired` (soft delete)
- Vérifie qu'une ressource `assigned` ne peut pas être supprimée

---

### 7.6 Les guards de permission

Un "guard" est une vérification au début d'une méthode qui bloque l'exécution si l'utilisateur n'a pas les droits.

```python
# Exemple dans user_controller.py
def create_user(self, ...):
    if not auth_controller.has_permission("manage_users"):
        return False, "Permission refusée", None  # ← bloque ici
    # La suite ne s'exécute que si l'utilisateur a la permission
```

Permissions disponibles (définies dans `config.py`) :
- `super_admin` : `["all"]` — peut tout faire
- `admin` : `["view_resources", "manage_resources", "view_users", "manage_users", "view_logs", "generate_contracts", "view_assignments", "manage_assignments"]`
- `employee` : `["view_own_resources", "view_own_assignments", "sign_contracts", "view_own_history"]`

---

## 8. Les Vues PySide6 (`src/views/`)

### 8.1 PySide6 — Comment ça marche

**Widget :** Un élément d'interface (bouton, champ texte, tableau, fenêtre). Tout est un widget.

**Layout :** Un conteneur qui organise les widgets (horizontal `QHBoxLayout`, vertical `QVBoxLayout`, grille `QGridLayout`).

**Signal/Slot :** Le système de communication de Qt. Un widget émet un **signal** (événement) quand quelque chose se passe. Un autre widget ou une fonction écoute ce signal (c'est un **slot**).

```python
# Exemple concret dans login_view.py
self.login_button.clicked.connect(self._on_login_clicked)
# ↑ Quand le bouton est cliqué (signal), appelle _on_login_clicked (slot)

# Et dans main_window.py
self.login_view.login_successful.connect(self._on_login_successful)
# ↑ Quand le signal login_successful est émis, affiche le dashboard
```

---

### 8.2 `styles.py` — La palette de couleurs

**Fichier :** `src/views/styles.py`

La palette de couleurs principale est stockée dans le dictionnaire `COLORS` :

```python
COLORS = {
    "primary":      "#6366f1",   # Indigo — couleur principale
    "primary_hover":"#4f46e5",   # Indigo plus foncé au survol
    "success":      "#10b981",   # Vert — succès
    "warning":      "#f59e0b",   # Amber — avertissement
    "danger":       "#ef4444",   # Rouge — erreur/danger
    "sidebar_bg":   "#1e1b4b",   # Indigo très sombre — sidebar
    ...
}
```

`GLOBAL_STYLE` est une grande chaîne CSS appliquée à toute l'application via `app.setStyleSheet(GLOBAL_STYLE)`. Elle définit l'apparence par défaut de tous les widgets Qt.

Les fonctions `primary_button_style()`, `secondary_button_style()`, etc. retournent des chaînes CSS pour des styles de boutons réutilisables.

---

### 8.3 `login_view.py` — L'écran de connexion

**Fichier :** `src/views/login_view.py`

#### Le fond dégradé

```python
class GradientBackground(QWidget):
    def paintEvent(self, event):
        painter = QPainter(self)
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0.0, QColor("#1e1b4b"))  # indigo sombre
        gradient.setColorAt(0.5, QColor("#312e81"))  # indigo moyen
        gradient.setColorAt(1.0, QColor("#4c1d95"))  # violet foncé
        painter.fillRect(self.rect(), QBrush(gradient))
```

`paintEvent` est une méthode spéciale appelée par Qt chaque fois que le widget doit être redessiné. En la surchargeant, on peut dessiner ce qu'on veut avec `QPainter`.

#### Le signal `login_successful`

```python
class LoginView(QWidget):
    login_successful = Signal()  # déclare un signal sans argument
    
    def _on_login_clicked(self):
        success, message = auth_controller.login(email, password)
        if success:
            self.login_successful.emit()  # émet le signal → main_window affiche le dashboard
```

---

### 8.4 `main_window.py` — La fenêtre principale

**Fichier :** `src/views/main_window.py`

#### QStackedWidget — La navigation

```python
self.stack = QStackedWidget()
self.stack.addWidget(self.login_view)    # index 0
self.stack.addWidget(self.dashboard_view) # index 1
self.stack.setCurrentWidget(self.login_view)  # affiche login au départ
```

`QStackedWidget` est comme un paquet de cartes : une seule carte est visible à la fois. Pour passer du login au dashboard, on appelle `setCurrentWidget(self.dashboard_view)`.

#### Création du premier super admin

Au démarrage, `_check_initial_setup()` vérifie si un super admin existe. Si non, des boîtes de dialogue demandent email et mot de passe pour en créer un.

---

### 8.5 `dashboard_view.py` — Le tableau de bord

**Fichier :** `src/views/dashboard_view.py`

#### StatCard — Cartes avec dégradé

```python
class StatCard(QFrame):
    def paintEvent(self, event):  # redessiné à chaque fois que le widget est affiché
        painter = QPainter(self)
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0.0, QColor(self._grad_start))  # ex: #6366f1
        gradient.setColorAt(1.0, QColor(self._grad_end))    # ex: #8b5cf6
        path = QPainterPath()
        path.addRoundedRect(...)  # coins arrondis
        painter.fillPath(path, QBrush(gradient))
```

4 cartes sont affichées : Utilisateurs actifs (indigo), Ressources (cyan), Affectations (vert), Entreprises (amber).

#### La sidebar

La sidebar est un `QFrame` de largeur fixe 260px avec :
- Logo avec dégradé
- Boutons de navigation avec emoji (🏠 👥 🏢 🖥️ 📋 📄 📊)
- En bas : avatar de l'utilisateur connecté + bouton de déconnexion

#### Navigation par QStackedWidget

```python
self.content_stack = QStackedWidget()
# Chaque clic sur un bouton de menu affiche la page correspondante
self.btn_resources.clicked.connect(lambda: self._navigate("resources"))
```

---

### 8.6 `data_table.py` — Le composant tableau réutilisable

**Fichier :** `src/views/widgets/data_table.py`

C'est le composant le plus réutilisé du projet. Il crée automatiquement un tableau avec recherche, filtres, pagination et boutons d'action.

#### Utilisation type
```python
# Dans users_view.py
columns = [
    {"key": "full_name", "label": "Nom complet"},
    {"key": "email",     "label": "Email"},
    {"key": "status",    "label": "Statut"},
]
self.table = DataTable(columns, title="👥 Utilisateurs", page_size=15)
self.table.set_actions([
    {"name": "edit",   "icon": "✏️", "label": "Modifier",    "color": "#6366f1"},
    {"name": "delete", "icon": "🗑️", "label": "Supprimer",   "color": "#ef4444"},
])
self.table.add_clicked.connect(self._on_add)
self.table.action_triggered.connect(self._on_action)
```

#### La recherche en temps réel

```python
def _on_search(self, text: str):
    if not text:
        self._filtered_data = self._data.copy()
    else:
        text_lower = text.lower()
        self._filtered_data = [
            row for row in self._data
            if any(text_lower in str(row.get(col["key"], "")).lower() for col in self._columns)
        ]
    self._refresh_table()
```

Filtre les données à chaque frappe, en cherchant le texte dans toutes les colonnes.

#### Les filtres (`add_filter_bar` / `add_filter`)

```python
# Exemple dans users_view.py
self.table.add_filter_bar()
self.table.add_filter("Rôle", [
    ("Tous les rôles", None),
    ("Super Admin",    "super_admin"),
    ("Administrateur", "admin"),
    ("Employé",        "employee"),
], key="role_name")
```

Les filtres et la recherche textuelle se combinent : un utilisateur doit correspondre à TOUS les filtres actifs et au texte de recherche.

#### Les badges de statut

```python
# Rend un badge coloré "pill" dans une cellule
self.table.set_status_badge(
    row_idx=2,
    col_idx=4,
    text="Actif",
    text_color="#059669",   # vert foncé
    bg_color="#d1fae5"      # vert clair
)
```

#### La pagination

```python
# Affiche 15 lignes par page
self._page_size = 15
# Navigation avec boutons "← Précédent" et "Suivant →"
# Affichage : "Page 2 / 5" et "75 élément(s)"
```

---

### 8.7 Les vues métier — Filtres par section

**`users_view.py`** — 3 filtres :
- Entreprise (recharge les données depuis la base)
- Rôle (filtre client-side)
- Statut : Actif / Inactif (filtre sur `is_active`)

**`resources_view.py`** — 4 mini-cartes de comptage + 2 filtres :
- Mini-cartes : Disponibles (vert), Affectées (bleu), Maintenance (orange), Retirées (gris)
- Filtre Entreprise + Filtre Statut

**`companies_view.py`** — 1 filtre :
- Statut : Actives uniquement / Toutes (inclus inactives)

**`assignments_view.py`** — 1 filtre :
- Statut : Toutes / Active / Retournée / Annulée

**`logs_view.py`** — 1 filtre + bouton Export :
- Type d'action : Toutes / LOGIN / LOGOUT / LOGIN_FAILED / CREATE / UPDATE / DELETE / PASSWORD_CHANGE
- Bouton "📥 Exporter CSV" pour télécharger les logs

---

## 9. Les utilitaires (`src/utils/`)

### 9.1 `backup.py` — La sauvegarde automatique

**Fichier :** `src/utils/backup.py`

```python
def create_backup() -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = backup_dir / f"gestres_pro_{timestamp}.sql"
    
    env = os.environ.copy()
    env["PGPASSWORD"] = config.DB_PASSWORD  # mot de passe via variable d'env
    
    result = subprocess.run([
        "pg_dump",
        "-h", config.DB_HOST, "-p", config.DB_PORT,
        "-U", config.DB_USER, "-d", config.DB_NAME,
        "-f", str(dest), "--format=plain",
    ], env=env, ...)
    
    # Garder uniquement les 10 dernières sauvegardes
    backups = sorted(backup_dir.glob("gestres_pro_*.sql"))
    for old in backups[:-10]:
        old.unlink()
```

**`pg_dump`** est l'outil officiel PostgreSQL pour exporter une base de données en SQL. Le fichier `.sql` généré peut être réimporté sur n'importe quel serveur PostgreSQL.

**La rotation** : on garde les 10 dernières sauvegardes et on supprime les plus anciennes. Ça évite de remplir le disque.

**Pourquoi au démarrage ?** La sauvegarde est faite juste avant que l'utilisateur puisse faire quoi que ce soit. Si une opération se passe mal, on a toujours le backup d'avant.

---

### 9.2 `maintenance.py` — La purge automatique

**Fichier :** `src/utils/maintenance.py`

```python
def purge_expired_sessions():
    now = datetime.now(timezone.utc)
    with get_session() as session:
        deleted = session.query(Session).filter(Session.expires_at < now).delete()
        session.commit()
    return deleted

def purge_expired_logs():
    cutoff = datetime.now(timezone.utc) - timedelta(days=config.AUDIT_LOG_RETENTION_DAYS)
    with get_session() as session:
        deleted = session.query(AuditLog).filter(AuditLog.created_at < cutoff).delete()
        session.commit()
    return deleted
```

- Les sessions sont purgées quand elles ont dépassé leur date d'expiration (8h après connexion)
- Les logs d'audit sont purgés au bout de `AUDIT_LOG_RETENTION_DAYS = 365 * 5` = 5 ans (obligation RGPD)

---

### 9.3 `validators.py` — Les validateurs réutilisables

**Fichier :** `src/utils/validators.py`

```python
# Utilisation de la classe Validator
validator = Validator()
validator.validate_required(name, "name")
validator.validate_length(name, "name", min_length=2, max_length=100)
validator.validate_email(email, "email")

if not validator.is_valid():
    errors = validator.get_errors()
    # errors = {"name": ["Ce champ est obligatoire"], "email": ["Format invalide"]}
```

**`ValidationError`** : exception personnalisée avec deux attributs : `field` (le champ concerné) et `message` (l'erreur).

---

## 10. Les Tests (`tests/`)

### 10.1 Pourquoi les tests sont importants

Les tests automatisés vérifient que le code fait bien ce qu'on attend. Sans tests, chaque modification peut casser quelque chose sans qu'on s'en rende compte. Avec 155 tests, on peut modifier le code et lancer `pytest` pour vérifier immédiatement que rien n'est cassé.

C'est aussi un argument fort pour l'oral E6 : **montrer 155 tests qui passent en live**.

---

### 10.2 pytest — Comment ça fonctionne

```bash
# Lancer tous les tests
python -m pytest tests/ -v

# Lancer un fichier spécifique
python -m pytest tests/test_security.py -v

# Résultat attendu
155 passed in 14.53s ✅
```

pytest cherche tous les fichiers `test_*.py`, toutes les classes `TestXxx` et toutes les fonctions `test_xxx`. Il les exécute et indique lesquels passent (✅) ou échouent (❌).

---

### 10.3 `conftest.py` — La base en mémoire pour les tests

**Fichier :** `tests/conftest.py`

```python
@pytest.fixture(autouse=True, scope="function")
def use_in_memory_db():
    test_engine = create_engine("sqlite:///:memory:", ...)
    Base.metadata.create_all(bind=test_engine)  # crée les tables en mémoire
    
    # Remplace temporairement le moteur PostgreSQL par SQLite en mémoire
    base_module.engine = test_engine
    base_module.SessionLocal = sessionmaker(bind=test_engine, ...)
    
    yield test_engine  # les tests s'exécutent ici
    
    # Après le test → remet PostgreSQL, supprime toutes les tables du test
    base_module.engine = original_engine
    Base.metadata.drop_all(bind=test_engine)
```

**Pourquoi SQLite en mémoire et pas PostgreSQL ?**
- Plus rapide : SQLite en mémoire est instantané, PostgreSQL nécessite une connexion réseau
- Isolation : chaque test repart de zéro, sans laisser de données dans la vraie base
- Pas de dépendance : les tests fonctionnent même sans PostgreSQL installé

⚠️ **Limite :** SQLite ne vérifie pas les contraintes CHECK ni les triggers PostgreSQL. Les tests vérifient la logique Python, pas la logique PostgreSQL.

---

### 10.4 Les 3 fichiers de tests

#### `test_security.py` — 40 tests

Teste `src/utils/security.py` :
- **TestPasswordHashing** (8 tests) : hash différent du clair, préfixe `$2b$`, vérification correcte/incorrecte, sel aléatoire, unicode, mot de passe long
- **TestTokenGeneration** (7 tests) : longueur 64, unicité sur 100 tokens, hexadécimal, SHA-256 déterministe, expiration future
- **TestPasswordStrength** (9 tests) : valide, trop court, pas de majuscule/minuscule/chiffre/spécial, plusieurs erreurs
- **TestEmailValidation** (3 tests) : emails valides/invalides, domaine en majuscules
- **TestSiretValidation** (7 tests) : SIRET valide, vide/null, trop court/long, lettres, espaces, Luhn invalide
- **TestSanitizeInput** (6 tests) : whitespace, tabs, None, vide, caractères de contrôle

#### `test_models.py` — 52 tests

Teste tous les modèles SQLAlchemy :
- Company, Role, User, ResourceType, Resource, Assignment, Contract, AuditLog, Session
- Vérifie : création, valeurs par défaut, propriétés calculées, soft delete, intégrité SHA-256

#### `test_controllers.py` — 63 tests

Teste les contrôleurs avec un super admin connecté via le fixture `logged_in_super_admin` :
- **TestAuthController** (26 tests) : login, logout, permissions, rate limiting, changement mdp
- **TestUserController** (18 tests) : CRUD, filtres, validation, guards de permission
- **TestCompanyController** (17 tests) : CRUD, validation SIRET, stats, guards de permission

**Total : 155 tests — 155 réussis — 0 échec** ✅

---

## 11. La configuration (`config.py` + `.env`)

### Pourquoi ne pas mettre les credentials dans le code

Si tu mets le mot de passe PostgreSQL directement dans `config.py` et que tu pousses sur GitHub, n'importe qui peut le lire. C'est une faille de sécurité classique.

**La solution :** Le fichier `.env` reste sur ta machine, jamais sur GitHub (grâce à `.gitignore`).

```bash
# .gitignore contient :
.env   # ← jamais commité
```

```bash
# .env (local, non commité)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=gestres_pro
DB_USER=gestres_user
DB_PASSWORD=GestRes2026!Secure
```

```bash
# .env.example (commité, sans le vrai mot de passe)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=gestres_pro
DB_USER=gestres_user
DB_PASSWORD=       # ← vide, à remplir par chaque développeur
```

### Les constantes de `config.py`

| Constante | Valeur | Rôle |
|-----------|--------|------|
| `DATABASE_URL` | `postgresql+psycopg2://...` | URL de connexion pour SQLAlchemy |
| `BCRYPT_ROUNDS` | `12` | Force du hachage bcrypt |
| `SESSION_DURATION_HOURS` | `8` | Durée d'une session (8 heures) |
| `PASSWORD_MIN_LENGTH` | `8` | Longueur minimale d'un mot de passe |
| `DEFAULT_RETENTION_DAYS` | `1095` (3 ans) | Durée de conservation des données |
| `AUDIT_LOG_RETENTION_DAYS` | `1825` (5 ans) | Durée de conservation des logs (RGPD) |
| `ROLES` | dict | Définition des 3 rôles et leurs permissions |
| `RESOURCE_STATUS` | dict | 4 statuts possibles pour une ressource |
| `ASSIGNMENT_STATUS` | dict | 3 statuts possibles pour une affectation |

---

## 12. Le démarrage de l'application (`main.py`)

**Fichier :** `main.py`

```python
def main():
    init_db()          # 1. Connexion BDD + création tables + rôles par défaut

    try:
        create_backup()     # 2. Sauvegarde pg_dump (si ça échoue → on continue)
    except Exception:
        pass

    try:
        run_maintenance()   # 3. Purge sessions/logs expirés (si ça échoue → on continue)
    except Exception:
        pass

    app = QApplication(sys.argv)  # 4. Démarre Qt

    app.setStyleSheet(GLOBAL_STYLE)  # 5. Applique le design global

    window = MainWindow()  # 6. Crée la fenêtre principale
    window.show()          # 7. Affiche la fenêtre

    sys.exit(app.exec())   # 8. Démarre la boucle d'événements Qt (attend les clics, etc.)
```

**Pourquoi cet ordre ?**
1. La base doit être prête avant tout
2. La sauvegarde doit se faire avant que l'utilisateur puisse modifier des données
3. La maintenance nettoie les vieilles données avant utilisation
4. L'interface s'affiche en dernier, quand tout est prêt

Les `try/except` autour de backup et maintenance évitent que l'app plante si le serveur PostgreSQL est temporairement inaccessible.

---

## 13. Conformité RGPD

Le RGPD (Règlement Général sur la Protection des Données) est une loi européenne qui impose des règles sur la collecte et le traitement des données personnelles.

### Données personnelles stockées

| Données | Justification |
|---------|---------------|
| Email | Nécessaire pour l'identification |
| Prénom, Nom | Nécessaire pour identifier qui a quelle ressource |
| Mot de passe (haché) | Nécessaire pour l'authentification |
| Date de dernière connexion | Traçabilité de sécurité |
| Adresse IP dans les logs | Sécurité, détection d'intrusion |

### Durées de rétention

- **Données utilisateurs** : 3 ans (`DEFAULT_RETENTION_DAYS = 365 * 3`)
- **Logs d'audit** : 5 ans (`AUDIT_LOG_RETENTION_DAYS = 365 * 5`) — obligation légale de traçabilité

### Droit à l'oubli (anonymisation)

La fonction PostgreSQL `fn_anonymize_user(user_id)` applique le "droit à l'oubli" :

```sql
UPDATE users SET
    email         = 'anonyme_42@supprime.local',
    first_name    = 'Anonyme',
    last_name     = 'Supprimé',
    password_hash = 'ANONYMIZED',
    is_active     = FALSE
WHERE id = 42;
DELETE FROM sessions WHERE user_id = 42;
```

L'enregistrement n'est pas supprimé (ça casserait les relations avec les affectations et contrats historiques). Les données personnelles sont remplacées par des valeurs neutres.

### Soft delete vs suppression physique

Partout dans le projet, les "suppressions" sont des **désactivations** (`is_active = FALSE`). On ne supprime jamais physiquement un utilisateur, une entreprise ou une ressource.

**Pourquoi ?** Pour conserver l'historique complet. Si un employé qui a eu un MacBook Pro quitte l'entreprise, on désactive son compte mais on garde la trace de l'affectation.

### Purge automatique

Au démarrage, `run_maintenance()` supprime :
- Les sessions expirées (plus de 8 heures)
- Les logs d'audit de plus de 5 ans

---

## 14. Glossaire

| Terme | Définition simple |
|-------|------------------|
| **ORM** | Object-Relational Mapper. Outil qui traduit du Python en SQL pour parler à la base de données sans écrire de SQL brut. |
| **MVC** | Modèle-Vue-Contrôleur. Architecture qui sépare les données (Modèle), l'affichage (Vue) et la logique (Contrôleur). |
| **bcrypt** | Algorithme de hachage de mots de passe. Volontairement lent pour empêcher les attaques par force brute. |
| **Hash** | Empreinte numérique d'une donnée. Irréversible : impossible de retrouver la donnée d'origine depuis le hash. |
| **Token** | Chaîne de caractères aléatoire servant d'identifiant de session. Comme un ticket de vestiaire. |
| **Session** | Période pendant laquelle un utilisateur est connecté. Expire après 8 heures. |
| **Trigger** | Code SQL qui s'exécute automatiquement quand quelque chose se passe dans la base (INSERT, UPDATE, DELETE). |
| **Vue SQL** | Requête SQL sauvegardée. On l'interroge comme une table mais elle combine plusieurs tables. |
| **Index** | Structure de données en base qui accélère les recherches. Comme l'index d'un livre. |
| **Clé étrangère** | Colonne qui fait référence à l'identifiant d'une autre table. Garantit l'intégrité des relations. |
| **RGPD** | Règlement Général sur la Protection des Données. Loi européenne sur la vie privée et les données personnelles. |
| **Soft delete** | "Suppression douce" : on ne supprime pas physiquement l'enregistrement, on met `is_active = FALSE`. |
| **Pool de connexions** | Ensemble de connexions à la base maintenues ouvertes en permanence pour éviter de les recréer à chaque requête. |
| **Rate limiting** | Limitation du nombre de tentatives. Ex: bloquer un compte 15 min après 5 tentatives de connexion échouées. |
| **SIRET** | Identifiant unique d'un établissement en France (14 chiffres). Validé avec l'algorithme de Luhn. |
| **Luhn** | Algorithme mathématique de validation de numéros (SIRET, cartes bancaires). Vérifie que le numéro n'a pas de faute de frappe. |
| **PL/pgSQL** | Langage de programmation intégré à PostgreSQL pour écrire des fonctions et triggers directement dans la base. |
| **pg_dump** | Outil officiel PostgreSQL pour exporter une base de données dans un fichier SQL. Utilisé pour les sauvegardes. |
| **Signal/Slot** | Mécanisme de communication de Qt. Un widget émet un signal (événement), un autre widget ou une fonction écoute et réagit (slot). |
| **CRUD** | Create, Read, Update, Delete — les 4 opérations de base sur une base de données. |

---

*Documentation générée le 2 juin 2026 — GestRes Pro v1.0 — CAMARA Ibrahim — BTS SIO SLAM 2026*
