from datetime import datetime, timezone

from sqlalchemy.orm import joinedload

from src.models.base import get_session
from src.models.user import User, Role
from src.models.company import Company
from src.models.audit_log import AuditLog
from src.utils.security import hash_password, validate_password_strength, validate_email
from src.controllers.auth_controller import auth_controller


class UserController:

    def get_all_users(self, company_id=None):
        with get_session() as session:
            query = session.query(User).options(joinedload(User.role), joinedload(User.company))

            if company_id:
                query = query.filter_by(company_id=company_id)

            users = query.order_by(User.created_at.desc()).all()
            return [self._format_user(u) for u in users]

    def get_user_by_id(self, user_id):
        with get_session() as session:
            user = session.query(User).options(
                joinedload(User.role), joinedload(User.company)
            ).filter_by(id=user_id).first()

            if user:
                return self._format_user(user)
            return None

    def create_user(self, email, password, first_name, last_name, role_id, company_id=None):
        if not auth_controller.has_permission("manage_users"):
            return False, "Permission refusée", None

        if not validate_email(email):
            return False, "Format d'email invalide", None

        is_valid, errors = validate_password_strength(password)
        if not is_valid:
            return False, errors[0], None

        with get_session() as session:
            existing = session.query(User).filter_by(email=email.lower().strip()).first()
            if existing:
                return False, "Cet email est déjà utilisé", None

            role = session.query(Role).filter_by(id=role_id).first()
            if not role:
                return False, "Rôle invalide", None

            if company_id:
                company = session.query(Company).filter_by(id=company_id).first()
                if not company:
                    return False, "Entreprise invalide", None

            user = User(
                email=email.lower().strip(),
                password_hash=hash_password(password),
                first_name=first_name.strip() if first_name else None,
                last_name=last_name.strip() if last_name else None,
                role_id=role_id,
                company_id=company_id,
                is_active=True
            )
            session.add(user)

            log = AuditLog.log(
                action="CREATE",
                user_id=auth_controller.current_user.id if auth_controller.current_user else None,
                table_name="users",
                new_values={"email": user.email, "first_name": first_name,
                            "last_name": last_name, "role_id": role_id, "company_id": company_id}
            )
            session.add(log)
            session.commit()

            return True, "Utilisateur créé avec succès", user.id

    def update_user(self, user_id, email=None, first_name=None, last_name=None,
                    role_id=None, company_id=None, is_active=None):
        if not auth_controller.has_permission("manage_users"):
            return False, "Permission refusée"

        with get_session() as session:
            user = session.query(User).filter_by(id=user_id).first()
            if not user:
                return False, "Utilisateur non trouvé"

            old_values = {
                "email": user.email, "first_name": user.first_name,
                "last_name": user.last_name, "role_id": user.role_id,
                "company_id": user.company_id, "is_active": user.is_active
            }

            if email is not None:
                if not validate_email(email):
                    return False, "Format d'email invalide"
                existing = session.query(User).filter(
                    User.email == email.lower().strip(), User.id != user_id
                ).first()
                if existing:
                    return False, "Cet email est déjà utilisé"
                user.email = email.lower().strip()

            if first_name is not None:
                user.first_name = first_name.strip() if first_name else None
            if last_name is not None:
                user.last_name = last_name.strip() if last_name else None
            if role_id is not None:
                role = session.query(Role).filter_by(id=role_id).first()
                if not role:
                    return False, "Rôle invalide"
                user.role_id = role_id
            if company_id is not None:
                if company_id > 0:
                    company = session.query(Company).filter_by(id=company_id).first()
                    if not company:
                        return False, "Entreprise invalide"
                    user.company_id = company_id
                else:
                    user.company_id = None
            if is_active is not None:
                user.is_active = is_active

            new_values = {
                "email": user.email, "first_name": user.first_name,
                "last_name": user.last_name, "role_id": user.role_id,
                "company_id": user.company_id, "is_active": user.is_active
            }

            log = AuditLog.log(
                action="UPDATE",
                user_id=auth_controller.current_user.id if auth_controller.current_user else None,
                table_name="users", record_id=user_id,
                old_values=old_values, new_values=new_values
            )
            session.add(log)
            session.commit()

            return True, "Utilisateur mis à jour avec succès"

    def delete_user(self, user_id):
        if not auth_controller.has_permission("manage_users"):
            return False, "Permission refusée"

        if auth_controller.current_user and auth_controller.current_user.id == user_id:
            return False, "Vous ne pouvez pas vous supprimer vous-même"

        with get_session() as session:
            user = session.query(User).filter_by(id=user_id).first()
            if not user:
                return False, "Utilisateur non trouvé"

            user.is_active = False

            log = AuditLog.log(
                action="DELETE",
                user_id=auth_controller.current_user.id if auth_controller.current_user else None,
                table_name="users", record_id=user_id,
                old_values={"is_active": True}, new_values={"is_active": False}
            )
            session.add(log)
            session.commit()

            return True, "Utilisateur désactivé avec succès"

    def reset_password(self, user_id, new_password):
        if not auth_controller.has_permission("manage_users"):
            return False, "Permission refusée"

        is_valid, errors = validate_password_strength(new_password)
        if not is_valid:
            return False, errors[0]

        with get_session() as session:
            user = session.query(User).filter_by(id=user_id).first()
            if not user:
                return False, "Utilisateur non trouvé"

            user.password_hash = hash_password(new_password)

            log = AuditLog.log(
                action="PASSWORD_RESET",
                user_id=auth_controller.current_user.id if auth_controller.current_user else None,
                table_name="users", record_id=user_id
            )
            session.add(log)
            session.commit()

            return True, "Mot de passe réinitialisé avec succès"

    def get_all_roles(self):
        with get_session() as session:
            roles = session.query(Role).all()
            resultat = []
            for role in roles:
                resultat.append({
                    "id": role.id,
                    "name": role.name,
                    "display_name": self._get_role_display_name(role.name)
                })
            return resultat

    def _format_user(self, user):
        return {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name or "",
            "last_name": user.last_name or "",
            "full_name": user.full_name,
            "role_id": user.role_id,
            "role_name": user.role.name if user.role else "",
            "role_display": self._get_role_display_name(user.role.name) if user.role else "",
            "company_id": user.company_id,
            "company_name": user.company.name if user.company else "Aucune",
            "is_active": user.is_active,
            "status": "Actif" if user.is_active else "Inactif",
            "created_at": user.created_at.strftime("%d/%m/%Y %H:%M") if user.created_at else "",
            "last_login": user.last_login.strftime("%d/%m/%Y %H:%M") if user.last_login else "Jamais"
        }

    def _get_role_display_name(self, role_name):
        noms = {
            "super_admin": "Super Administrateur",
            "admin": "Administrateur",
            "employee": "Employé"
        }
        return noms.get(role_name, role_name)


user_controller = UserController()
