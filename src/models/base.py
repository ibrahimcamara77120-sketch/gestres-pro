from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session as SASession
from contextlib import contextmanager

import config

engine = create_engine(
    config.DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False}
)

# foreign keys SQLite
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def init_db():
    from src.models import (
        Company, User, Role, ResourceType, Resource,
        Assignment, Contract, AuditLog, Session
    )
    Base.metadata.create_all(bind=engine)
    _create_default_roles()


def _create_default_roles():
    import json
    from src.models.user import Role

    with get_session() as session:
        for role_key, role_data in config.ROLES.items():
            existing = session.query(Role).filter_by(name=role_key).first()
            if not existing:
                role = Role(
                    name=role_key,
                    permissions=json.dumps(role_data["permissions"])
                )
                session.add(role)
        session.commit()


@contextmanager
def get_session() -> SASession:
    session = SessionLocal()
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
