"""
Configuration globale des tests : base de données en mémoire isolée.

Chaque test utilise une base SQLite en mémoire propre.
Le vrai database.db n'est JAMAIS touché pendant les tests.
"""
import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
import src.models.base as base_module


def make_test_engine():
    test_engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False}
    )

    @event.listens_for(test_engine, "connect")
    def set_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    return test_engine


@pytest.fixture(autouse=True, scope="function")
def use_in_memory_db():
    """
    Remplace le moteur SQLite fichier par une base en mémoire pour chaque test.
    Patche AUSSI les références directes `engine` dans les modules de test
    pour que leurs `create_all` / `drop_all` ciblent la base en mémoire,
    et non le vrai database.db.
    """
    test_engine = make_test_engine()

    # Créer toutes les tables sur la base en mémoire
    base_module.Base.metadata.create_all(bind=test_engine)

    # Sauvegarder les références originales
    original_engine = base_module.engine
    original_session_local = base_module.SessionLocal

    # Patcher le module base
    base_module.engine = test_engine
    base_module.SessionLocal = sessionmaker(
        bind=test_engine, autoflush=False, autocommit=False
    )

    # Patcher les références directes dans les modules de test
    # (évite que leurs `drop_all(bind=engine)` touchent le vrai database.db)
    import tests.test_controllers as tc
    import tests.test_models as tm
    original_tc_engine = tc.engine
    original_tm_engine = tm.engine
    tc.engine = test_engine
    tm.engine = test_engine

    yield test_engine

    # Restaurer tout
    base_module.engine = original_engine
    base_module.SessionLocal = original_session_local
    tc.engine = original_tc_engine
    tm.engine = original_tm_engine

    base_module.Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()
