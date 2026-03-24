import pytest
import json
from datetime import datetime, timezone

from src.models.base import Base, get_session, engine
from src.models.user import User, Role
from src.models.company import Company
from src.controllers.auth_controller import AuthController
from src.controllers.user_controller import UserController
from src.controllers.company_controller import CompanyController


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)

    with get_session() as session:
        roles = [
            Role(name="super_admin", permissions=json.dumps(["all"])),
            Role(name="admin", permissions=json.dumps(["view_resources", "manage_resources"])),
            Role(name="employee", permissions=json.dumps(["view_own_resources"]))
        ]
        for role in roles:
            session.add(role)
        session.commit()

        yield session

    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def auth_controller():
    return AuthController()


@pytest.fixture
def user_controller():
    return UserController()


@pytest.fixture
def company_controller():
    return CompanyController()


class TestAuthController:

    def test_initial_state(self, db_session, auth_controller):
        assert auth_controller.current_user is None
        assert auth_controller.is_authenticated is False

    def test_create_user_success(self, db_session, auth_controller):
        success, msg, user = auth_controller.create_user(
            email="test@example.com",
            password="SecurePass123!",
            first_name="John",
            last_name="Doe",
            role_name="employee"
        )

        assert success is True
        assert user is not None

    def test_create_user_invalid_email(self, db_session, auth_controller):
        success, msg, user = auth_controller.create_user(
            email="invalid-email",
            password="SecurePass123!",
            role_name="employee"
        )

        assert success is False
        assert "email" in msg.lower()
        assert user is None

    def test_create_user_weak_password(self, db_session, auth_controller):
        success, msg, user = auth_controller.create_user(
            email="test@example.com",
            password="weak",
            role_name="employee"
        )

        assert success is False
        assert user is None

    def test_create_user_duplicate_email(self, db_session, auth_controller):
        auth_controller.create_user(
            email="test@example.com",
            password="SecurePass123!",
            role_name="employee"
        )

        success, msg, user = auth_controller.create_user(
            email="test@example.com",
            password="AnotherPass123!",
            role_name="employee"
        )

        assert success is False
        assert "utilisé" in msg.lower()
        assert user is None

    def test_create_user_unknown_role(self, db_session, auth_controller):
        success, msg, user = auth_controller.create_user(
            email="test@example.com",
            password="SecurePass123!",
            role_name="nonexistent_role"
        )

        assert success is False
        assert user is None

    def test_login_success(self, db_session, auth_controller):
        auth_controller.create_user(
            email="test@example.com",
            password="SecurePass123!",
            first_name="John",
            role_name="employee"
        )

        success, msg = auth_controller.login("test@example.com", "SecurePass123!")

        assert success is True
        assert auth_controller.is_authenticated is True
        assert auth_controller.current_user is not None
        assert auth_controller.current_user.email == "test@example.com"

    def test_login_wrong_password(self, db_session, auth_controller):
        auth_controller.create_user(
            email="test@example.com",
            password="SecurePass123!",
            role_name="employee"
        )

        success, msg = auth_controller.login("test@example.com", "WrongPass123!")

        assert success is False
        assert auth_controller.is_authenticated is False

    def test_login_nonexistent_user(self, db_session, auth_controller):
        success, msg = auth_controller.login("nonexistent@example.com", "SomePass123!")

        assert success is False
        assert auth_controller.is_authenticated is False

    def test_login_inactive_user(self, db_session, auth_controller):
        auth_controller.create_user(
            email="test@example.com",
            password="SecurePass123!",
            role_name="employee"
        )

        with get_session() as session:
            user = session.query(User).filter_by(email="test@example.com").first()
            user.is_active = False
            session.commit()

        success, msg = auth_controller.login("test@example.com", "SecurePass123!")

        assert success is False
        assert "désactivé" in msg.lower()

    def test_login_empty_credentials(self, db_session, auth_controller):
        success, msg = auth_controller.login("", "")
        assert success is False

    def test_logout(self, db_session, auth_controller):
        auth_controller.create_user(
            email="test@example.com",
            password="SecurePass123!",
            role_name="employee"
        )
        auth_controller.login("test@example.com", "SecurePass123!")

        assert auth_controller.is_authenticated is True

        result = auth_controller.logout()

        assert result is True
        assert auth_controller.is_authenticated is False
        assert auth_controller.current_user is None

    def test_logout_not_authenticated(self, db_session, auth_controller):
        result = auth_controller.logout()
        assert result is False

    def test_has_permission(self, db_session, auth_controller):
        auth_controller.create_user(
            email="admin@example.com",
            password="SecurePass123!",
            role_name="admin"
        )
        auth_controller.login("admin@example.com", "SecurePass123!")

        assert auth_controller.has_permission("view_resources") is True
        assert auth_controller.has_permission("nonexistent_perm") is False

    def test_has_permission_not_authenticated(self, db_session, auth_controller):
        assert auth_controller.has_permission("view_resources") is False

    def test_has_permission_super_admin(self, db_session, auth_controller):
        auth_controller.create_user(
            email="superadmin@example.com",
            password="SecurePass123!",
            role_name="super_admin"
        )
        auth_controller.login("superadmin@example.com", "SecurePass123!")

        assert auth_controller.has_permission("anything") is True
        assert auth_controller.is_super_admin() is True
        assert auth_controller.is_admin() is True

    def test_is_admin(self, db_session, auth_controller):
        auth_controller.create_user(
            email="admin@example.com",
            password="SecurePass123!",
            role_name="admin"
        )
        auth_controller.login("admin@example.com", "SecurePass123!")

        assert auth_controller.is_admin() is True
        assert auth_controller.is_super_admin() is False

    def test_is_admin_not_authenticated(self, db_session, auth_controller):
        assert auth_controller.is_admin() is False
        assert auth_controller.is_super_admin() is False

    def test_change_password_success(self, db_session, auth_controller):
        auth_controller.create_user(
            email="test@example.com",
            password="SecurePass123!",
            role_name="employee"
        )
        auth_controller.login("test@example.com", "SecurePass123!")

        success, msg = auth_controller.change_password(
            current_password="SecurePass123!",
            new_password="NewSecurePass456!"
        )

        assert success is True

        auth_controller.logout()
        success, _ = auth_controller.login("test@example.com", "NewSecurePass456!")
        assert success is True

    def test_change_password_wrong_current(self, db_session, auth_controller):
        auth_controller.create_user(
            email="test@example.com",
            password="SecurePass123!",
            role_name="employee"
        )
        auth_controller.login("test@example.com", "SecurePass123!")

        success, msg = auth_controller.change_password(
            current_password="WrongPassword!",
            new_password="NewSecurePass456!"
        )

        assert success is False
        assert "incorrect" in msg.lower()

    def test_change_password_weak_new(self, db_session, auth_controller):
        auth_controller.create_user(
            email="test@example.com",
            password="SecurePass123!",
            role_name="employee"
        )
        auth_controller.login("test@example.com", "SecurePass123!")

        success, msg = auth_controller.change_password(
            current_password="SecurePass123!",
            new_password="weak"
        )

        assert success is False

    def test_change_password_not_authenticated(self, db_session, auth_controller):
        success, msg = auth_controller.change_password(
            current_password="anything",
            new_password="NewPass123!"
        )
        assert success is False

    def test_create_initial_super_admin(self, db_session, auth_controller):
        success, msg = auth_controller.create_initial_super_admin(
            email="superadmin@example.com",
            password="SuperSecure123!",
            first_name="Super",
            last_name="Admin"
        )

        assert success is True

    def test_create_initial_super_admin_duplicate(self, db_session, auth_controller):
        auth_controller.create_initial_super_admin(
            email="superadmin@example.com",
            password="SuperSecure123!"
        )

        success2, msg2 = auth_controller.create_initial_super_admin(
            email="another@example.com",
            password="AnotherPass123!"
        )

        assert success2 is False
        assert "existe déjà" in msg2.lower()

    def test_login_updates_last_login(self, db_session, auth_controller):
        auth_controller.create_user(
            email="test@example.com",
            password="SecurePass123!",
            role_name="employee"
        )

        with get_session() as session:
            user = session.query(User).filter_by(email="test@example.com").first()
            assert user.last_login is None

        auth_controller.login("test@example.com", "SecurePass123!")

        with get_session() as session:
            user = session.query(User).filter_by(email="test@example.com").first()
            assert user.last_login is not None

    def test_login_case_insensitive_email(self, db_session, auth_controller):
        auth_controller.create_user(
            email="test@example.com",
            password="SecurePass123!",
            role_name="employee"
        )

        success, msg = auth_controller.login("TEST@EXAMPLE.COM", "SecurePass123!")
        assert success is True


class TestUserController:

    def test_get_all_users_empty(self, db_session, user_controller):
        users = user_controller.get_all_users()
        assert isinstance(users, list)
        assert len(users) == 0

    def test_create_user_success(self, db_session, user_controller):
        role = db_session.query(Role).filter_by(name="employee").first()

        success, msg, user_id = user_controller.create_user(
            email="john@example.com",
            password="SecurePass123!",
            first_name="John",
            last_name="Doe",
            role_id=role.id
        )

        assert success is True
        assert user_id is not None
        assert isinstance(user_id, int)

    def test_create_user_invalid_email(self, db_session, user_controller):
        role = db_session.query(Role).filter_by(name="employee").first()

        success, msg, user_id = user_controller.create_user(
            email="not_an_email",
            password="SecurePass123!",
            first_name="John",
            last_name="Doe",
            role_id=role.id
        )

        assert success is False
        assert user_id is None

    def test_create_user_duplicate_email(self, db_session, user_controller):
        role = db_session.query(Role).filter_by(name="employee").first()

        user_controller.create_user(
            email="dup@example.com",
            password="SecurePass123!",
            first_name="A",
            last_name="B",
            role_id=role.id
        )

        success, msg, user_id = user_controller.create_user(
            email="dup@example.com",
            password="SecurePass123!",
            first_name="C",
            last_name="D",
            role_id=role.id
        )

        assert success is False
        assert "utilisé" in msg.lower()

    def test_create_user_invalid_role(self, db_session, user_controller):
        success, msg, user_id = user_controller.create_user(
            email="x@example.com",
            password="SecurePass123!",
            first_name="X",
            last_name="Y",
            role_id=9999
        )

        assert success is False
        assert "rôle" in msg.lower()

    def test_get_all_users_after_create(self, db_session, user_controller):
        role = db_session.query(Role).filter_by(name="employee").first()

        user_controller.create_user(
            email="alice@example.com",
            password="SecurePass123!",
            first_name="Alice",
            last_name="Durand",
            role_id=role.id
        )

        users = user_controller.get_all_users()
        assert len(users) == 1
        assert users[0]["email"] == "alice@example.com"

    def test_get_user_by_id(self, db_session, user_controller):
        role = db_session.query(Role).filter_by(name="employee").first()

        _, _, user_id = user_controller.create_user(
            email="bob@example.com",
            password="SecurePass123!",
            first_name="Bob",
            last_name="Smith",
            role_id=role.id
        )

        user_data = user_controller.get_user_by_id(user_id)
        assert user_data is not None
        assert user_data["email"] == "bob@example.com"
        assert user_data["first_name"] == "Bob"

    def test_get_user_by_id_not_found(self, db_session, user_controller):
        result = user_controller.get_user_by_id(9999)
        assert result is None

    def test_update_user_name(self, db_session, user_controller):
        role = db_session.query(Role).filter_by(name="employee").first()

        _, _, user_id = user_controller.create_user(
            email="charlie@example.com",
            password="SecurePass123!",
            first_name="Charlie",
            last_name="Old",
            role_id=role.id
        )

        success, msg = user_controller.update_user(user_id, last_name="New")
        assert success is True

        user_data = user_controller.get_user_by_id(user_id)
        assert user_data["last_name"] == "New"

    def test_update_user_not_found(self, db_session, user_controller):
        success, msg = user_controller.update_user(9999, first_name="Nobody")
        assert success is False
        assert "trouvé" in msg.lower()

    def test_update_user_invalid_email(self, db_session, user_controller):
        role = db_session.query(Role).filter_by(name="employee").first()

        _, _, user_id = user_controller.create_user(
            email="dave@example.com",
            password="SecurePass123!",
            first_name="Dave",
            last_name="D",
            role_id=role.id
        )

        success, msg = user_controller.update_user(user_id, email="bad-email")
        assert success is False

    def test_delete_user(self, db_session, user_controller):
        role = db_session.query(Role).filter_by(name="employee").first()

        _, _, user_id = user_controller.create_user(
            email="todelete@example.com",
            password="SecurePass123!",
            first_name="Delete",
            last_name="Me",
            role_id=role.id
        )

        success, msg = user_controller.delete_user(user_id)
        assert success is True

        user_data = user_controller.get_user_by_id(user_id)
        assert user_data["is_active"] is False

    def test_delete_user_not_found(self, db_session, user_controller):
        success, msg = user_controller.delete_user(9999)
        assert success is False
        assert "trouvé" in msg.lower()

    def test_reset_password_success(self, db_session, user_controller):
        role = db_session.query(Role).filter_by(name="employee").first()

        _, _, user_id = user_controller.create_user(
            email="reset@example.com",
            password="OldPass123!",
            first_name="Reset",
            last_name="Me",
            role_id=role.id
        )

        success, msg = user_controller.reset_password(user_id, "NewPass456!")
        assert success is True

    def test_reset_password_weak(self, db_session, user_controller):
        role = db_session.query(Role).filter_by(name="employee").first()

        _, _, user_id = user_controller.create_user(
            email="reset2@example.com",
            password="OldPass123!",
            first_name="Reset",
            last_name="Weak",
            role_id=role.id
        )

        success, msg = user_controller.reset_password(user_id, "weak")
        assert success is False

    def test_reset_password_user_not_found(self, db_session, user_controller):
        success, msg = user_controller.reset_password(9999, "NewPass456!")
        assert success is False

    def test_get_all_roles(self, db_session, user_controller):
        roles = user_controller.get_all_roles()
        assert len(roles) == 3
        role_names = [r["name"] for r in roles]
        assert "super_admin" in role_names
        assert "admin" in role_names
        assert "employee" in role_names

    def test_get_users_by_company(self, db_session, user_controller):
        company = Company(name="Corp A")
        db_session.add(company)
        db_session.commit()

        role = db_session.query(Role).filter_by(name="employee").first()

        user_controller.create_user(
            email="emp1@corp.com",
            password="SecurePass123!",
            first_name="Emp",
            last_name="One",
            role_id=role.id,
            company_id=company.id
        )
        user_controller.create_user(
            email="emp2@other.com",
            password="SecurePass123!",
            first_name="Emp",
            last_name="Two",
            role_id=role.id
        )

        company_users = user_controller.get_all_users(company_id=company.id)
        assert len(company_users) == 1
        assert company_users[0]["email"] == "emp1@corp.com"


class TestCompanyController:

    def test_create_company_success(self, db_session, company_controller):
        success, msg, company_id = company_controller.create_company(
            name="Test Corp",
            address="10 rue de la Paix"
        )

        assert success is True
        assert company_id is not None

    def test_create_company_with_siret(self, db_session, company_controller):
        success, msg, company_id = company_controller.create_company(
            name="Corp SIRET",
            siret="73282932000074"
        )

        assert success is True

    def test_create_company_invalid_siret(self, db_session, company_controller):
        success, msg, company_id = company_controller.create_company(
            name="Bad SIRET Corp",
            siret="11111111111111"
        )

        assert success is False
        assert "siret" in msg.lower()

    def test_create_company_short_name(self, db_session, company_controller):
        success, msg, company_id = company_controller.create_company(name="A")

        assert success is False
        assert company_id is None

    def test_create_company_duplicate_siret(self, db_session, company_controller):
        company_controller.create_company(name="Corp 1", siret="73282932000074")

        success, msg, company_id = company_controller.create_company(
            name="Corp 2",
            siret="73282932000074"
        )

        assert success is False
        assert "siret" in msg.lower()

    def test_get_all_companies_empty(self, db_session, company_controller):
        companies = company_controller.get_all_companies()
        assert isinstance(companies, list)
        assert len(companies) == 0

    def test_get_all_companies(self, db_session, company_controller):
        company_controller.create_company(name="Company A")
        company_controller.create_company(name="Company B")

        companies = company_controller.get_all_companies()
        assert len(companies) == 2

    def test_get_company_by_id(self, db_session, company_controller):
        _, _, company_id = company_controller.create_company(
            name="Lookup Corp",
            address="5 avenue Test"
        )

        data = company_controller.get_company_by_id(company_id)
        assert data is not None
        assert data["name"] == "Lookup Corp"

    def test_get_company_by_id_not_found(self, db_session, company_controller):
        result = company_controller.get_company_by_id(9999)
        assert result is None

    def test_update_company_name(self, db_session, company_controller):
        _, _, company_id = company_controller.create_company(name="Old Name")

        success, msg = company_controller.update_company(company_id, name="New Name")
        assert success is True

        data = company_controller.get_company_by_id(company_id)
        assert data["name"] == "New Name"

    def test_update_company_not_found(self, db_session, company_controller):
        success, msg = company_controller.update_company(9999, name="Nowhere")
        assert success is False
        assert "trouvée" in msg.lower()

    def test_update_company_invalid_siret(self, db_session, company_controller):
        _, _, company_id = company_controller.create_company(name="Corp Test")

        success, msg = company_controller.update_company(company_id, siret="11111111111111")
        assert success is False

    def test_delete_company_success(self, db_session, company_controller):
        _, _, company_id = company_controller.create_company(name="To Delete")

        success, msg = company_controller.delete_company(company_id)
        assert success is True

        data = company_controller.get_company_by_id(company_id)
        assert data["is_active"] is False

    def test_delete_company_with_active_users(self, db_session, company_controller, user_controller):
        _, _, company_id = company_controller.create_company(name="Has Users")

        role = db_session.query(Role).filter_by(name="employee").first()
        user_controller.create_user(
            email="emp@hasusers.com",
            password="SecurePass123!",
            first_name="Emp",
            last_name="Test",
            role_id=role.id,
            company_id=company_id
        )

        success, msg = company_controller.delete_company(company_id)
        assert success is False
        assert "utilisateur" in msg.lower()

    def test_delete_company_not_found(self, db_session, company_controller):
        success, msg = company_controller.delete_company(9999)
        assert success is False

    def test_get_company_stats(self, db_session, company_controller):
        _, _, company_id = company_controller.create_company(name="Stats Corp")

        stats = company_controller.get_company_stats(company_id)
        assert "users_count" in stats
        assert "resources_count" in stats
        assert "available_resources" in stats
        assert stats["users_count"] == 0

    def test_get_all_companies_excludes_inactive(self, db_session, company_controller):
        company_controller.create_company(name="Active Corp")
        _, _, cid = company_controller.create_company(name="Will Deactivate")
        company_controller.delete_company(cid)

        active = company_controller.get_all_companies(include_inactive=False)
        all_companies = company_controller.get_all_companies(include_inactive=True)

        assert len(active) == 1
        assert len(all_companies) == 2
