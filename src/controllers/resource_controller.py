from typing import List, Dict, Any, Optional, Tuple
import json

from sqlalchemy.orm import joinedload

from src.models.base import get_session
from src.models.resource import Resource
from src.models.resource_type import ResourceType
from src.models.company import Company
from src.models.audit_log import AuditLog
from src.utils.security import sanitize_input
from src.controllers.auth_controller import auth_controller
import config


class ResourceController:

    def get_all_resources(self, company_id: Optional[int] = None,
                          status: Optional[str] = None,
                          resource_type_id: Optional[int] = None) -> List[Dict[str, Any]]:
        with get_session() as session:
            query = session.query(Resource).options(
                joinedload(Resource.resource_type),
                joinedload(Resource.company)
            )
            if company_id:
                query = query.filter_by(company_id=company_id)
            if status:
                query = query.filter_by(status=status)
            if resource_type_id:
                query = query.filter_by(resource_type_id=resource_type_id)

            resources = query.order_by(Resource.created_at.desc()).all()
            return [self._format_resource(r) for r in resources]

    def get_resource_by_id(self, resource_id: int) -> Optional[Dict[str, Any]]:
        with get_session() as session:
            resource = session.query(Resource).options(
                joinedload(Resource.resource_type),
                joinedload(Resource.company)
            ).filter_by(id=resource_id).first()
            if resource:
                return self._format_resource(resource)
            return None

    def create_resource(self, company_id: int, resource_type_id: int, name: str,
                        serial_number: Optional[str] = None,
                        custom_data: Optional[dict] = None) -> Tuple[bool, str, Optional[int]]:
        name = sanitize_input(name)
        if not name or len(name) < 2:
            return False, "Nom requis (min 2 caractères)", None

        with get_session() as session:
            company = session.query(Company).filter_by(id=company_id).first()
            if not company:
                return False, "Entreprise introuvable", None

            rt = session.query(ResourceType).filter_by(id=resource_type_id).first()
            if not rt:
                return False, "Type de ressource introuvable", None

            if serial_number:
                serial_number = sanitize_input(serial_number)
                existing = session.query(Resource).filter_by(serial_number=serial_number).first()
                if existing:
                    return False, "Ce numéro de série est déjà enregistré", None

            resource = Resource(
                company_id=company_id,
                resource_type_id=resource_type_id,
                name=name,
                serial_number=serial_number,
                status="available"
            )
            if custom_data:
                resource.set_custom_data(custom_data)

            session.add(resource)
            log = AuditLog.log(
                action="CREATE",
                user_id=auth_controller.current_user.id if auth_controller.current_user else None,
                table_name="resources",
                new_values={"name": name, "company_id": company_id, "resource_type_id": resource_type_id}
            )
            session.add(log)
            session.commit()
            return True, "Ressource créée avec succès", resource.id

    def update_resource(self, resource_id: int, name: Optional[str] = None,
                        status: Optional[str] = None,
                        serial_number: Optional[str] = None,
                        custom_data: Optional[dict] = None) -> Tuple[bool, str]:
        with get_session() as session:
            resource = session.query(Resource).filter_by(id=resource_id).first()
            if not resource:
                return False, "Ressource introuvable"

            old_values = {"name": resource.name, "status": resource.status, "serial_number": resource.serial_number}

            if name is not None:
                name = sanitize_input(name)
                if not name or len(name) < 2:
                    return False, "Nom requis (min 2 caractères)"
                resource.name = name

            if status is not None:
                if status not in config.RESOURCE_STATUS:
                    return False, f"Statut invalide : {status}"
                resource.status = status

            if serial_number is not None:
                sn = sanitize_input(serial_number)
                if sn:
                    existing = session.query(Resource).filter(
                        Resource.serial_number == sn, Resource.id != resource_id
                    ).first()
                    if existing:
                        return False, "Ce numéro de série est déjà utilisé"
                resource.serial_number = sn

            if custom_data is not None:
                resource.set_custom_data(custom_data)

            log = AuditLog.log(
                action="UPDATE",
                user_id=auth_controller.current_user.id if auth_controller.current_user else None,
                table_name="resources", record_id=resource_id,
                old_values=old_values,
                new_values={"name": resource.name, "status": resource.status}
            )
            session.add(log)
            session.commit()
            return True, "Ressource mise à jour avec succès"

    def delete_resource(self, resource_id: int) -> Tuple[bool, str]:
        with get_session() as session:
            resource = session.query(Resource).filter_by(id=resource_id).first()
            if not resource:
                return False, "Ressource introuvable"

            if resource.status == "assigned":
                return False, "Impossible : ressource actuellement affectée"

            resource.status = "retired"
            log = AuditLog.log(
                action="DELETE",
                user_id=auth_controller.current_user.id if auth_controller.current_user else None,
                table_name="resources", record_id=resource_id,
                old_values={"status": "available"}, new_values={"status": "retired"}
            )
            session.add(log)
            session.commit()
            return True, "Ressource retirée avec succès"

    def get_resources_by_user(self, user_id: int) -> List[Dict[str, Any]]:
        from src.models.assignment import Assignment
        with get_session() as session:
            subquery = (
                session.query(Assignment.resource_id)
                .filter_by(user_id=user_id, status="active")
                .subquery()
            )
            resources = session.query(Resource).options(
                joinedload(Resource.resource_type),
                joinedload(Resource.company)
            ).filter(Resource.id.in_(subquery)).all()
            return [self._format_resource(r) for r in resources]

    def get_all_resource_types(self, company_id: Optional[int] = None) -> List[Dict[str, Any]]:
        with get_session() as session:
            query = session.query(ResourceType)
            if company_id:
                query = query.filter_by(company_id=company_id)
            types = query.order_by(ResourceType.name).all()
            return [self._format_resource_type(rt) for rt in types]

    def create_resource_type(self, company_id: int, name: str,
                             description: Optional[str] = None,
                             custom_fields: Optional[list] = None) -> Tuple[bool, str, Optional[int]]:
        name = sanitize_input(name)
        if not name or len(name) < 2:
            return False, "Nom requis (min 2 caractères)", None

        with get_session() as session:
            rt = ResourceType(
                company_id=company_id,
                name=name,
                description=sanitize_input(description)
            )
            if custom_fields:
                rt.set_custom_fields(custom_fields)
            session.add(rt)
            session.commit()
            return True, "Type de ressource créé", rt.id

    def update_resource_type(self, rt_id: int, name: Optional[str] = None,
                             description: Optional[str] = None,
                             custom_fields: Optional[list] = None) -> Tuple[bool, str]:
        with get_session() as session:
            rt = session.query(ResourceType).filter_by(id=rt_id).first()
            if not rt:
                return False, "Type introuvable"
            if name is not None:
                rt.name = sanitize_input(name) or rt.name
            if description is not None:
                rt.description = sanitize_input(description)
            if custom_fields is not None:
                rt.set_custom_fields(custom_fields)
            session.commit()
            return True, "Type mis à jour"

    def _format_resource(self, resource: Resource) -> Dict[str, Any]:
        status_labels = config.RESOURCE_STATUS
        status_colors = {
            "available": "#10b981",
            "assigned": "#2563eb",
            "maintenance": "#f59e0b",
            "retired": "#94a3b8"
        }
        return {
            "id": resource.id,
            "name": resource.name,
            "serial_number": resource.serial_number or "",
            "status": resource.status,
            "status_label": status_labels.get(resource.status, resource.status),
            "status_color": status_colors.get(resource.status, "#64748b"),
            "resource_type_id": resource.resource_type_id,
            "resource_type_name": resource.resource_type.name if resource.resource_type else "",
            "company_id": resource.company_id,
            "company_name": resource.company.name if resource.company else "",
            "custom_data": resource.get_custom_data(),
            "is_available": resource.is_available,
            "created_at": resource.created_at.strftime("%d/%m/%Y") if resource.created_at else ""
        }

    def _format_resource_type(self, rt: ResourceType) -> Dict[str, Any]:
        return {
            "id": rt.id,
            "name": rt.name,
            "description": rt.description or "",
            "company_id": rt.company_id,
            "custom_fields": rt.get_custom_fields()
        }


resource_controller = ResourceController()
