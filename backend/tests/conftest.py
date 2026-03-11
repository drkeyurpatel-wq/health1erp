"""
Shared fixtures for the hospital-management-system test suite.

Uses an in-memory SQLite database (via aiosqlite) so tests are fast and
completely isolated from any external services.
"""

import asyncio
import uuid
from datetime import date, datetime, time, timedelta, timezone
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event, text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

# ---------------------------------------------------------------------------
# The application must be importable *before* we touch the database layer,
# but the module-level ``engine`` in ``database.py`` will try to connect to
# Postgres.  We therefore override ``get_db`` *before* any request is sent.
# ---------------------------------------------------------------------------
from app.core.database import Base, get_db
from app.core.security import create_access_token, get_password_hash
from app.models.user import User, UserRole

# Import every model so ``Base.metadata`` is fully populated when we call
# ``create_all``.  Order matters for FK constraints.
from app.models.staff import Department, DoctorProfile  # noqa: F401
from app.models.patient import Patient  # noqa: F401
from app.models.appointment import Appointment  # noqa: F401
from app.models.ipd import (  # noqa: F401
    Ward, Bed, Admission, DoctorRound, NursingAssessment, DischargePlanning,
)
from app.models.billing import Bill, BillItem, Payment, InsuranceClaim  # noqa: F401
from app.models.inventory import (  # noqa: F401
    Supplier, Item, ItemBatch, StockMovement, PurchaseOrder,
)
from app.models.pharmacy import Prescription, PrescriptionItem, Dispensation  # noqa: F401
from app.models.laboratory import LabTest, LabOrder, LabResult  # noqa: F401

from app.main import app

# ---------- async event-loop scope ----------------------------------------

@pytest.fixture(scope="session")
def event_loop():
    """Create a single event loop for the whole test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# ---------- SQLite engine & session ---------------------------------------

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# SQLite doesn't support PostgreSQL-specific features; we need to handle
# UUID columns (stored as CHAR(32)) and JSONB (stored as JSON/TEXT).

@pytest_asyncio.fixture(scope="session")
async def _engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    # SQLite needs ``PRAGMA foreign_keys = ON`` per-connection.
    @event.listens_for(engine.sync_engine, "connect")
    def _set_sqlite_pragma(dbapi_conn, _):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(_engine) -> AsyncGenerator[AsyncSession, None]:
    """Provide a fresh transactional session that is rolled back after
    every test so that tests stay fully independent."""
    session_factory = async_sessionmaker(
        _engine, class_=AsyncSession, expire_on_commit=False,
    )
    async with session_factory() as session:
        async with session.begin():
            yield session
            # Roll back everything the test did.
            await session.rollback()


# ---------- Dependency override -------------------------------------------

@pytest_asyncio.fixture
async def client(db_session: AsyncSession, admin_user) -> AsyncGenerator[AsyncClient, None]:
    """Authenticated HTTP client (Admin role)."""

    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db

    token = create_access_token(admin_user.id, admin_user.role.value)
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://testserver",
        headers={"Authorization": f"Bearer {token}"},
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def unauth_client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Unauthenticated HTTP client."""

    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def doctor_client(db_session: AsyncSession, doctor_user) -> AsyncGenerator[AsyncClient, None]:
    """Authenticated HTTP client (Doctor role)."""

    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db

    token = create_access_token(doctor_user.id, doctor_user.role.value)
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://testserver",
        headers={"Authorization": f"Bearer {token}"},
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def nurse_client(db_session: AsyncSession, nurse_user) -> AsyncGenerator[AsyncClient, None]:
    """Authenticated HTTP client (Nurse role)."""

    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db

    token = create_access_token(nurse_user.id, nurse_user.role.value)
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://testserver",
        headers={"Authorization": f"Bearer {token}"},
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def pharmacist_client(db_session: AsyncSession, pharmacist_user) -> AsyncGenerator[AsyncClient, None]:
    """Authenticated HTTP client (Pharmacist role)."""

    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db

    token = create_access_token(pharmacist_user.id, pharmacist_user.role.value)
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://testserver",
        headers={"Authorization": f"Bearer {token}"},
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def lab_tech_client(db_session: AsyncSession, lab_tech_user) -> AsyncGenerator[AsyncClient, None]:
    """Authenticated HTTP client (LabTech role)."""

    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db

    token = create_access_token(lab_tech_user.id, lab_tech_user.role.value)
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://testserver",
        headers={"Authorization": f"Bearer {token}"},
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def receptionist_client(db_session: AsyncSession, receptionist_user) -> AsyncGenerator[AsyncClient, None]:
    """Authenticated HTTP client (Receptionist role)."""

    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db

    token = create_access_token(receptionist_user.id, receptionist_user.role.value)
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://testserver",
        headers={"Authorization": f"Bearer {token}"},
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def accountant_client(db_session: AsyncSession, accountant_user) -> AsyncGenerator[AsyncClient, None]:
    """Authenticated HTTP client (Accountant role)."""

    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db

    token = create_access_token(accountant_user.id, accountant_user.role.value)
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://testserver",
        headers={"Authorization": f"Bearer {token}"},
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


# ========================== User factory helpers ==========================

async def _make_user(session: AsyncSession, *, role: UserRole, email: str, **kw) -> User:
    user = User(
        id=uuid.uuid4(),
        email=email,
        password_hash=get_password_hash("TestPass123!"),
        first_name=kw.get("first_name", role.value),
        last_name=kw.get("last_name", "User"),
        role=role,
        is_active=True,
        is_verified=True,
    )
    session.add(user)
    await session.flush()
    return user


@pytest_asyncio.fixture
async def admin_user(db_session: AsyncSession) -> User:
    return await _make_user(db_session, role=UserRole.Admin, email="admin@test.com")


@pytest_asyncio.fixture
async def doctor_user(db_session: AsyncSession) -> User:
    return await _make_user(db_session, role=UserRole.Doctor, email="doctor@test.com",
                            first_name="John", last_name="Smith")


@pytest_asyncio.fixture
async def nurse_user(db_session: AsyncSession) -> User:
    return await _make_user(db_session, role=UserRole.Nurse, email="nurse@test.com")


@pytest_asyncio.fixture
async def pharmacist_user(db_session: AsyncSession) -> User:
    return await _make_user(db_session, role=UserRole.Pharmacist, email="pharmacist@test.com")


@pytest_asyncio.fixture
async def lab_tech_user(db_session: AsyncSession) -> User:
    return await _make_user(db_session, role=UserRole.LabTech, email="labtech@test.com")


@pytest_asyncio.fixture
async def receptionist_user(db_session: AsyncSession) -> User:
    return await _make_user(db_session, role=UserRole.Receptionist, email="receptionist@test.com")


@pytest_asyncio.fixture
async def accountant_user(db_session: AsyncSession) -> User:
    return await _make_user(db_session, role=UserRole.Accountant, email="accountant@test.com")


# ========================== Domain-entity helpers =========================

@pytest_asyncio.fixture
async def sample_patient(db_session: AsyncSession) -> Patient:
    patient = Patient(
        id=uuid.uuid4(),
        uhid=f"UH{uuid.uuid4().hex[:8].upper()}",
        first_name="Jane",
        last_name="Doe",
        date_of_birth=date(1990, 5, 15),
        gender="Female",
        blood_group="O+",
        phone="+919876543210",
        email="jane@example.com",
        address={"street": "123 Main St", "city": "Mumbai"},
        emergency_contact={"name": "John Doe", "phone": "+919876543211"},
        allergies=["Penicillin"],
        nationality="Indian",
    )
    db_session.add(patient)
    await db_session.flush()
    return patient


@pytest_asyncio.fixture
async def sample_department(db_session: AsyncSession) -> Department:
    dept = Department(
        id=uuid.uuid4(),
        name="General Medicine",
        code="GM",
        is_clinical=True,
    )
    db_session.add(dept)
    await db_session.flush()
    return dept


@pytest_asyncio.fixture
async def sample_ward(db_session: AsyncSession, sample_department) -> Ward:
    from app.models.ipd import BedType
    ward = Ward(
        id=uuid.uuid4(),
        name="Ward A",
        department_id=sample_department.id,
        total_beds=10,
        ward_type=BedType.General,
        floor=1,
    )
    db_session.add(ward)
    await db_session.flush()
    return ward


@pytest_asyncio.fixture
async def sample_bed(db_session: AsyncSession, sample_ward) -> Bed:
    from app.models.ipd import BedStatus, BedType
    bed = Bed(
        id=uuid.uuid4(),
        ward_id=sample_ward.id,
        bed_number="A-101",
        bed_type=BedType.General,
        status=BedStatus.Available,
        floor=1,
    )
    db_session.add(bed)
    await db_session.flush()
    return bed


@pytest_asyncio.fixture
async def second_bed(db_session: AsyncSession, sample_ward) -> Bed:
    from app.models.ipd import BedStatus, BedType
    bed = Bed(
        id=uuid.uuid4(),
        ward_id=sample_ward.id,
        bed_number="A-102",
        bed_type=BedType.General,
        status=BedStatus.Available,
        floor=1,
    )
    db_session.add(bed)
    await db_session.flush()
    return bed


@pytest_asyncio.fixture
async def sample_inventory_item(db_session: AsyncSession) -> Item:
    item = Item(
        id=uuid.uuid4(),
        name="Paracetamol 500mg",
        generic_name="Acetaminophen",
        category="Medication",
        unit="tablet",
        reorder_level=50,
        current_stock=200,
        unit_cost=1.5,
        selling_price=3.0,
        is_controlled_substance=False,
    )
    db_session.add(item)
    await db_session.flush()
    return item


@pytest_asyncio.fixture
async def controlled_substance_item(db_session: AsyncSession) -> Item:
    item = Item(
        id=uuid.uuid4(),
        name="Morphine 10mg",
        generic_name="Morphine Sulfate",
        category="Medication",
        unit="ampoule",
        reorder_level=10,
        current_stock=50,
        unit_cost=25.0,
        selling_price=50.0,
        is_controlled_substance=True,
        schedule_class="II",
    )
    db_session.add(item)
    await db_session.flush()
    return item


@pytest_asyncio.fixture
async def low_stock_item(db_session: AsyncSession) -> Item:
    item = Item(
        id=uuid.uuid4(),
        name="Amoxicillin 250mg",
        generic_name="Amoxicillin",
        category="Medication",
        unit="capsule",
        reorder_level=50,
        current_stock=10,
        unit_cost=2.0,
        selling_price=5.0,
    )
    db_session.add(item)
    await db_session.flush()
    return item


@pytest_asyncio.fixture
async def expiring_batch(db_session: AsyncSession, sample_inventory_item) -> ItemBatch:
    batch = ItemBatch(
        id=uuid.uuid4(),
        item_id=sample_inventory_item.id,
        batch_number="BATCH-001",
        manufacturing_date=date.today() - timedelta(days=300),
        expiry_date=date.today() + timedelta(days=10),
        quantity_received=100,
        quantity_remaining=80,
    )
    db_session.add(batch)
    await db_session.flush()
    return batch


@pytest_asyncio.fixture
async def sample_lab_test(db_session: AsyncSession) -> LabTest:
    test = LabTest(
        id=uuid.uuid4(),
        name="Complete Blood Count",
        code="CBC",
        category="Hematology",
        sample_type="Blood",
        normal_range={"wbc": {"min": 4.5, "max": 11.0, "unit": "10^3/uL"}},
        unit="10^3/uL",
        price=350.0,
        turnaround_hours=4,
    )
    db_session.add(test)
    await db_session.flush()
    return test
