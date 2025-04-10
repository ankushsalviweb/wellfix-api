"""
Integration tests for job endpoints.
"""

import pytest
import logging
import uuid
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from wellfix_api.main import app
from wellfix_api.core.config import settings
from wellfix_api.models.user import User, UserRole
from wellfix_api.models.enums import JobStatus, PaymentStatus, RepairType
from wellfix_api.core.dependencies import get_db, get_current_user
from wellfix_api.models.job import Job, RepairJob, JobStatusUpdate
from tests.utils.test_db import override_get_db, TestingSessionLocal
from wellfix_api.models.address import Address


# Set up logging for tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@pytest.fixture
def test_client():
    """
    Create a test client with overridden database dependency.
    """
    # Override the DB dependency
    app.dependency_overrides[get_db] = override_get_db
    
    # Return test client
    client = TestClient(app)
    yield client
    
    # Clean up
    app.dependency_overrides.clear()


@pytest.fixture
def db():
    """
    Create a database session for test use.
    """
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def customer_user(db: Session):
    """
    Create a customer user for testing.
    """
    random_suffix = uuid.uuid4().hex[:8]
    user = User(
        email=f"customer_{random_suffix}@example.com",
        password_hash="$2b$12$DlK0cFN5FuJvxN08lJrJfeHk3Gt0zZ9l2Z3pBFU9EcYG9OCb1qiim",  # "password"
        first_name="Test",
        last_name="Customer",
        phone_number="1234567890",
        role=UserRole.CUSTOMER,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def engineer_user(db: Session):
    """
    Create an engineer user for testing.
    """
    random_suffix = uuid.uuid4().hex[:8]
    user = User(
        email=f"engineer_{random_suffix}@example.com",
        password_hash="$2b$12$DlK0cFN5FuJvxN08lJrJfeHk3Gt0zZ9l2Z3pBFU9EcYG9OCb1qiim",  # "password"
        first_name="Test",
        last_name="Engineer",
        phone_number="0987654321",
        role=UserRole.ENGINEER,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def admin_user(db: Session):
    """
    Create an admin user for testing.
    """
    random_suffix = uuid.uuid4().hex[:8]
    user = User(
        email=f"admin_{random_suffix}@example.com",
        password_hash="$2b$12$DlK0cFN5FuJvxN08lJrJfeHk3Gt0zZ9l2Z3pBFU9EcYG9OCb1qiim",  # "password"
        first_name="Test",
        last_name="Admin",
        phone_number="5555555555",
        role=UserRole.ADMIN,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_address(db: Session, customer_user: User):
    """
    Create a test address for testing.
    """
    address = Address(
        user_id=customer_user.id,
        street_address="123 Test St",
        city="Test City",
        state="Test State",
        pincode="12345",
        is_default=True
    )
    db.add(address)
    db.commit()
    db.refresh(address)
    return address


@pytest.fixture
def test_job(db: Session, customer_user: User, test_address):
    """
    Create a test job for testing.
    """
    job = RepairJob(
        customer_id=customer_user.id,
        address_id=test_address.id,
        laptop_manufacturer="Test Manufacturer",
        laptop_model="Test Model",
        laptop_serial_number="12345ABC",
        reported_symptoms="Test symptoms",
        repair_type_requested=RepairType.HARDWARE,
        status=JobStatus.PENDING_ASSIGNMENT,
        payment_status=PaymentStatus.PENDING,
        customer_consent_for_lab=False,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


@pytest.fixture
def assigned_test_job(db: Session, customer_user: User, engineer_user: User, test_address):
    """
    Create a test job that is already assigned to an engineer.
    """
    job = RepairJob(
        customer_id=customer_user.id,
        engineer_id=engineer_user.id,
        address_id=test_address.id,
        laptop_manufacturer="Assigned Manufacturer",
        laptop_model="Assigned Model",
        laptop_serial_number="ASSIGNED123",
        reported_symptoms="Assigned job symptoms",
        repair_type_requested=RepairType.SOFTWARE,
        status=JobStatus.ASSIGNED,
        payment_status=PaymentStatus.PENDING,
        customer_consent_for_lab=False,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def override_get_current_user_customer(user: User):
    """
    Override the get_current_user dependency for customer users.
    """
    def get_current_user_override():
        return user
    return get_current_user_override


def override_get_current_user_engineer(user: User):
    """
    Override the get_current_user dependency for engineer users.
    """
    def get_current_user_override():
        return user
    return get_current_user_override


def override_get_current_user_admin(user: User):
    """
    Override the get_current_user dependency for admin users.
    """
    def get_current_user_override():
        return user
    return get_current_user_override


# ====================
# Customer Job Tests
# ====================

def test_create_job_as_customer(test_client: TestClient, customer_user: User, test_address: Address):
    """
    Test creating a job as a customer.
    """
    # Override the user dependency
    app.dependency_overrides[get_current_user] = override_get_current_user_customer(customer_user)
    
    # Prepare test data
    job_data = {
        "laptop_manufacturer": "Dell",
        "laptop_model": "XPS 15",
        "laptop_serial_number": "XPS123456789",
        "reported_symptoms": "Screen does not turn on",
        "repair_type_requested": "HARDWARE",
        "address_id": test_address.id  # Use the test address
    }
    
    # Make the request
    response = test_client.post("/api/v1/jobs", json=job_data)
    
    # Check response
    assert response.status_code == 201
    data = response.json()
    assert data["customer_id"] == customer_user.id
    assert data["status"] == JobStatus.PENDING_ASSIGNMENT
    assert data["laptop_manufacturer"] == job_data["laptop_manufacturer"]
    assert data["laptop_model"] == job_data["laptop_model"]
    assert "id" in data
    
    # Clean up
    app.dependency_overrides.clear()


def test_create_job_as_non_customer(test_client: TestClient, engineer_user: User):
    """
    Test that only customers can create jobs.
    """
    # Override the user dependency
    app.dependency_overrides[get_current_user] = override_get_current_user_engineer(engineer_user)
    
    # Prepare test data
    job_data = {
        "laptop_manufacturer": "Dell",
        "laptop_model": "XPS 15",
        "laptop_serial_number": "XPS123456789",
        "reported_symptoms": "Screen does not turn on",
        "repair_type_requested": "HARDWARE",
        "address_id": None  # No address for now
    }
    
    # Make the request - should fail
    response = test_client.post("/api/v1/jobs", json=job_data)
    
    # Check response
    assert response.status_code == 403
    assert "Only customers can create repair jobs" in response.json()["detail"]
    
    # Clean up
    app.dependency_overrides.clear()


def test_customer_can_see_only_own_jobs(
    test_client: TestClient, 
    customer_user: User, 
    test_job: Job, 
    db: Session
):
    """
    Test that customers can only see their own jobs.
    """
    # Create a job for a different customer
    other_customer = User(
        email="other_customer@example.com",
        password_hash="$2b$12$DlK0cFN5FuJvxN08lJrJfeHk3Gt0zZ9l2Z3pBFU9EcYG9OCb1qiim",  # "password"
        first_name="Other",
        last_name="Customer",
        phone_number="9999999999",
        role=UserRole.CUSTOMER,
    )
    db.add(other_customer)
    db.commit()
    db.refresh(other_customer)
    
    other_job = Job(
        customer_id=other_customer.id,
        laptop_manufacturer="Other Manufacturer",
        laptop_model="Other Model",
        laptop_serial_number="OTHER123",
        reported_symptoms="Other job symptoms",
        repair_type_requested="HARDWARE",
        status=JobStatus.PENDING_ASSIGNMENT,
        payment_status=PaymentStatus.PENDING,
    )
    db.add(other_job)
    db.commit()
    
    # Override the user dependency
    app.dependency_overrides[get_current_user] = override_get_current_user_customer(customer_user)
    
    # Make the request
    response = test_client.get("/api/v1/jobs")
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 1  # Only the customer's own job
    jobs = data["jobs"]
    assert len(jobs) == 1
    assert jobs[0]["id"] == test_job.id
    assert jobs[0]["customer_id"] == customer_user.id
    
    # Clean up
    app.dependency_overrides.clear()


def test_customer_job_detail_access(
    test_client: TestClient,
    customer_user: User,
    test_job: Job
):
    """
    Test that customers can access details of their own jobs but not others.
    """
    # Override the user dependency
    app.dependency_overrides[get_current_user] = override_get_current_user_customer(customer_user)
    
    # Make the request for their own job
    response = test_client.get(f"/api/v1/jobs/{test_job.id}")
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_job.id
    assert data["customer_id"] == customer_user.id
    
    # Try to access a non-existent job
    response = test_client.get("/api/v1/jobs/9999")
    assert response.status_code == 404
    
    # Clean up
    app.dependency_overrides.clear()


def test_customer_cancel_job(
    test_client: TestClient,
    customer_user: User,
    test_job: Job
):
    """
    Test that customers can cancel their own jobs.
    """
    # Override the user dependency
    app.dependency_overrides[get_current_user] = override_get_current_user_customer(customer_user)
    
    # Prepare cancellation data
    cancel_data = {
        "reason": "Changed my mind"
    }
    
    # Make the request
    response = test_client.post(f"/api/v1/jobs/{test_job.id}/cancel", json=cancel_data)
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == JobStatus.CANCELLED
    
    # Clean up
    app.dependency_overrides.clear()


# ====================
# Engineer Job Tests
# ====================

def test_engineer_job_list_access(
    test_client: TestClient,
    engineer_user: User,
    assigned_test_job: Job
):
    """
    Test that engineers can only see jobs assigned to them.
    """
    # Override the user dependency
    app.dependency_overrides[get_current_user] = override_get_current_user_engineer(engineer_user)
    
    # Make the request
    response = test_client.get("/api/v1/jobs")
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 1  # Only the assigned job
    jobs = data["jobs"]
    assert len(jobs) == 1
    assert jobs[0]["id"] == assigned_test_job.id
    assert jobs[0]["engineer_id"] == engineer_user.id
    
    # Clean up
    app.dependency_overrides.clear()


def test_engineer_job_detail_access(
    test_client: TestClient,
    engineer_user: User,
    assigned_test_job: Job,
    test_job: Job
):
    """
    Test that engineers can access details of jobs assigned to them but not others.
    """
    # Override the user dependency
    app.dependency_overrides[get_current_user] = override_get_current_user_engineer(engineer_user)
    
    # Make the request for an assigned job
    response = test_client.get(f"/api/v1/jobs/{assigned_test_job.id}")
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == assigned_test_job.id
    assert data["engineer_id"] == engineer_user.id
    
    # Try to access a job not assigned to the engineer
    response = test_client.get(f"/api/v1/jobs/{test_job.id}")
    assert response.status_code == 403
    
    # Clean up
    app.dependency_overrides.clear()


def test_engineer_update_job_status(
    test_client: TestClient,
    engineer_user: User,
    assigned_test_job: Job
):
    """
    Test that engineers can update the status of jobs assigned to them.
    """
    # Override the user dependency
    app.dependency_overrides[get_current_user] = override_get_current_user_engineer(engineer_user)
    
    # Prepare status update data - move from ASSIGNED to PENDING_VISIT
    status_data = {
        "status": JobStatus.PENDING_VISIT,
        "notes": "Scheduling a visit for diagnosis"
    }
    
    # Make the request
    response = test_client.patch(f"/api/v1/jobs/{assigned_test_job.id}/status", json=status_data)
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == JobStatus.PENDING_VISIT
    
    # Clean up
    app.dependency_overrides.clear()


def test_lab_escalation_with_consent(
    test_client: TestClient,
    engineer_user: User,
    db: Session
):
    """
    Test the lab escalation workflow with customer consent.
    """
    # Create a job in the ON_SITE_DIAGNOSIS status assigned to the test engineer
    job = RepairJob(
        customer_id=1,  # Assuming a customer exists
        engineer_id=engineer_user.id,
        address_id=1,  # Assuming an address exists
        laptop_manufacturer="Lab Test",
        laptop_model="Escalation Model",
        laptop_serial_number="LAB123",
        reported_symptoms="Needs lab diagnosis",
        repair_type_requested=RepairType.HARDWARE,
        status=JobStatus.ON_SITE_DIAGNOSIS,
        payment_status=PaymentStatus.PENDING,
        customer_consent_for_lab=False  # Initially no consent
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    
    # Override the user dependency
    app.dependency_overrides[get_current_user] = override_get_current_user_engineer(engineer_user)
    
    # Prepare status update data - move from ON_SITE_DIAGNOSIS to ESCALATED_TO_LAB with consent
    status_data = {
        "status": JobStatus.ESCALATED_TO_LAB,
        "notes": "Cannot repair on-site, needs lab diagnosis",
        "customer_consent_for_lab": True
    }
    
    # Make the request
    response = test_client.patch(f"/api/v1/jobs/{job.id}/status", json=status_data)
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == JobStatus.ESCALATED_TO_LAB
    assert data["customer_consent_for_lab"] is True  # Consent flag should be updated
    
    # Now try to move to in-transit status, which should work as we have consent
    status_data = {
        "status": JobStatus.PENDING_PICKUP_FOR_LAB,
        "notes": "Scheduling pickup for lab repair"
    }
    
    # Make the request
    response = test_client.patch(f"/api/v1/jobs/{job.id}/status", json=status_data)
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == JobStatus.PENDING_PICKUP_FOR_LAB
    
    # Now try to move to IN_TRANSIT_TO_LAB which should work as we have consent
    status_data = {
        "status": JobStatus.IN_TRANSIT_TO_LAB,
        "notes": "Device picked up, on the way to lab"
    }
    
    # Make the request
    response = test_client.patch(f"/api/v1/jobs/{job.id}/status", json=status_data)
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == JobStatus.IN_TRANSIT_TO_LAB
    
    # Clean up
    app.dependency_overrides.clear()


def test_lab_transit_without_consent_rejected(
    test_client: TestClient,
    engineer_user: User,
    db: Session
):
    """
    Test that transitioning to IN_TRANSIT_TO_LAB without consent is rejected.
    """
    # Create a job in the PENDING_PICKUP_FOR_LAB status but WITHOUT customer consent
    job = RepairJob(
        customer_id=1,  # Assuming a customer exists
        engineer_id=engineer_user.id,
        address_id=1,  # Assuming an address exists
        laptop_manufacturer="No Consent",
        laptop_model="Rejection Model",
        laptop_serial_number="NOC123",
        reported_symptoms="Needs lab but no consent",
        repair_type_requested=RepairType.HARDWARE,
        status=JobStatus.PENDING_PICKUP_FOR_LAB,
        payment_status=PaymentStatus.PENDING,
        customer_consent_for_lab=False  # No consent given
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    
    # Override the user dependency
    app.dependency_overrides[get_current_user] = override_get_current_user_engineer(engineer_user)
    
    # Try to move to IN_TRANSIT_TO_LAB without consent, should be rejected
    status_data = {
        "status": JobStatus.IN_TRANSIT_TO_LAB,
        "notes": "Attempting transit without consent"
    }
    
    # Make the request
    response = test_client.patch(f"/api/v1/jobs/{job.id}/status", json=status_data)
    
    # Check response - should be rejected with 422
    assert response.status_code == 422
    assert "consent required" in response.json()["detail"].lower()
    
    # Clean up
    app.dependency_overrides.clear()


def test_engineer_invalid_status_update(
    test_client: TestClient,
    engineer_user: User,
    assigned_test_job: Job
):
    """
    Test validation for invalid status transitions by engineers.
    """
    # Override the user dependency
    app.dependency_overrides[get_current_user] = override_get_current_user_engineer(engineer_user)
    
    # Try an invalid transition (ASSIGNED -> COMPLETED) which should be rejected
    status_data = {
        "status": JobStatus.COMPLETED,
        "notes": "Trying to complete without going through proper steps"
    }
    
    # Make the request
    response = test_client.patch(f"/api/v1/jobs/{assigned_test_job.id}/status", json=status_data)
    
    # Check response - should reject invalid transition
    assert response.status_code == 422
    assert "Invalid status transition" in response.json()["detail"]
    
    # Clean up
    app.dependency_overrides.clear()


def test_engineer_add_job_notes(
    test_client: TestClient,
    engineer_user: User,
    assigned_test_job: Job
):
    """
    Test that engineers can add notes to jobs assigned to them.
    """
    # Override the user dependency
    app.dependency_overrides[get_current_user] = override_get_current_user_engineer(engineer_user)
    
    # Prepare notes data
    notes_data = {
        "notes": "Preliminary assessment: Laptop appears to have software issues."
    }
    
    # Make the request
    response = test_client.post(f"/api/v1/jobs/{assigned_test_job.id}/notes", json=notes_data)
    
    # Check response
    assert response.status_code == 200
    
    # Verify notes added to engineer_notes by checking job details
    response = test_client.get(f"/api/v1/jobs/{assigned_test_job.id}")
    data = response.json()
    
    # Notes should be in engineer_notes field
    assert "engineer_notes" in data
    assert data["engineer_notes"] is not None
    assert notes_data["notes"] in data["engineer_notes"]
    
    # Clean up
    app.dependency_overrides.clear()


# ====================
# Admin Job Tests
# ====================

def test_admin_job_list_access(
    test_client: TestClient,
    admin_user: User,
    test_job: Job,
    assigned_test_job: Job
):
    """
    Test that admins can see all jobs.
    """
    # Override the user dependency
    app.dependency_overrides[get_current_user] = override_get_current_user_admin(admin_user)
    
    # Make the request
    response = test_client.get("/api/v1/jobs")
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert data["count"] >= 2  # Should see at least our test jobs
    jobs = data["jobs"]
    assert len(jobs) >= 2
    
    # Verify our test jobs are in the response
    job_ids = [job["id"] for job in jobs]
    assert test_job.id in job_ids
    assert assigned_test_job.id in job_ids
    
    # Clean up
    app.dependency_overrides.clear()


def test_admin_job_detail_access(
    test_client: TestClient,
    admin_user: User,
    test_job: Job
):
    """
    Test that admins can access details of any job.
    """
    # Override the user dependency
    app.dependency_overrides[get_current_user] = override_get_current_user_admin(admin_user)
    
    # Make the request
    response = test_client.get(f"/api/v1/jobs/{test_job.id}")
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_job.id
    
    # Clean up
    app.dependency_overrides.clear()


def test_admin_assign_engineer(
    test_client: TestClient,
    admin_user: User,
    test_job: Job,
    engineer_user: User
):
    """
    Test that admins can assign engineers to jobs.
    """
    # Override the user dependency
    app.dependency_overrides[get_current_user] = override_get_current_user_admin(admin_user)
    
    # Prepare assignment data
    assignment_data = {
        "engineer_id": engineer_user.id
    }
    
    # Make the request
    response = test_client.patch(f"/api/v1/jobs/{test_job.id}/assign", json=assignment_data)
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert data["engineer_id"] == engineer_user.id
    assert data["status"] == JobStatus.ASSIGNED  # Status should update to ASSIGNED
    
    # Clean up
    app.dependency_overrides.clear()


def test_admin_update_job_status(
    test_client: TestClient,
    admin_user: User,
    test_job: Job
):
    """
    Test that admins can update the status of any job.
    """
    # Override the user dependency
    app.dependency_overrides[get_current_user] = override_get_current_user_admin(admin_user)
    
    # Prepare status update data
    status_data = {
        "status": JobStatus.CANCELLED,
        "notes": "Cancelling unassigned job"
    }
    
    # Make the request
    response = test_client.patch(f"/api/v1/jobs/{test_job.id}/status", json=status_data)
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == JobStatus.CANCELLED
    
    # Clean up
    app.dependency_overrides.clear()


def test_admin_add_job_notes(
    test_client: TestClient,
    admin_user: User,
    test_job: Job
):
    """
    Test that admins can add notes to any job.
    """
    # Override the user dependency
    app.dependency_overrides[get_current_user] = override_get_current_user_admin(admin_user)
    
    # Prepare notes data
    notes_data = {
        "notes": "Admin note: Customer requested priority handling"
    }
    
    # Make the request
    response = test_client.post(f"/api/v1/jobs/{test_job.id}/notes", json=notes_data)
    
    # Check response
    assert response.status_code == 200
    
    # Verify notes added to admin_notes by checking job details
    response = test_client.get(f"/api/v1/jobs/{test_job.id}")
    data = response.json()
    
    # Notes should be in admin_notes field
    assert "admin_notes" in data
    assert data["admin_notes"] is not None
    assert notes_data["notes"] in data["admin_notes"]
    
    # Clean up
    app.dependency_overrides.clear()


def test_admin_update_payment_status(
    test_client: TestClient,
    admin_user: User,
    db: Session,
    test_address: Address
):
    """
    Test that admins can update payment status.
    """
    # Create a job with PENDING_PAYMENT status
    job = RepairJob(
        customer_id=1,  # Assuming a customer exists
        address_id=test_address.id,
        laptop_manufacturer="Payment Test",
        laptop_model="Payment Model",
        laptop_serial_number="PAYMENT123",
        reported_symptoms="Testing payment status updates",
        repair_type_requested=RepairType.HARDWARE,
        status=JobStatus.PENDING_PAYMENT,
        payment_status=PaymentStatus.PENDING,
        final_cost=150.00,
        customer_consent_for_lab=False
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    
    # Override the user dependency
    app.dependency_overrides[get_current_user] = override_get_current_user_admin(admin_user)
    
    # Prepare payment status update data
    payment_data = {
        "payment_status": PaymentStatus.COMPLETED,
        "notes": "Payment received via credit card"
    }
    
    # Make the request
    response = test_client.patch(f"/api/v1/jobs/{job.id}/payment", json=payment_data)
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert data["payment_status"] == PaymentStatus.COMPLETED
    
    # Clean up
    app.dependency_overrides.clear()


def test_engineer_update_job_quote(
    test_client: TestClient,
    engineer_user: User,
    db: Session
):
    """
    Test that engineers can update quotes for jobs assigned to them.
    """
    # Create a job in LAB_DIAGNOSIS status assigned to the engineer
    job = RepairJob(
        customer_id=1,  # Assuming a customer exists
        engineer_id=engineer_user.id,
        address_id=1,  # Assuming an address exists
        laptop_manufacturer="Quote Test",
        laptop_model="Engineer Quote Model",
        reported_symptoms="Needs cost estimate",
        repair_type_requested=RepairType.HARDWARE,
        status=JobStatus.LAB_DIAGNOSIS,  # Valid status for setting estimated cost
        payment_status=PaymentStatus.PENDING,
        customer_consent_for_lab=True
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    
    # Override the user dependency
    app.dependency_overrides[get_current_user] = override_get_current_user_engineer(engineer_user)
    
    # Prepare quote update data - estimated cost only
    quote_data = {
        "estimated_cost": 125.50,
        "notes": "Estimated cost for replacing motherboard capacitors"
    }
    
    # Make the request
    response = test_client.patch(f"/api/v1/jobs/{job.id}/quote", json=quote_data)
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert data["estimated_cost"] == 125.50
    
    # Notes should be added to engineer_notes
    assert "engineer_notes" in data
    assert data["engineer_notes"] is not None
    assert quote_data["notes"] in data["engineer_notes"]
    
    # Update job to a status where final cost can be set
    job.status = JobStatus.REPAIR_IN_PROGRESS_LAB
    db.commit()
    
    # Prepare quote update data - final cost
    quote_data = {
        "final_cost": 150.00,
        "notes": "Final cost after completing repairs"
    }
    
    # Make the request
    response = test_client.patch(f"/api/v1/jobs/{job.id}/quote", json=quote_data)
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert data["final_cost"] == 150.00
    
    # Clean up
    app.dependency_overrides.clear()


def test_admin_update_job_quote(
    test_client: TestClient,
    admin_user: User,
    db: Session
):
    """
    Test that admins can update quotes for any job.
    """
    # Create a job in ON_SITE_DIAGNOSIS status
    job = RepairJob(
        customer_id=1,  # Assuming a customer exists
        address_id=1,  # Assuming an address exists
        laptop_manufacturer="Quote Test",
        laptop_model="Admin Quote Model",
        reported_symptoms="Needs admin quote",
        repair_type_requested=RepairType.HARDWARE,
        status=JobStatus.ON_SITE_DIAGNOSIS,  # Valid status for setting estimated cost
        payment_status=PaymentStatus.PENDING,
        customer_consent_for_lab=False
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    
    # Override the user dependency
    app.dependency_overrides[get_current_user] = override_get_current_user_admin(admin_user)
    
    # Prepare quote update data - estimated cost only
    quote_data = {
        "estimated_cost": 200.75,
        "notes": "Admin estimate for on-site repair"
    }
    
    # Make the request
    response = test_client.patch(f"/api/v1/jobs/{job.id}/quote", json=quote_data)
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert data["estimated_cost"] == 200.75
    
    # Notes should be added to admin_notes
    assert "admin_notes" in data
    assert data["admin_notes"] is not None
    assert quote_data["notes"] in data["admin_notes"]
    
    # Test setting final cost in an invalid status
    quote_data = {
        "final_cost": 225.00,
        "notes": "Trying to set final cost too early"
    }
    
    # Make the request
    response = test_client.patch(f"/api/v1/jobs/{job.id}/quote", json=quote_data)
    
    # Check response - should be rejected with 422 because ON_SITE_DIAGNOSIS is not valid for final cost
    assert response.status_code == 422
    assert "final cost" in response.json()["detail"].lower()
    
    # Update job status to a valid one for final cost
    job.status = JobStatus.PENDING_PAYMENT
    db.commit()
    
    # Prepare quote update data - final cost
    quote_data = {
        "final_cost": 225.00,
        "notes": "Final cost for completed job"
    }
    
    # Make the request
    response = test_client.patch(f"/api/v1/jobs/{job.id}/quote", json=quote_data)
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert data["final_cost"] == 225.00
    
    # Clean up
    app.dependency_overrides.clear()


def test_invalid_job_quote_status(
    test_client: TestClient,
    admin_user: User,
    db: Session
):
    """
    Test that quotes cannot be updated for jobs in invalid statuses.
    """
    # Create a job in PENDING_ASSIGNMENT status (invalid for setting costs)
    job = RepairJob(
        customer_id=1,  # Assuming a customer exists
        address_id=1,  # Assuming an address exists
        laptop_manufacturer="Invalid Status",
        laptop_model="Invalid Quote Model",
        reported_symptoms="Testing invalid status for quotes",
        repair_type_requested=RepairType.HARDWARE,
        status=JobStatus.PENDING_ASSIGNMENT,  # Invalid status for setting estimated cost
        payment_status=PaymentStatus.PENDING,
        customer_consent_for_lab=False
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    
    # Override the user dependency
    app.dependency_overrides[get_current_user] = override_get_current_user_admin(admin_user)
    
    # Prepare quote update data - estimated cost
    quote_data = {
        "estimated_cost": 150.00,
        "notes": "Trying to set estimate before diagnosis"
    }
    
    # Make the request
    response = test_client.patch(f"/api/v1/jobs/{job.id}/quote", json=quote_data)
    
    # Check response - should be rejected with 422
    assert response.status_code == 422
    assert "estimated cost" in response.json()["detail"].lower()
    
    # Clean up
    app.dependency_overrides.clear() 