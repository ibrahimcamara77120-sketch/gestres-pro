from datetime import datetime, timezone
from typing import List, TYPE_CHECKING
import json

from sqlalchemy import String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


def _utc_now():
    return datetime.now(timezone.utc)

if TYPE_CHECKING:
    from src.models.company import Company
    from src.models.assignment import Assignment
    from src.models.audit_log import AuditLog, Session


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    permissions: Mapped[str | None] = mapped_column(Text, nullable=True)

    users: Mapped[List["User"]] = relationship("User", back_populates="role")

    def get_permissions(self) -> list:
        if self.permissions:
            return json.loads(self.permissions)
        return []

    def has_permission(self, permission: str) -> bool:
        perms = self.get_permissions()
        return "all" in perms or permission in perms

    def __repr__(self) -> str:
        return f"<Role(id={self.id}, name='{self.name}')>"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str | None] = mapped_column(String(50), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(50), nullable=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), nullable=False)
    company_id: Mapped[int | None] = mapped_column(ForeignKey("companies.id"), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utc_now, nullable=False)
    last_login: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    role: Mapped["Role"] = relationship("Role", back_populates="users")
    company: Mapped["Company | None"] = relationship("Company", back_populates="users")
    assignments: Mapped[List["Assignment"]] = relationship(
        "Assignment", foreign_keys="Assignment.user_id", back_populates="user"
    )
    assigned_by_me: Mapped[List["Assignment"]] = relationship(
        "Assignment", foreign_keys="Assignment.assigned_by", back_populates="assigner"
    )
    audit_logs: Mapped[List["AuditLog"]] = relationship("AuditLog", back_populates="user")
    sessions: Mapped[List["Session"]] = relationship(
        "Session", back_populates="user", cascade="all, delete-orphan"
    )

    @property
    def full_name(self) -> str:
        parts = [self.first_name, self.last_name]
        return " ".join(p for p in parts if p) or self.email

    def has_permission(self, permission: str) -> bool:
        return self.role.has_permission(permission)

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}')>"
