import os
from pathlib import Path

BASE_DIR = Path(__file__).parent
DATABASE_PATH = BASE_DIR / "database.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

BCRYPT_ROUNDS = 12
SESSION_DURATION_HOURS = 8
PASSWORD_MIN_LENGTH = 8

DEFAULT_RETENTION_DAYS = 365 * 3   # 3 ans
AUDIT_LOG_RETENTION_DAYS = 365 * 5  # 5 ans

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
    "available": "Disponible",
    "assigned": "Affectée",
    "maintenance": "En maintenance",
    "retired": "Retirée"
}

ASSIGNMENT_STATUS = {
    "active": "Active",
    "returned": "Retournée",
    "cancelled": "Annulée"
}
