from datetime import datetime, timedelta, timezone

from src.models.base import get_session
from src.models.audit_log import AuditLog, Session
import config


def purge_expired_logs():
    cutoff = datetime.now(timezone.utc) - timedelta(days=config.AUDIT_LOG_RETENTION_DAYS)
    with get_session() as session:
        deleted = session.query(AuditLog).filter(AuditLog.created_at < cutoff).delete()
        session.commit()
    return deleted


def purge_expired_sessions():
    now = datetime.now(timezone.utc)
    with get_session() as session:
        deleted = session.query(Session).filter(Session.expires_at < now).delete()
        session.commit()
    return deleted


def run_maintenance():
    logs_deleted = purge_expired_logs()
    sessions_deleted = purge_expired_sessions()
    return logs_deleted, sessions_deleted
