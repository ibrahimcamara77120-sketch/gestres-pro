from datetime import datetime, timezone
from typing import List, TYPE_CHECKING

from sqlalchemy import String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base

if TYPE_CHECKING:
    from src.models.resource import Resource
    from src.models.user import User
    from src.models.contract import Contract


class Assignment(Base):
    __tablename__ = "assignments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    resource_id: Mapped[int] = mapped_column(ForeignKey("resources.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    assigned_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    start_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    resource: Mapped["Resource"] = relationship("Resource", back_populates="assignments")
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id], back_populates="assignments")
    assigner: Mapped["User"] = relationship("User", foreign_keys=[assigned_by], back_populates="assigned_by_me")
    contracts: Mapped[List["Contract"]] = relationship("Contract", back_populates="assignment", cascade="all, delete-orphan")

    @property
    def is_active(self) -> bool:
        return self.status == "active"

    @property
    def duration_days(self) -> int | None:
        end = self.end_date or datetime.now(timezone.utc).replace(tzinfo=None)
        return (end - self.start_date).days

    def __repr__(self) -> str:
        return f"<Assignment(id={self.id}, resource_id={self.resource_id}, user_id={self.user_id})>"
