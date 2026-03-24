from typing import List, TYPE_CHECKING
import json

from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base

if TYPE_CHECKING:
    from src.models.company import Company
    from src.models.resource import Resource


class ResourceType(Base):
    __tablename__ = "resource_types"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    custom_fields: Mapped[str | None] = mapped_column(Text, nullable=True)

    company: Mapped["Company"] = relationship("Company", back_populates="resource_types")
    resources: Mapped[List["Resource"]] = relationship(
        "Resource", back_populates="resource_type", cascade="all, delete-orphan"
    )

    def get_custom_fields(self) -> list:
        if self.custom_fields:
            return json.loads(self.custom_fields)
        return []

    def set_custom_fields(self, fields: list):
        self.custom_fields = json.dumps(fields)

    def __repr__(self) -> str:
        return f"<ResourceType(id={self.id}, name='{self.name}')>"
