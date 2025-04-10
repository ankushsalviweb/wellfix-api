import pytest
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List

from sqlalchemy.orm import Session

from wellfix_api.models.job import RepairJob, JobStatusUpdate
from wellfix_api.models.user import User, UserRole
from wellfix_api.models.address import Address
from wellfix_api.models.enums import JobStatus, RepairType, PaymentStatus
from wellfix_api.crud.crud_job import (
    get_job,
    list_jobs,
    list_jobs_by_customer,
    list_jobs_by_engineer,
    create_job,
    assign_engineer,
    update_job_status,
    add_job_notes,
    update_job_quote,
    update_payment_status,
    cancel_job
)


@pytest.fixture
def test_users(db_session: Session) -> Dict[str, User]:
    """Create test users with different roles."""
    users = {}
    
    # Create a customer
    customer = User(
        id=str(uuid.uuid4()),
        email="customer@example.com",
        password_hash="hashed_password",
        first_name="Test",
        last_name="Customer",
        phone_number="1234567890",
        role=UserRole.CUSTOMER,
        is_active=True
    )
    db_session.add(customer)
    
    # Create an engineer
    engineer = User(
        id=str(uuid.uuid4()),
        email="engineer@example.com",
        password_hash="hashed_password",
        first_name="Test",
        last_name="Engineer",
        phone_number="2345678901",
        role=UserRole.ENGINEER,
        is_active=True
    )
    db_session.add(engineer)
    
    # Create an admin
    admin = User(
        id=str(uuid.uuid4()),
        email="admin@example.com",
        password_hash="hashed_password",
        first_name="Test",
        last_name="Admin",
        phone_number="3456789012",
        role=UserRole.ADMIN,
        is_active=True
    )
    db_session.add(admin)
    
    db_session.commit()
    
    # Refresh to get the database-assigned IDs
    db_session.refresh(customer)
    db_session.refresh(engineer)
    db_session.refresh(admin)
    
    users["customer"] = customer
    users["engineer"] = engineer
    users["admin"] = admin
    
    return users


@pytest.fixture
def test_address(db_session: Session, test_users: Dict[str, User]) -> Address:
    """Create a test address."""
    address = Address(
        id=str(uuid.uuid4()),
        user_id=test_users["customer"].id,
        street_address="123 Test St",
        city="Test City",
        state="Test State",
        pincode="12345",
        is_default=True
    )
    db_session.add(address)
    db_session.commit()
    db_session.refresh(address)
    return address


@pytest.fixture
def test_job(db_session: Session, test_users: Dict[str, User], test_address: Address) -> RepairJob:
    """Create a test job."""
    job = RepairJob(
        customer_id=test_users["customer"].id,
        address_id=test_address.id,
        laptop_manufacturer="Test Manufacturer",
        laptop_model="Test Model",
        laptop_serial_number="123456789",
        reported_symptoms="Test symptoms",
        repair_type_requested=RepairType.HARDWARE,
        status=JobStatus.PENDING_ASSIGNMENT,
        payment_status=PaymentStatus.PENDING
    )
    db_session.add(job)
    db_session.commit()
    db_session.refresh(job)
    return job


@pytest.fixture
def test_multiple_jobs(db_session: Session, test_users: Dict[str, User], test_address: Address) -> List[RepairJob]:
    """Create multiple test jobs."""
    jobs = []
    
    # Create 3 jobs for the customer
    for i in range(3):
        job = RepairJob(
            customer_id=test_users["customer"].id,
            address_id=test_address.id,
            laptop_manufacturer=f"Manufacturer {i}",
            laptop_model=f"Model {i}",
            laptop_serial_number=f"SN-{i}",
            reported_symptoms=f"Symptoms {i}",
            repair_type_requested=RepairType.HARDWARE,
            status=JobStatus.PENDING_ASSIGNMENT,
            payment_status=PaymentStatus.PENDING
        )
        db_session.add(job)
        jobs.append(job)
    
    # Create a job assigned to the engineer
    job_with_engineer = RepairJob(
        customer_id=test_users["customer"].id,
        engineer_id=test_users["engineer"].id,
        address_id=test_address.id,
        laptop_manufacturer="Engineer Job",
        laptop_model="Model E",
        laptop_serial_number="SN-E",
        reported_symptoms="Engineer test symptoms",
        repair_type_requested=RepairType.SOFTWARE,
        status=JobStatus.ASSIGNED,
        payment_status=PaymentStatus.PENDING
    )
    db_session.add(job_with_engineer)
    jobs.append(job_with_engineer)
    
    db_session.commit()
    
    # Refresh all jobs to get the database-assigned IDs
    for job in jobs:
        db_session.refresh(job)
    
    return jobs


def test_get_job(db_session: Session, test_job: RepairJob):
    """Test getting a job by ID."""
    # Get the existing job
    job = get_job(db_session, test_job.id)
    
    # Verify that the job was found and has the correct attributes
    assert job is not None
    assert job.id == test_job.id
    assert job.customer_id == test_job.customer_id
    assert job.laptop_manufacturer == test_job.laptop_manufacturer
    
    # Try to get a job with a non-existent ID
    non_existent_job = get_job(db_session, 9999)
    assert non_existent_job is None


def test_list_jobs(db_session: Session, test_multiple_jobs: List[RepairJob], test_users: Dict[str, User]):
    """Test listing jobs with various filters."""
    # Test listing all jobs
    jobs, total = list_jobs(db_session)
    assert total == len(test_multiple_jobs)
    assert len(jobs) == len(test_multiple_jobs)
    
    # Test pagination
    jobs_page1, total = list_jobs(db_session, skip=0, limit=2)
    assert total == len(test_multiple_jobs)
    assert len(jobs_page1) == 2
    
    jobs_page2, total = list_jobs(db_session, skip=2, limit=2)
    assert total == len(test_multiple_jobs)
    assert len(jobs_page2) == 2
    
    # Test filtering by status
    filter_params = {"status": JobStatus.ASSIGNED}
    filtered_jobs, total = list_jobs(db_session, filter_params=filter_params)
    assert total == 1
    assert filtered_jobs[0].status == JobStatus.ASSIGNED
    
    # Test filtering by customer
    filter_params = {"customer_id": test_users["customer"].id}
    filtered_jobs, total = list_jobs(db_session, filter_params=filter_params)
    assert total == len(test_multiple_jobs)
    
    # Test filtering by engineer
    filter_params = {"engineer_id": test_users["engineer"].id}
    filtered_jobs, total = list_jobs(db_session, filter_params=filter_params)
    assert total == 1
    assert filtered_jobs[0].engineer_id == test_users["engineer"].id


def test_list_jobs_by_customer(db_session: Session, test_multiple_jobs: List[RepairJob], test_users: Dict[str, User]):
    """Test listing jobs for a specific customer."""
    # Get all jobs for the customer
    jobs, total = list_jobs_by_customer(db_session, test_users["customer"].id)
    assert total == len(test_multiple_jobs)
    assert len(jobs) == len(test_multiple_jobs)
    
    # Filter by status
    jobs, total = list_jobs_by_customer(db_session, test_users["customer"].id, status=JobStatus.ASSIGNED)
    assert total == 1
    assert jobs[0].status == JobStatus.ASSIGNED
    
    # Test pagination
    jobs, total = list_jobs_by_customer(db_session, test_users["customer"].id, skip=2, limit=2)
    assert total == len(test_multiple_jobs)
    assert len(jobs) == 2


def test_list_jobs_by_engineer(db_session: Session, test_multiple_jobs: List[RepairJob], test_users: Dict[str, User]):
    """Test listing jobs assigned to a specific engineer."""
    # Get all jobs for the engineer
    jobs, total = list_jobs_by_engineer(db_session, test_users["engineer"].id)
    assert total == 1
    assert jobs[0].engineer_id == test_users["engineer"].id
    
    # Filter by status
    jobs, total = list_jobs_by_engineer(db_session, test_users["engineer"].id, status=JobStatus.ASSIGNED)
    assert total == 1
    
    # Filter by non-matching status
    jobs, total = list_jobs_by_engineer(db_session, test_users["engineer"].id, status=JobStatus.PENDING_ASSIGNMENT)
    assert total == 0
    
    # Test with an engineer that has no jobs
    jobs, total = list_jobs_by_engineer(db_session, str(uuid.uuid4()))
    assert total == 0
    assert len(jobs) == 0


def test_create_job(db_session: Session, test_users: Dict[str, User], test_address: Address):
    """Test creating a new job."""
    # Prepare job data
    job_data = {
        "address_id": test_address.id,
        "laptop_manufacturer": "New Manufacturer",
        "laptop_model": "New Model",
        "laptop_serial_number": "New-SN-123",
        "reported_symptoms": "New symptoms for testing",
        "repair_type_requested": RepairType.HARDWARE
    }
    
    # Create the job
    job = create_job(db_session, job_data, test_users["customer"].id)
    
    # Verify the job was created with the correct attributes
    assert job is not None
    assert job.id is not None
    assert job.customer_id == test_users["customer"].id
    assert job.address_id == test_address.id
    assert job.laptop_manufacturer == job_data["laptop_manufacturer"]
    assert job.laptop_model == job_data["laptop_model"]
    assert job.laptop_serial_number == job_data["laptop_serial_number"]
    assert job.reported_symptoms == job_data["reported_symptoms"]
    assert job.repair_type_requested == job_data["repair_type_requested"]
    assert job.status == JobStatus.PENDING_ASSIGNMENT
    assert job.payment_status == PaymentStatus.PENDING
    
    # Verify that a status update was created
    status_update = db_session.query(JobStatusUpdate).filter(JobStatusUpdate.job_id == job.id).first()
    assert status_update is not None
    assert status_update.new_status == JobStatus.PENDING_ASSIGNMENT
    assert status_update.user_id == test_users["customer"].id


def test_assign_engineer(db_session: Session, test_job: RepairJob, test_users: Dict[str, User]):
    """Test assigning an engineer to a job."""
    # Assign the engineer
    updated_job = assign_engineer(
        db_session, 
        test_job.id, 
        test_users["engineer"].id, 
        test_users["admin"].id
    )
    
    # Verify the assignment
    assert updated_job is not None
    assert updated_job.engineer_id == test_users["engineer"].id
    assert updated_job.status == JobStatus.ASSIGNED
    
    # Verify that a status update was created
    status_update = db_session.query(JobStatusUpdate).filter(
        JobStatusUpdate.job_id == test_job.id, 
        JobStatusUpdate.new_status == JobStatus.ASSIGNED
    ).first()
    assert status_update is not None
    assert status_update.user_id == test_users["admin"].id
    
    # Unassign the engineer
    updated_job = assign_engineer(
        db_session, 
        test_job.id, 
        None,  # Unassign
        test_users["admin"].id
    )
    
    # Verify the unassignment
    assert updated_job is not None
    assert updated_job.engineer_id is None
    assert updated_job.status == JobStatus.PENDING_ASSIGNMENT


def test_update_job_status(db_session: Session, test_job: RepairJob, test_users: Dict[str, User]):
    """Test updating a job's status."""
    # Update the status
    new_status = JobStatus.ASSIGNED
    notes = "Status update test notes"
    
    updated_job = update_job_status(
        db_session,
        test_job.id,
        new_status,
        test_users["admin"].id,
        notes=notes
    )
    
    # Verify the update
    assert updated_job is not None
    assert updated_job.status == new_status
    
    # Verify that a status update was created
    status_update = db_session.query(JobStatusUpdate).filter(
        JobStatusUpdate.job_id == test_job.id,
        JobStatusUpdate.new_status == new_status
    ).first()
    assert status_update is not None
    assert status_update.notes == notes
    assert status_update.user_id == test_users["admin"].id
    assert status_update.previous_status == JobStatus.PENDING_ASSIGNMENT


def test_add_job_notes(db_session: Session, test_job: RepairJob, test_users: Dict[str, User]):
    """Test adding notes to a job."""
    # Add engineer notes
    engineer_notes = "Engineer test notes"
    updated_job = add_job_notes(
        db_session,
        test_job.id,
        test_users["engineer"].id,
        engineer_notes
    )
    
    # Verify the engineer notes were added
    assert updated_job is not None
    assert engineer_notes in updated_job.engineer_notes
    assert "[" in updated_job.engineer_notes  # Check for timestamp format
    
    # Add admin notes
    admin_notes = "Admin test notes"
    updated_job = add_job_notes(
        db_session,
        test_job.id,
        test_users["admin"].id,
        admin_notes
    )
    
    # Verify the admin notes were added
    assert updated_job is not None
    assert admin_notes in updated_job.admin_notes
    
    # Add more engineer notes (should append)
    more_engineer_notes = "More engineer notes"
    updated_job = add_job_notes(
        db_session,
        test_job.id,
        test_users["engineer"].id,
        more_engineer_notes
    )
    
    # Verify the new engineer notes were appended
    assert updated_job is not None
    assert engineer_notes in updated_job.engineer_notes
    assert more_engineer_notes in updated_job.engineer_notes


def test_update_job_quote(db_session: Session, test_job: RepairJob, test_users: Dict[str, User]):
    """Test updating a job's cost quote."""
    # Update with estimated cost only
    estimated_cost = 100.50
    updated_job = update_job_quote(
        db_session,
        test_job.id,
        test_users["engineer"].id,
        estimated_cost=estimated_cost
    )
    
    # Verify the estimated cost was updated
    assert updated_job is not None
    assert updated_job.estimated_cost == estimated_cost
    assert updated_job.final_cost is None
    
    # Update with final cost only
    final_cost = 125.75
    updated_job = update_job_quote(
        db_session,
        test_job.id,
        test_users["admin"].id,
        final_cost=final_cost
    )
    
    # Verify the final cost was updated
    assert updated_job is not None
    assert updated_job.estimated_cost == estimated_cost  # Unchanged
    assert updated_job.final_cost == final_cost


def test_update_payment_status(db_session: Session, test_job: RepairJob, test_users: Dict[str, User]):
    """Test updating a job's payment status."""
    # Update payment status
    payment_status = PaymentStatus.COMPLETED
    notes = "Payment received"
    
    updated_job = update_payment_status(
        db_session,
        test_job.id,
        payment_status,
        test_users["admin"].id,
        notes=notes
    )
    
    # Verify the payment status was updated
    assert updated_job is not None
    assert updated_job.payment_status == payment_status
    
    # Verify that a status update note was created if the job status changed
    if updated_job.status != test_job.status:
        status_update = db_session.query(JobStatusUpdate).filter(
            JobStatusUpdate.job_id == test_job.id,
            JobStatusUpdate.new_status == updated_job.status
        ).first()
        assert status_update is not None
        assert notes in status_update.notes


def test_cancel_job(db_session: Session, test_job: RepairJob, test_users: Dict[str, User]):
    """Test cancelling a job."""
    # Cancel the job
    reason = "Testing job cancellation"
    
    updated_job = cancel_job(
        db_session,
        test_job.id,
        test_users["customer"].id,
        reason
    )
    
    # Verify the job was cancelled
    assert updated_job is not None
    assert updated_job.status == JobStatus.CANCELLED
    assert updated_job.cancellation_reason == reason
    
    # Verify that a status update was created
    status_update = db_session.query(JobStatusUpdate).filter(
        JobStatusUpdate.job_id == test_job.id,
        JobStatusUpdate.new_status == JobStatus.CANCELLED
    ).first()
    assert status_update is not None
    assert status_update.user_id == test_users["customer"].id
    assert reason in status_update.notes 