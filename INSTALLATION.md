# Guide d'Installation et Lancement

## GestRes Pro - Gestionnaire de Ressources d'Entreprise

---

## Prérequis

- **Python 3.10+** (testé avec Python 3.14)
- **pip** (gestionnaire de paquets Python)
- **macOS** (application desktop)

---

## Installation sur une nouvelle machine

### 1. Cloner ou copier le projet

```bash
# Si via Git
git clone <url-du-repo> GestRes-Pro
cd GestRes-Pro

# Ou copier le dossier manuellement
```

### 2. Créer un environnement virtuel

```bash
# Créer l'environnement virtuel
python3 -m venv .venv

# Activer l'environnement virtuel
source .venv/bin/activate
```

> **Note Windows:** Utiliser `.venv\Scripts\activate` au lieu de `source .venv/bin/activate`

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

Les dépendances installées :
- `PySide6` - Interface graphique Qt
- `SQLAlchemy` - ORM base de données
- `bcrypt` - Hashage des mots de passe
- `reportlab` - Génération de PDF
- `pytest` - Tests unitaires
- `python-dateutil` - Manipulation des dates

### 4. Lancer l'application

```bash
python3 main.py
```

---

## Premier lancement

Au premier lancement, l'application vous demandera de créer un **Super Administrateur** :

1. **Email** : Entrez une adresse email valide (ex: `admin@entreprise.com`)
2. **Mot de passe** : Minimum 8 caractères avec :
   - Au moins une majuscule
   - Au moins une minuscule
   - Au moins un chiffre
   - Au moins un caractère spécial (!@#$%^&*...)
   - Exemple : `Admin123!`
3. **Prénom** et **Nom** : Informations du compte

---

## Structure des fichiers

```
GestRes-Pro/
├── main.py                 # Point d'entrée
├── config.py               # Configuration
├── requirements.txt        # Dépendances
├── config.py               # URL de connexion PostgreSQL (postgresql+psycopg2://...)
├── src/
│   ├── models/             # Modèles de données
│   ├── views/              # Interfaces graphiques
│   ├── controllers/        # Logique métier
│   └── utils/              # Utilitaires
└── tests/                  # Tests unitaires
```

---

## Commandes utiles

### Lancer l'application
```bash
source .venv/bin/activate && python3 main.py
```

### Lancer les tests
```bash
source .venv/bin/activate && python3 -m pytest tests/ -v
```

### Réinitialiser la base de données
```bash
# Se connecter à PostgreSQL et supprimer/recréer la base
psql -U postgres -c "DROP DATABASE IF EXISTS gestres_db;"
psql -U postgres -c "CREATE DATABASE gestres_db OWNER gestres_user;"
python3 main.py  # Recrée le schéma via SQLAlchemy
```

---

## Dépannage

### Erreur "No module named 'PySide6'"
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### Erreur de base de données
```bash
# Vérifier que PostgreSQL tourne et que les variables dans config.py sont correctes
psql -U gestres_user -d gestres_db -c "\dt"
python3 main.py
```

### Mot de passe oublié
Connectez-vous à PostgreSQL et remettez à zéro le super administrateur via `seed_test_company.py`.

---

## Identifiants de test

Pour tester rapidement :
- **Email** : `admin@test.com`
- **Mot de passe** : `Admin123!`

---

## Support

Projet BTS SIO - Application de gestion des ressources d'entreprise.
