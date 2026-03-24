from datetime import datetime, timezone
from typing import TYPE_CHECKING
import hashlib

from sqlalchemy import String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


def _utc_now():
    return datetime.now(timezone.utc)

if TYPE_CHECKING:
    from src.models.assignment import Assignment


class Contract(Base):
    __tablename__ = "contracts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    assignment_id: Mapped[int] = mapped_column(ForeignKey("assignments.id"), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)  # SHA-256
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utc_now, nullable=False)
    signed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    signature_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    pdf_path: Mapped[str | None] = mapped_column(String(255), nullable=True)

    assignment: Mapped["Assignment"] = relationship("Assignment", back_populates="contracts")

    @staticmethod
    def compute_hash(content: str) -> str:
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def verify_integrity(self) -> bool:
        return self.content_hash == self.compute_hash(self.content)

    @property
    def is_signed(self) -> bool:
        return self.signed_at is not None and self.signature_hash is not None

    def sign(self, signer_data: str):
        self.signed_at = datetime.now(timezone.utc)
        signature_content = f"{self.content_hash}:{signer_data}:{self.signed_at.isoformat()}"
        self.signature_hash = self.compute_hash(signature_content)

    def __repr__(self) -> str:
        return f"<Contract(id={self.id}, assignment_id={self.assignment_id}, signed={self.is_signed})>"
