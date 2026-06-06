from datetime import datetime, date, timezone
from typing import List, TYPE_CHECKING
import json

from sqlalchemy import String, Text, Date, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


def _utc_now():
    return datetime.now(timezone.utc)

if TYPE_CHECKING:
    from src.models.company import Company
    from src.models.resource_type import ResourceType
    from src.models.assignment import Assignment


class Resource(Base):
    __tablename__ = "resources"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), nullable=False)
    resource_type_id: Mapped[int] = mapped_column(ForeignKey("resource_types.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    serial_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="available", nullable=False)
    criticite: Mapped[str] = mapped_column(String(10), default="normal", nullable=False)
    custom_data: Mapped[str | None] = mapped_column(Text, nullable=True)
    purchase_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_of_life_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utc_now, nullable=False)

    company: Mapped["Company"] = relationship("Company", back_populates="resources")
    resource_type: Mapped["ResourceType"] = relationship("ResourceType", back_populates="resources")
    assignments: Mapped[List["Assignment"]] = relationship(
        "Assignment", back_populates="resource", cascade="all, delete-orphan"
    )

    def get_custom_data(self) -> dict:
        if self.custom_data:
            return json.loads(self.custom_data)
        return {}

    def set_custom_data(self, data: dict):
        self.custom_data = json.dumps(data)

    @property
    def is_available(self) -> bool:
        return self.status == "available"

    @property
    def current_assignment(self) -> "Assignment | None":
        for assignment in self.assignments:
            if assignment.status == "active":
                return assignment
        return None

    def __repr__(self) -> str:
        return f"<Resource(id={self.id}, name='{self.name}', status='{self.status}')>"
