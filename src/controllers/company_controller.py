from sqlalchemy import func

from src.models.base import get_session
from src.models.company import Company
from src.models.user import User
from src.models.resource import Resource
from src.models.audit_log import AuditLog
from src.utils.security import validate_siret, sanitize_input
from src.controllers.auth_controller import auth_controller


class CompanyController:

    def get_all_companies(self, include_inactive=False):
        with get_session() as session:
            query = session.query(Company)

            if not include_inactive:
                query = query.filter_by(is_active=True)

            companies = query.order_by(Company.created_at.desc()).all()

            result = []
            for company in companies:
                nb_users = session.query(func.count(User.id)).filter(
                    User.company_id == company.id, User.is_active == True
                ).scalar()
                nb_ressources = session.query(func.count(Resource.id)).filter(
                    Resource.company_id == company.id
                ).scalar()
                result.append(self._format_company(company, nb_users, nb_ressources))

            return result

    def get_company_by_id(self, company_id):
        with get_session() as session:
            company = session.query(Company).filter_by(id=company_id).first()

            if company:
                nb_users = session.query(func.count(User.id)).filter(
                    User.company_id == company.id, User.is_active == True
                ).scalar()
                nb_ressources = session.query(func.count(Resource.id)).filter(
                    Resource.company_id == company.id
                ).scalar()
                return self._format_company(company, nb_users, nb_ressources)
            return None

    def create_company(self, name, siret=None, address=None):
        if not auth_controller.is_super_admin():
            return False, "Permission refusée : réservé au Super Administrateur", None

        name = sanitize_input(name)
        if not name or len(name) < 2:
            return False, "Nom requis (min 2 caractères)", None

        if siret:
            siret = siret.replace(" ", "")
            if not validate_siret(siret):
                return False, "Numéro SIRET invalide", None

        with get_session() as session:
            if siret:
                existing = session.query(Company).filter_by(siret=siret).first()
                if existing:
                    return False, "Ce numéro SIRET est déjà enregistré", None

            company = Company(
                name=name,
                siret=siret if siret else None,
                address=sanitize_input(address),
                is_active=True
            )
            session.add(company)

            log = AuditLog.log(
                action="CREATE",
                user_id=auth_controller.current_user.id if auth_controller.current_user else None,
                table_name="companies",
                new_values={"name": name, "siret": siret, "address": address}
            )
            session.add(log)
            session.commit()

            return True, "Entreprise créée avec succès", company.id

    def update_company(self, company_id, name=None, siret=None, address=None, is_active=None):
        if not auth_controller.has_permission("manage_resources"):
            return False, "Permission refusée"

        with get_session() as session:
            company = session.query(Company).filter_by(id=company_id).first()
            if not company:
                return False, "Entreprise non trouvée"

            old_values = {"name": company.name, "siret": company.siret,
                          "address": company.address, "is_active": company.is_active}

            if name is not None:
                name = sanitize_input(name)
                if not name or len(name) < 2:
                    return False, "Nom requis (min 2 caractères)"
                company.name = name

            if siret is not None:
                if siret:
                    siret = siret.replace(" ", "")
                    if not validate_siret(siret):
                        return False, "Numéro SIRET invalide"
                    existing = session.query(Company).filter(
                        Company.siret == siret, Company.id != company_id
                    ).first()
                    if existing:
                        return False, "Ce numéro SIRET est déjà enregistré"
                    company.siret = siret
                else:
                    company.siret = None

            if address is not None:
                company.address = sanitize_input(address)

            if is_active is not None:
                company.is_active = is_active

            new_values = {"name": company.name, "siret": company.siret,
                          "address": company.address, "is_active": company.is_active}

            log = AuditLog.log(
                action="UPDATE",
                user_id=auth_controller.current_user.id if auth_controller.current_user else None,
                table_name="companies", record_id=company_id,
                old_values=old_values, new_values=new_values
            )
            session.add(log)
            session.commit()

            return True, "Entreprise mise à jour avec succès"

    def delete_company(self, company_id):
        if not auth_controller.is_super_admin():
            return False, "Permission refusée : réservé au Super Administrateur"

        with get_session() as session:
            company = session.query(Company).filter_by(id=company_id).first()
            if not company:
                return False, "Entreprise non trouvée"

            nb_actifs = session.query(func.count(User.id)).filter(
                User.company_id == company_id, User.is_active == True
            ).scalar()

            if nb_actifs > 0:
                return False, f"Impossible : {nb_actifs} utilisateur(s) actif(s)"

            company.is_active = False

            log = AuditLog.log(
                action="DELETE",
                user_id=auth_controller.current_user.id if auth_controller.current_user else None,
                table_name="companies", record_id=company_id,
                old_values={"is_active": True}, new_values={"is_active": False}
            )
            session.add(log)
            session.commit()

            return True, "Entreprise désactivée avec succès"

    def get_company_stats(self, company_id):
        with get_session() as session:
            nb_users = session.query(func.count(User.id)).filter(
                User.company_id == company_id, User.is_active == True
            ).scalar()
            nb_ressources = session.query(func.count(Resource.id)).filter(
                Resource.company_id == company_id
            ).scalar()
            nb_dispo = session.query(func.count(Resource.id)).filter(
                Resource.company_id == company_id, Resource.status == "available"
            ).scalar()

            return {
                "users_count": nb_users,
                "resources_count": nb_ressources,
                "available_resources": nb_dispo
            }

    def _format_company(self, company, users_count=0, resources_count=0):
        return {
            "id": company.id,
            "name": company.name,
            "siret": company.siret or "",
            "siret_formatted": self._format_siret(company.siret) if company.siret else "Non renseigné",
            "address": company.address or "",
            "is_active": company.is_active,
            "status": "Active" if company.is_active else "Inactive",
            "users_count": users_count,
            "resources_count": resources_count,
            "created_at": company.created_at.strftime("%d/%m/%Y") if company.created_at else ""
        }

    def _format_siret(self, siret):
        if not siret or len(siret) != 14:
            return siret or ""
        return f"{siret[:3]} {siret[3:6]} {siret[6:9]} {siret[9:]}"


company_controller = CompanyController()
