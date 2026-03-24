import pytest
import json
from datetime import datetime, timedelta, timezone

from src.models.base import Base, get_session, engine
from src.models.company import Company
from src.models.user import User, Role
from src.models.resource_type import ResourceType
from src.models.resource import Resource
from src.models.assignment import Assignment
from src.models.contract import Contract
from src.models.audit_log import AuditLog, Session


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)

    with get_session() as session:
        role = Role(name="test_role", permissions=json.dumps(["view_resources"]))
        session.add(role)
        session.commit()

        yield session

    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def populated_db(db_session):
    company = Company(name="Test Corp", siret="73282932000074", address="10 rue Test")
    db_session.add(company)
    db_session.commit()

    role = db_session.query(Role).filter_by(name="test_role").first()
    user = User(
        email="user@test.com",
        password_hash="hashed",
        first_name="Alice",
        last_name="Martin",
        role_id=role.id,
        company_id=company.id
    )
    db_session.add(user)
    db_session.commit()

    rt = ResourceType(company_id=company.id, name="Laptop", description="Ordinateurs")
    db_session.add(rt)
    db_session.commit()

    resource = Resource(
        company_id=company.id,
        resource_type_id=rt.id,
        name="MacBook Pro",
        serial_number="SN001"
    )
    db_session.add(resource)
    db_session.commit()

    return {"session": db_session, "company": company, "user": user, "role": role, "rt": rt, "resource": resource}


class TestCompany:

    def test_create_company(self, db_session):
        company = Company(name="Test Enterprise", siret="12345678901234", address="123 Test Street")
        db_session.add(company)
        db_session.commit()

        assert company.id is not None
        assert company.name == "Test Enterprise"
        assert company.is_active is True
        assert company.created_at is not None

    def test_company_default_active(self, db_session):
        company = Company(name="Minimal Corp")
        db_session.add(company)
        db_session.commit()

        assert company.is_active is True

    def test_company_without_siret(self, db_session):
        company = Company(name="No Siret Inc")
        db_session.add(company)
        db_session.commit()

        assert company.siret is None

    def test_company_repr(self, db_session):
        company = Company(name="Test Co")
        db_session.add(company)
        db_session.commit()

        assert "Test Co" in repr(company)

    def test_company_deactivation(self, db_session):
        company = Company(name="To Deactivate")
        db_session.add(company)
        db_session.commit()

        company.is_active = False
        db_session.commit()

        assert company.is_active is False

    def test_multiple_companies(self, db_session):
        for i in range(5):
            db_session.add(Company(name=f"Company {i}"))
        db_session.commit()

        count = db_session.query(Company).count()
        assert count == 5


class TestRole:

    def test_get_permissions(self, db_session):
        role = db_session.query(Role).filter_by(name="test_role").first()
        perms = role.get_permissions()

        assert "view_resources" in perms

    def test_has_permission(self, db_session):
        role = db_session.query(Role).filter_by(name="test_role").first()

        assert role.has_permission("view_resources") is True
        assert role.has_permission("delete_all") is False

    def test_has_permission_all(self, db_session):
        role = Role(name="admin_test", permissions=json.dumps(["all"]))
        db_session.add(role)
        db_session.commit()

        assert role.has_permission("anything") is True
        assert role.has_permission("create_users") is True

    def test_role_empty_permissions(self, db_session):
        role = Role(name="empty_role", permissions=json.dumps([]))
        db_session.add(role)
        db_session.commit()

        assert role.has_permission("view_resources") is False
        assert role.get_permissions() == []

    def test_role_multiple_permissions(self, db_session):
        role = Role(name="multi_role", permissions=json.dumps(["read", "write", "delete"]))
        db_session.add(role)
        db_session.commit()

        assert role.has_permission("read") is True
        assert role.has_permission("write") is True
        assert role.has_permission("delete") is True
        assert role.has_permission("admin") is False

    def test_role_repr(self, db_session):
        role = db_session.query(Role).filter_by(name="test_role").first()
        assert "test_role" in repr(role)


class TestUser:

    def test_create_user(self, db_session):
        role = db_session.query(Role).filter_by(name="test_role").first()
        user = User(
            email="test@example.com",
            password_hash="hashed_password",
            first_name="John",
            last_name="Doe",
            role_id=role.id
        )
        db_session.add(user)
        db_session.commit()

        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.is_active is True

    def test_full_name_with_both_names(self, db_session):
        role = db_session.query(Role).filter_by(name="test_role").first()
        user = User(email="a@b.com", password_hash="h", first_name="John", last_name="Doe", role_id=role.id)

        assert user.full_name == "John Doe"

    def test_full_name_first_name_only(self, db_session):
        role = db_session.query(Role).filter_by(name="test_role").first()
        user = User(email="b@b.com", password_hash="h", first_name="Jane", role_id=role.id)

        assert user.full_name == "Jane"

    def test_full_name_fallback_to_email(self, db_session):
        role = db_session.query(Role).filter_by(name="test_role").first()
        user = User(email="fallback@b.com", password_hash="h", role_id=role.id)

        assert user.full_name == "fallback@b.com"

    def test_user_default_active(self, db_session):
        role = db_session.query(Role).filter_by(name="test_role").first()
        user = User(email="active@test.com", password_hash="h", role_id=role.id)
        db_session.add(user)
        db_session.commit()

        assert user.is_active is True

    def test_user_last_login_initially_none(self, db_session):
        role = db_session.query(Role).filter_by(name="test_role").first()
        user = User(email="new@test.com", password_hash="h", role_id=role.id)
        db_session.add(user)
        db_session.commit()

        assert user.last_login is None

    def test_user_repr(self, db_session):
        role = db_session.query(Role).filter_by(name="test_role").first()
        user = User(email="repr@test.com", password_hash="h", role_id=role.id)
        db_session.add(user)
        db_session.commit()

        assert "repr@test.com" in repr(user)

    def test_user_soft_delete(self, db_session):
        role = db_session.query(Role).filter_by(name="test_role").first()
        user = User(email="delete@test.com", password_hash="h", role_id=role.id)
        db_session.add(user)
        db_session.commit()

        user.is_active = False
        db_session.commit()

        fetched = db_session.query(User).filter_by(email="delete@test.com").first()
        assert fetched.is_active is False

    def test_user_has_permission_via_role(self, db_session):
        role = db_session.query(Role).filter_by(name="test_role").first()
        user = User(email="perm@test.com", password_hash="h", role_id=role.id)
        db_session.add(user)
        db_session.commit()

        db_session.refresh(user)
        assert user.has_permission("view_resources") is True
        assert user.has_permission("admin") is False


class TestResourceType:

    def test_custom_fields(self, db_session):
        company = Company(name="Test Co")
        db_session.add(company)
        db_session.commit()

        rt = ResourceType(company_id=company.id, name="Ordinateur", description="Ordinateurs portables")
        custom_fields = [
            {"name": "ram", "type": "string", "label": "RAM"},
            {"name": "storage", "type": "string", "label": "Stockage"}
        ]
        rt.set_custom_fields(custom_fields)
        db_session.add(rt)
        db_session.commit()

        loaded = rt.get_custom_fields()
        assert len(loaded) == 2
        assert loaded[0]["name"] == "ram"

    def test_empty_custom_fields(self, db_session):
        company = Company(name="Test Co 2")
        db_session.add(company)
        db_session.commit()

        rt = ResourceType(company_id=company.id, name="Téléphone")
        db_session.add(rt)
        db_session.commit()

        assert rt.get_custom_fields() == []

    def test_set_then_override_custom_fields(self, db_session):
        company = Company(name="Test Co 3")
        db_session.add(company)
        db_session.commit()

        rt = ResourceType(company_id=company.id, name="Tablette")
        rt.set_custom_fields([{"name": "os", "type": "string", "label": "OS"}])
        rt.set_custom_fields([{"name": "screen", "type": "string", "label": "Écran"}])
        db_session.add(rt)
        db_session.commit()

        fields = rt.get_custom_fields()
        assert len(fields) == 1
        assert fields[0]["name"] == "screen"

    def test_resource_type_repr(self, db_session):
        company = Company(name="Test Co 4")
        db_session.add(company)
        db_session.commit()

        rt = ResourceType(company_id=company.id, name="Imprimante")
        db_session.add(rt)
        db_session.commit()

        assert "Imprimante" in repr(rt)


class TestResource:

    def test_create_resource(self, db_session):
        company = Company(name="Test Co")
        db_session.add(company)
        db_session.commit()

        rt = ResourceType(company_id=company.id, name="Laptop")
        db_session.add(rt)
        db_session.commit()

        resource = Resource(
            company_id=company.id,
            resource_type_id=rt.id,
            name="MacBook Pro 2023",
            serial_number="ABC123"
        )
        db_session.add(resource)
        db_session.commit()

        assert resource.id is not None
        assert resource.status == "available"
        assert resource.is_available is True

    def test_resource_custom_data(self, db_session):
        company = Company(name="Test Co")
        db_session.add(company)
        db_session.commit()

        rt = ResourceType(company_id=company.id, name="Laptop")
        db_session.add(rt)
        db_session.commit()

        resource = Resource(company_id=company.id, resource_type_id=rt.id, name="MacBook")
        resource.set_custom_data({"ram": "16GB", "storage": "512GB"})
        db_session.add(resource)
        db_session.commit()

        data = resource.get_custom_data()
        assert data["ram"] == "16GB"
        assert data["storage"] == "512GB"

    def test_resource_empty_custom_data(self, db_session):
        company = Company(name="Test Co")
        db_session.add(company)
        db_session.commit()

        rt = ResourceType(company_id=company.id, name="Laptop")
        db_session.add(rt)
        db_session.commit()

        resource = Resource(company_id=company.id, resource_type_id=rt.id, name="Dell")
        db_session.add(resource)
        db_session.commit()

        assert resource.get_custom_data() == {}

    def test_resource_status_change(self, db_session):
        company = Company(name="Test Co")
        db_session.add(company)
        db_session.commit()

        rt = ResourceType(company_id=company.id, name="Laptop")
        db_session.add(rt)
        db_session.commit()

        resource = Resource(company_id=company.id, resource_type_id=rt.id, name="ThinkPad")
        db_session.add(resource)
        db_session.commit()

        assert resource.is_available is True

        resource.status = "assigned"
        db_session.commit()

        assert resource.is_available is False

    def test_resource_repr(self, db_session):
        company = Company(name="Test Co")
        db_session.add(company)
        db_session.commit()

        rt = ResourceType(company_id=company.id, name="Laptop")
        db_session.add(rt)
        db_session.commit()

        resource = Resource(company_id=company.id, resource_type_id=rt.id, name="Surface Pro")
        db_session.add(resource)
        db_session.commit()

        assert "Surface Pro" in repr(resource)


class TestAssignment:

    def test_create_assignment(self, populated_db):
        data = populated_db
        session = data["session"]

        assignment = Assignment(
            resource_id=data["resource"].id,
            user_id=data["user"].id,
            assigned_by=data["user"].id,
            start_date=datetime.now(timezone.utc)
        )
        session.add(assignment)
        session.commit()

        assert assignment.id is not None
        assert assignment.status == "active"
        assert assignment.is_active is True

    def test_assignment_is_active_property(self, populated_db):
        data = populated_db
        session = data["session"]

        assignment = Assignment(
            resource_id=data["resource"].id,
            user_id=data["user"].id,
            assigned_by=data["user"].id,
            start_date=datetime.now(timezone.utc),
            status="active"
        )
        session.add(assignment)
        session.commit()

        assert assignment.is_active is True

        assignment.status = "returned"
        assert assignment.is_active is False

    def test_assignment_with_end_date(self, populated_db):
        data = populated_db
        session = data["session"]

        start = datetime.now(timezone.utc).replace(tzinfo=None)
        end = start + timedelta(days=30)

        assignment = Assignment(
            resource_id=data["resource"].id,
            user_id=data["user"].id,
            assigned_by=data["user"].id,
            start_date=start,
            end_date=end
        )
        session.add(assignment)
        session.commit()

        assert assignment.duration_days == 30

    def test_assignment_repr(self, populated_db):
        data = populated_db
        session = data["session"]

        assignment = Assignment(
            resource_id=data["resource"].id,
            user_id=data["user"].id,
            assigned_by=data["user"].id,
            start_date=datetime.now(timezone.utc)
        )
        session.add(assignment)
        session.commit()

        r = repr(assignment)
        assert "Assignment" in r


class TestContract:

    def test_compute_hash_deterministic(self):
        content = "Test contract content"
        assert Contract.compute_hash(content) == Contract.compute_hash(content)

    def test_compute_hash_length(self):
        assert len(Contract.compute_hash("anything")) == 64  # SHA-256

    def test_different_content_different_hash(self):
        assert Contract.compute_hash("content A") != Contract.compute_hash("content B")

    def test_verify_integrity_ok(self, populated_db):
        data = populated_db
        session = data["session"]

        assignment = Assignment(
            resource_id=data["resource"].id,
            user_id=data["user"].id,
            assigned_by=data["user"].id,
            start_date=datetime.now(timezone.utc)
        )
        session.add(assignment)
        session.commit()

        content = "Contract content"
        contract = Contract(
            assignment_id=assignment.id,
            content=content,
            content_hash=Contract.compute_hash(content)
        )
        session.add(contract)
        session.commit()

        assert contract.verify_integrity() is True

    def test_verify_integrity_tampered(self, populated_db):
        data = populated_db
        session = data["session"]

        assignment = Assignment(
            resource_id=data["resource"].id,
            user_id=data["user"].id,
            assigned_by=data["user"].id,
            start_date=datetime.now(timezone.utc)
        )
        session.add(assignment)
        session.commit()

        content = "Original content"
        contract = Contract(
            assignment_id=assignment.id,
            content=content,
            content_hash=Contract.compute_hash(content)
        )
        session.add(contract)
        session.commit()

        contract.content = "Tampered content"
        assert contract.verify_integrity() is False

    def test_sign_contract(self, populated_db):
        data = populated_db
        session = data["session"]

        assignment = Assignment(
            resource_id=data["resource"].id,
            user_id=data["user"].id,
            assigned_by=data["user"].id,
            start_date=datetime.now(timezone.utc)
        )
        session.add(assignment)
        session.commit()

        content = "Contract content"
        contract = Contract(
            assignment_id=assignment.id,
            content=content,
            content_hash=Contract.compute_hash(content)
        )
        session.add(contract)
        session.commit()

        assert contract.is_signed is False
        contract.sign("user@email.com")
        assert contract.is_signed is True
        assert contract.signature_hash is not None
        assert contract.signed_at is not None

    def test_contract_repr(self, populated_db):
        data = populated_db
        session = data["session"]

        assignment = Assignment(
            resource_id=data["resource"].id,
            user_id=data["user"].id,
            assigned_by=data["user"].id,
            start_date=datetime.now(timezone.utc)
        )
        session.add(assignment)
        session.commit()

        content = "Content"
        contract = Contract(
            assignment_id=assignment.id,
            content=content,
            content_hash=Contract.compute_hash(content)
        )
        session.add(contract)
        session.commit()

        assert "Contract" in repr(contract)


class TestAuditLog:

    def test_create_log(self, db_session):
        log = AuditLog.log(
            action="CREATE",
            table_name="users",
            record_id=1,
            new_values={"email": "test@example.com"}
        )
        db_session.add(log)
        db_session.commit()

        assert log.id is not None
        assert log.get_new_values()["email"] == "test@example.com"

    def test_log_old_values(self, db_session):
        log = AuditLog.log(
            action="UPDATE",
            table_name="users",
            record_id=1,
            old_values={"email": "old@example.com"},
            new_values={"email": "new@example.com"}
        )
        db_session.add(log)
        db_session.commit()

        assert log.get_old_values()["email"] == "old@example.com"
        assert log.get_new_values()["email"] == "new@example.com"

    def test_log_no_values_returns_empty_dict(self, db_session):
        log = AuditLog.log(action="LOGIN", user_id=None)
        db_session.add(log)
        db_session.commit()

        assert log.get_old_values() == {}
        assert log.get_new_values() == {}

    def test_log_with_ip(self, db_session):
        log = AuditLog.log(action="LOGIN", ip_address="192.168.1.1")
        db_session.add(log)
        db_session.commit()

        assert log.ip_address == "192.168.1.1"

    def test_log_repr(self, db_session):
        log = AuditLog.log(action="DELETE", table_name="resources", record_id=5)
        db_session.add(log)
        db_session.commit()

        assert "DELETE" in repr(log)

    def test_log_created_at(self, db_session):
        before = datetime.now(timezone.utc)
        log = AuditLog.log(action="CREATE")
        db_session.add(log)
        db_session.commit()
        after = datetime.now(timezone.utc)

        created = log.created_at
        if created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)

        assert before <= created <= after


class TestSession:

    def test_session_expired(self, db_session):
        role = db_session.query(Role).filter_by(name="test_role").first()
        user = User(email="s@t.com", password_hash="h", role_id=role.id)
        db_session.add(user)
        db_session.commit()

        expired = Session(
            user_id=user.id,
            token_hash="hash1",
            expires_at=datetime.now(timezone.utc) - timedelta(hours=1)
        )
        db_session.add(expired)
        db_session.commit()

        assert expired.is_expired is True
        assert expired.is_valid is False

    def test_session_valid(self, db_session):
        role = db_session.query(Role).filter_by(name="test_role").first()
        user = User(email="s2@t.com", password_hash="h", role_id=role.id)
        db_session.add(user)
        db_session.commit()

        valid = Session(
            user_id=user.id,
            token_hash="hash2",
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1)
        )
        db_session.add(valid)
        db_session.commit()

        assert valid.is_expired is False
        assert valid.is_valid is True

    def test_session_repr(self, db_session):
        role = db_session.query(Role).filter_by(name="test_role").first()
        user = User(email="s3@t.com", password_hash="h", role_id=role.id)
        db_session.add(user)
        db_session.commit()

        session = Session(
            user_id=user.id,
            token_hash="hash3",
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1)
        )
        db_session.add(session)
        db_session.commit()

        assert "Session" in repr(session)

    def test_session_just_expired(self, db_session):
        role = db_session.query(Role).filter_by(name="test_role").first()
        user = User(email="s4@t.com", password_hash="h", role_id=role.id)
        db_session.add(user)
        db_session.commit()

        just_expired = Session(
            user_id=user.id,
            token_hash="hash4",
            expires_at=datetime.now(timezone.utc) - timedelta(seconds=1)
        )
        db_session.add(just_expired)
        db_session.commit()

        assert just_expired.is_expired is True
