import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).parent
load_dotenv(BASE_DIR / ".env")

# Connexion PostgreSQL externe
DB_HOST     = os.getenv("DB_HOST", "localhost")
DB_PORT     = os.getenv("DB_PORT", "5432")
DB_NAME     = os.getenv("DB_NAME", "gestres_pro")
DB_USER     = os.getenv("DB_USER", "gestres_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)


SESSION_DURATION_HOURS = 8
PASSWORD_MIN_LENGTH = 8

DEFAULT_RETENTION_DAYS   = 365 * 3
AUDIT_LOG_RETENTION_DAYS = 365 * 5

ROLES = {
    "super_admin": {
        "name": "Super Administrateur",
        "permissions": ["all"]
    },
    "admin": {
        "name": "Administrateur Entreprise",
        "permissions": [
            "view_resources", "manage_resources",
            "view_users", "manage_users",
            "view_logs", "generate_contracts",
            "view_assignments", "manage_assignments"
        ]
    },
    "employee": {
        "name": "Employé",
        "permissions": [
            "view_own_resources", "view_own_assignments",
            "sign_contracts", "view_own_history"
        ]
    }
}

RESOURCE_STATUS = {
    "available":   "Disponible",
    "assigned":    "Affectée",
    "maintenance": "En maintenance",
    "retired":     "Retirée"
}

CRITICITES = {
    "faible":   "Faible",
    "normal":   "Normal",
    "haute":    "Haute",
    "critique": "Critique"
}

ASSIGNMENT_STATUS = {
    "active":    "Active",
    "returned":  "Retournée",
    "cancelled": "Annulée"
}
