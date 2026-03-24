from datetime import datetime, timezone
from typing import TYPE_CHECKING
import json

from sqlalchemy import String, Text, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


def _utc_now():
    return datetime.now(timezone.utc)

if TYPE_CHECKING:
    from src.models.user import User


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    table_name: Mapped[str | None] = mapped_column(String(50), nullable=True)
    record_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    old_values: Mapped[str | None] = mapped_column(Text, nullable=True)
    new_values: Mapped[str | None] = mapped_column(Text, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utc_now, nullable=False)

    user: Mapped["User | None"] = relationship("User", back_populates="audit_logs")

    def get_old_values(self) -> dict:
        if self.old_values:
            return json.loads(self.old_values)
        return {}

    def get_new_values(self) -> dict:
        if self.new_values:
            return json.loads(self.new_values)
        return {}

    @classmethod
    def log(cls, action: str, user_id: int | None = None, table_name: str | None = None,
            record_id: int | None = None, old_values: dict | None = None,
            new_values: dict | None = None, ip_address: str | None = None) -> "AuditLog":
        return cls(
            user_id=user_id,
            action=action,
            table_name=table_name,
            record_id=record_id,
            old_values=json.dumps(old_values) if old_values else None,
            new_values=json.dumps(new_values) if new_values else None,
            ip_address=ip_address
        )

    def __repr__(self) -> str:
        return f"<AuditLog(id={self.id}, action='{self.action}', user_id={self.user_id})>"


class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    token_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utc_now, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="sessions")

    @property
    def is_expired(self) -> bool:
        now = datetime.now(timezone.utc)
        expires = self.expires_at
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        return now > expires

    @property
    def is_valid(self) -> bool:
        return not self.is_expired

    def __repr__(self) -> str:
        return f"<Session(id={self.id}, user_id={self.user_id})>"
