from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple

from sqlalchemy.orm import joinedload

from src.models.base import get_session
from src.models.assignment import Assignment
from src.models.resource import Resource
from src.models.user import User
from src.models.audit_log import AuditLog
from src.controllers.auth_controller import auth_controller
import config


class AssignmentController:

    def get_all_assignments(self, company_id: Optional[int] = None,
                            status: Optional[str] = None,
                            user_id: Optional[int] = None) -> List[Dict[str, Any]]:
        with get_session() as session:
            query = session.query(Assignment).options(
                joinedload(Assignment.resource),
                joinedload(Assignment.user),
                joinedload(Assignment.assigner)
            )
            if status:
                query = query.filter_by(status=status)
            if user_id:
                query = query.filter_by(user_id=user_id)
            if company_id:
                query = query.join(Resource).filter(Resource.company_id == company_id)

            assignments = query.order_by(Assignment.start_date.desc()).all()
            return [self._format_assignment(a) for a in assignments]

    def get_assignment_by_id(self, assignment_id: int) -> Optional[Dict[str, Any]]:
        with get_session() as session:
            a = session.query(Assignment).options(
                joinedload(Assignment.resource),
                joinedload(Assignment.user),
                joinedload(Assignment.assigner)
            ).filter_by(id=assignment_id).first()
            if a:
                return self._format_assignment(a)
            return None

    def create_assignment(self, resource_id: int, user_id: int,
                          start_date: datetime,
                          notes: Optional[str] = None) -> Tuple[bool, str, Optional[int]]:
        with get_session() as session:
            resource = session.query(Resource).filter_by(id=resource_id).first()
            if not resource:
                return False, "Ressource introuvable", None

            if not resource.is_available:
                label = config.RESOURCE_STATUS.get(resource.status, resource.status)
                return False, f"Ressource non disponible (statut : {label})", None

            user = session.query(User).filter_by(id=user_id, is_active=True).first()
            if not user:
                return False, "Utilisateur introuvable ou inactif", None

            assigned_by = auth_controller.current_user.id if auth_controller.current_user else user_id

            assignment = Assignment(
                resource_id=resource_id,
                user_id=user_id,
                assigned_by=assigned_by,
                start_date=start_date,
                status="active",
                notes=notes
            )
            session.add(assignment)

            resource.status = "assigned"

            log = AuditLog.log(
                action="CREATE",
                user_id=assigned_by,
                table_name="assignments",
                new_values={
                    "resource_id": resource_id,
                    "user_id": user_id,
                    "start_date": start_date.isoformat()
                }
            )
            session.add(log)
            session.commit()
            return True, "Affectation créée avec succès", assignment.id

    def close_assignment(self, assignment_id: int,
                         end_date: Optional[datetime] = None) -> Tuple[bool, str]:
        with get_session() as session:
            a = session.query(Assignment).filter_by(id=assignment_id).first()
            if not a:
                return False, "Affectation introuvable"
            if a.status != "active":
                return False, "Affectation déjà clôturée"

            a.status = "returned"
            a.end_date = end_date or datetime.now(timezone.utc).replace(tzinfo=None)

            resource = session.query(Resource).filter_by(id=a.resource_id).first()
            if resource:
                resource.status = "available"

            log = AuditLog.log(
                action="UPDATE",
                user_id=auth_controller.current_user.id if auth_controller.current_user else None,
                table_name="assignments", record_id=assignment_id,
                old_values={"status": "active"}, new_values={"status": "returned"}
            )
            session.add(log)
            session.commit()
            return True, "Ressource retournée avec succès"

    def cancel_assignment(self, assignment_id: int) -> Tuple[bool, str]:
        with get_session() as session:
            a = session.query(Assignment).filter_by(id=assignment_id).first()
            if not a:
                return False, "Affectation introuvable"
            if a.status != "active":
                return False, "Affectation déjà clôturée"

            a.status = "cancelled"
            a.end_date = datetime.now(timezone.utc).replace(tzinfo=None)

            resource = session.query(Resource).filter_by(id=a.resource_id).first()
            if resource:
                resource.status = "available"

            log = AuditLog.log(
                action="UPDATE",
                user_id=auth_controller.current_user.id if auth_controller.current_user else None,
                table_name="assignments", record_id=assignment_id,
                old_values={"status": "active"}, new_values={"status": "cancelled"}
            )
            session.add(log)
            session.commit()
            return True, "Affectation annulée"

    def _format_assignment(self, a: Assignment) -> Dict[str, Any]:
        status_labels = config.ASSIGNMENT_STATUS
        status_colors = {
            "active": "#2563eb",
            "returned": "#10b981",
            "cancelled": "#ef4444"
        }
        start = a.start_date.strftime("%d/%m/%Y") if a.start_date else ""
        end = a.end_date.strftime("%d/%m/%Y") if a.end_date else "En cours"
        return {
            "id": a.id,
            "resource_id": a.resource_id,
            "resource_name": a.resource.name if a.resource else "",
            "user_id": a.user_id,
            "user_name": a.user.full_name if a.user else "",
            "user_email": a.user.email if a.user else "",
            "assigned_by": a.assigned_by,
            "assigner_name": a.assigner.full_name if a.assigner else "",
            "start_date": start,
            "end_date": end,
            "status": a.status,
            "status_label": status_labels.get(a.status, a.status),
            "status_color": status_colors.get(a.status, "#64748b"),
            "notes": a.notes or "",
            "is_active": a.is_active
        }


assignment_controller = AssignmentController()
