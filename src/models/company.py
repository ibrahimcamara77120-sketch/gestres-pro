from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import String, Boolean, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


def _utc_now():
    return datetime.now(timezone.utc)

if TYPE_CHECKING:
    from src.models.user import User
    from src.models.resource_type import ResourceType
    from src.models.resource import Resource


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    siret: Mapped[str | None] = mapped_column(String(14), unique=True, nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utc_now, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    users: Mapped[list["User"]] = relationship("User", back_populates="company", cascade="all, delete-orphan")
    resource_types: Mapped[list["ResourceType"]] = relationship("ResourceType", back_populates="company", cascade="all, delete-orphan")
    resources: Mapped[list["Resource"]] = relationship("Resource", back_populates="company", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Company(id={self.id}, name='{self.name}')>"
