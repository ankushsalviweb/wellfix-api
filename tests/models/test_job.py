import uuid
import pytest
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from wellfix_api.models.job import RepairJob, JobStatusUpdate, Rating
from wellfix_api.models.user import User, UserRole
from wellfix_api.models.address import Address
from wellfix_api.models.enums import JobStatus, RepairType, PaymentStatus
from wellfix_api.core.db import Base


@pytest.fixture
def db_session():
    """Create a test in-memory database session."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def test_customer(db_session):
    """Create a test customer user."""
    user = User(
        id=str(uuid.uuid4()),
        email="customer@example.com",
        password_hash="hashed_password",
        first_name="Test",
        last_name="Customer",
        phone_number="1234567890",
        role=UserRole.CUSTOMER,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def test_engineer(db_session):
    """Create a test engineer user."""
    user = User(
        id=str(uuid.uuid4()),
        email="engineer@example.com",
        password_hash="hashed_password",
        first_name="Test",
        last_name="Engineer",
        phone_number="2345678901",
        role=UserRole.ENGINEER,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def test_address(db_session, test_customer):
    """Create a test address."""
    address = Address(
        id=str(uuid.uuid4()),
        user_id=test_customer.id,
        street_address="123 Test St",
        city="Test City",
        state="Test State",
        pincode="12345",
        is_default=True
    )
    db_session.add(address)
    db_session.commit()
    return address


def test_create_repair_job(db_session, test_customer, test_address):
    """Test creating a RepairJob model."""
    # Create a new repair job
    job = RepairJob(
        customer_id=test_customer.id,
        address_id=test_address.id,
        laptop_manufacturer="Test Manufacturer",
        laptop_model="Test Model",
        laptop_serial_number="123456789",
        reported_symptoms="Test symptoms description",
        repair_type_requested=RepairType.HARDWARE,
        status=JobStatus.PENDING_ASSIGNMENT,
        payment_status=PaymentStatus.PENDING
    )
    
    db_session.add(job)
    db_session.commit()
    
    # Query the job from the database
    retrieved_job = db_session.query(RepairJob).filter_by(id=job.id).first()
    
    # Check that the job was retrieved
    assert retrieved_job is not None
    assert retrieved_job.customer_id == test_customer.id
    assert retrieved_job.address_id == test_address.id
    assert retrieved_job.laptop_manufacturer == "Test Manufacturer"
    assert retrieved_job.laptop_model == "Test Model"
    assert retrieved_job.status == JobStatus.PENDING_ASSIGNMENT
    assert retrieved_job.payment_status == PaymentStatus.PENDING


def test_repair_job_relationships(db_session, test_customer, test_engineer, test_address):
    """Test the relationships between RepairJob and related models."""
    # Create a repair job with an engineer assigned
    job = RepairJob(
        customer_id=test_customer.id,
        engineer_id=test_engineer.id,
        address_id=test_address.id,
        laptop_manufacturer="Relationship Test",
        laptop_model="Model R",
        reported_symptoms="Testing relationships",
        repair_type_requested=RepairType.SOFTWARE,
        status=JobStatus.ASSIGNED,
        payment_status=PaymentStatus.PENDING
    )
    
    db_session.add(job)
    db_session.commit()
    
    # Add a status update for the job
    status_update = JobStatusUpdate(
        job_id=job.id,
        user_id=test_engineer.id,
        previous_status=JobStatus.PENDING_ASSIGNMENT,
        new_status=JobStatus.ASSIGNED,
        notes="Test status update"
    )
    db_session.add(status_update)
    db_session.commit()
    
    # Refresh the job to load the relationships
    db_session.refresh(job)
    db_session.refresh(test_customer)
    db_session.refresh(test_engineer)
    
    # Test customer relationship
    assert job.customer.id == test_customer.id
    assert job.customer.email == test_customer.email
    
    # Test engineer relationship
    assert job.engineer.id == test_engineer.id
    assert job.engineer.email == test_engineer.email
    
    # Test address relationship
    assert job.address.id == test_address.id
    assert job.address.street_address == test_address.street_address
    
    # Test status_updates relationship
    assert len(job.status_updates) == 1
    assert job.status_updates[0].previous_status == JobStatus.PENDING_ASSIGNMENT
    assert job.status_updates[0].new_status == JobStatus.ASSIGNED
    
    # Test reverse relationships - jobs linked to users
    customer_jobs = db_session.query(RepairJob).filter_by(customer_id=test_customer.id).all()
    assert job.id in [j.id for j in customer_jobs]
    
    engineer_jobs = db_session.query(RepairJob).filter_by(engineer_id=test_engineer.id).all()
    assert job.id in [j.id for j in engineer_jobs]


def test_job_status_update(db_session, test_customer, test_engineer, test_address):
    """Test creating and updating job status."""
    # Create a repair job
    job = RepairJob(
        customer_id=test_customer.id,
        address_id=test_address.id,
        laptop_manufacturer="Status Test",
        laptop_model="Model S",
        reported_symptoms="Testing status updates",
        repair_type_requested=RepairType.HARDWARE,
        status=JobStatus.PENDING_ASSIGNMENT,
        payment_status=PaymentStatus.PENDING
    )
    
    db_session.add(job)
    db_session.commit()
    
    # Create an initial status update
    status_update1 = JobStatusUpdate(
        job_id=job.id,
        user_id=test_customer.id,
        previous_status=None,
        new_status=JobStatus.PENDING_ASSIGNMENT,
        notes="Job created"
    )
    db_session.add(status_update1)
    
    # Assign the job to an engineer with a status update
    job.status = JobStatus.ASSIGNED
    job.engineer_id = test_engineer.id
    
    status_update2 = JobStatusUpdate(
        job_id=job.id,
        user_id=test_engineer.id,
        previous_status=JobStatus.PENDING_ASSIGNMENT,
        new_status=JobStatus.ASSIGNED,
        notes="Job assigned to engineer"
    )
    db_session.add(status_update2)
    db_session.commit()
    
    # Move to on-site diagnosis
    job.status = JobStatus.ON_SITE_DIAGNOSIS
    status_update3 = JobStatusUpdate(
        job_id=job.id,
        user_id=test_engineer.id,
        previous_status=JobStatus.ASSIGNED,
        new_status=JobStatus.ON_SITE_DIAGNOSIS,
        notes="Engineer arrived on site"
    )
    db_session.add(status_update3)
    db_session.commit()
    
    # Query the status updates for the job
    status_updates = db_session.query(JobStatusUpdate).filter_by(job_id=job.id).order_by(JobStatusUpdate.id).all()
    
    # Check that the status updates were saved correctly
    assert len(status_updates) == 3
    assert status_updates[0].new_status == JobStatus.PENDING_ASSIGNMENT
    assert status_updates[1].new_status == JobStatus.ASSIGNED
    assert status_updates[2].new_status == JobStatus.ON_SITE_DIAGNOSIS
    
    # Check chronological sequence
    assert status_updates[0].previous_status is None
    assert status_updates[1].previous_status == JobStatus.PENDING_ASSIGNMENT
    assert status_updates[2].previous_status == JobStatus.ASSIGNED
    
    # Check the final status of the job
    assert job.status == JobStatus.ON_SITE_DIAGNOSIS 