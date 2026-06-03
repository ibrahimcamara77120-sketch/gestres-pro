"""
Configuration globale des tests : base PostgreSQL de test isolée.

Chaque test utilise la base gestres_test (PostgreSQL).
La base de production gestres_pro n'est JAMAIS touchée pendant les tests.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import src.models.base as base_module

TEST_DATABASE_URL = (
    "postgresql+psycopg2://gestres_user:GestRes2026!Secure"
    "@localhost:5432/gestres_test"
)


def make_test_engine():
    return create_engine(TEST_DATABASE_URL)


@pytest.fixture(autouse=True, scope="function")
def use_test_db():
    """
    Remplace le moteur de production par la base PostgreSQL de test.
    Crée toutes les tables avant chaque test, les supprime après.
    La base gestres_pro n'est jamais touchée.
    """
    test_engine = make_test_engine()

    base_module.Base.metadata.create_all(bind=test_engine)

    original_engine = base_module.engine
    original_session_local = base_module.SessionLocal

    base_module.engine = test_engine
    base_module.SessionLocal = sessionmaker(
        bind=test_engine, autoflush=False, autocommit=False
    )

    import tests.test_controllers as tc
    import tests.test_models as tm
    original_tc_engine = tc.engine
    original_tm_engine = tm.engine
    tc.engine = test_engine
    tm.engine = test_engine

    yield test_engine

    base_module.engine = original_engine
    base_module.SessionLocal = original_session_local
    tc.engine = original_tc_engine
    tm.engine = original_tm_engine

    base_module.Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()
