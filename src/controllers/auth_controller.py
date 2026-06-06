from datetime import datetime, timezone, timedelta
import json

from sqlalchemy.orm import joinedload

from src.models.base import get_session
from src.models.user import User, Role
from src.models.audit_log import AuditLog, Session
from src.utils.security import (
    hash_password, verify_password, generate_token,
    hash_token, generate_session_expiry,
    validate_password_strength, validate_email
)

# Nombre max de tentatives avant blocage
MAX_TENTATIVES = 5
DUREE_BLOCAGE = 15  # en minutes


class AuthController:

    def __init__(self):
        self._current_user = None
        self._session_token = None
        self._failed_attempts = {}

    @property
    def current_user(self):
        return self._current_user

    @property
    def is_authenticated(self):
        return self._current_user is not None

    def _is_locked_out(self, email):
        key = email.lower().strip()
        info = self._failed_attempts.get(key)
        if not info:
            return False
        if info["count"] < MAX_TENTATIVES:
            return False
        elapsed = datetime.now(timezone.utc) - info["since"]
        if elapsed < timedelta(minutes=DUREE_BLOCAGE):
            return True
        del self._failed_attempts[key]
        return False

    def _record_failure(self, email):
        key = email.lower().strip()
        info = self._failed_attempts.get(key)
        if not info:
            self._failed_attempts[key] = {"count": 1, "since": datetime.now(timezone.utc)}
        else:
            elapsed = datetime.now(timezone.utc) - info["since"]
            if elapsed >= timedelta(minutes=DUREE_BLOCAGE):
                self._failed_attempts[key] = {"count": 1, "since": datetime.now(timezone.utc)}
            else:
                info["count"] += 1

    def _reset_attempts(self, email):
        self._failed_attempts.pop(email.lower().strip(), None)

    def login(self, email, password):
        if not email or not password:
            return False, "Email et mot de passe requis"

        if self._is_locked_out(email):
            self._log_failed_login(email)
            return False, (
                f"Compte temporairement bloqué après {MAX_TENTATIVES} tentatives échouées. "
                f"Réessayez dans {DUREE_BLOCAGE} minutes."
            )

        with get_session() as session:
            user = session.query(User).filter_by(email=email.lower().strip()).first()

            if not user:
                self._record_failure(email)
                self._log_failed_login(email)
                return False, "Email ou mot de passe incorrect"

            if not user.is_active:
                self._log_failed_login(email, user.id)
                return False, "Ce compte est désactivé"

            if not verify_password(password, user.password_hash):
                self._record_failure(email)
                self._log_failed_login(email, user.id)
                return False, "Email ou mot de passe incorrect"

            self._reset_attempts(email)

            token = generate_token()
            token_hash = hash_token(token)
            expires_at = generate_session_expiry()

            db_session = Session(user_id=user.id, token_hash=token_hash, expires_at=expires_at)
            session.add(db_session)

            user.last_login = datetime.now(timezone.utc)

            log = AuditLog.log(action="LOGIN", user_id=user.id, table_name="users", record_id=user.id)
            session.add(log)
            session.commit()

            from src.models.company import Company
            self._current_user = session.query(User).options(
                joinedload(User.role),
                joinedload(User.company)
            ).filter_by(id=user.id).first()
            self._session_token = token

            session.expunge(self._current_user)
            session.expunge(self._current_user.role)
            if self._current_user.company is not None:
                session.expunge(self._current_user.company)

            return True, f"Bienvenue, {self._current_user.full_name}!"

    def logout(self):
        if not self.is_authenticated:
            return False

        with get_session() as session:
            if self._session_token:
                token_hash = hash_token(self._session_token)
                db_session = session.query(Session).filter_by(token_hash=token_hash).first()
                if db_session:
                    session.delete(db_session)

            log = AuditLog.log(action="LOGOUT", user_id=self._current_user.id,
                               table_name="users", record_id=self._current_user.id)
            session.add(log)
            session.commit()

        self._current_user = None
        self._session_token = None
        return True

    def has_permission(self, permission):
        if not self.is_authenticated:
            return False
        return self._current_user.has_permission(permission)

    def is_super_admin(self):
        if not self.is_authenticated:
            return False
        return self._current_user.role.name == "super_admin"

    def is_admin(self):
        if not self.is_authenticated:
            return False
        return self._current_user.role.name in ("super_admin", "admin")

    def create_user(self, email, password, first_name=None, last_name=None,
                    role_name="employee", company_id=None):
        if not validate_email(email):
            return False, "Format d'email invalide", None

        is_valid, errors = validate_password_strength(password)
        if not is_valid:
            return False, errors[0], None

        with get_session() as session:
            existing = session.query(User).filter_by(email=email.lower().strip()).first()
            if existing:
                return False, "Cet email est déjà utilisé", None

            role = session.query(Role).filter_by(name=role_name).first()
            if not role:
                return False, f"Rôle '{role_name}' introuvable", None

            user = User(
                email=email.lower().strip(),
                password_hash=hash_password(password),
                first_name=first_name,
                last_name=last_name,
                role_id=role.id,
                company_id=company_id
            )
            session.add(user)

            log = AuditLog.log(
                action="CREATE",
                user_id=self._current_user.id if self._current_user else None,
                table_name="users",
                new_values={"email": user.email, "first_name": first_name,
                            "last_name": last_name, "role": role_name}
            )
            session.add(log)
            session.commit()

            session.expunge(user)
            return True, "Utilisateur créé avec succès", user

    def change_password(self, current_password, new_password):
        if not self.is_authenticated:
            return False, "Non connecté"

        with get_session() as session:
            user = session.get(User, self._current_user.id)

            if not verify_password(current_password, user.password_hash):
                return False, "Mot de passe actuel incorrect"

            is_valid, errors = validate_password_strength(new_password)
            if not is_valid:
                return False, errors[0]

            user.password_hash = hash_password(new_password)

            log = AuditLog.log(action="PASSWORD_CHANGE", user_id=user.id,
                               table_name="users", record_id=user.id)
            session.add(log)
            session.commit()

            return True, "Mot de passe modifié avec succès"

    def _log_failed_login(self, email, user_id=None):
        with get_session() as session:
            log = AuditLog.log(action="LOGIN_FAILED", user_id=user_id,
                               table_name="users", new_values={"attempted_email": email})
            session.add(log)
            session.commit()

    def create_initial_super_admin(self, email, password,
                                   first_name="Super", last_name="Admin"):
        with get_session() as session:
            super_admin_role = session.query(Role).filter_by(name="super_admin").first()
            if not super_admin_role:
                return False, "Rôle super_admin non trouvé"

            existing = session.query(User).filter_by(role_id=super_admin_role.id).first()
            if existing:
                return False, "Un super administrateur existe déjà"

        success, msg, user = self.create_user(
            email=email, password=password,
            first_name=first_name, last_name=last_name,
            role_name="super_admin"
        )
        return success, msg


auth_controller = AuthController()
