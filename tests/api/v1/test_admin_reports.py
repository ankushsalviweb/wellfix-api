"""
Integration tests for admin reporting endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from wellfix_api.main import app
from wellfix_api.models.user import User, UserRole
from wellfix_api.models.enums import JobStatus, PaymentStatus, RepairType
from wellfix_api.core.dependencies import get_db, get_current_user
from wellfix_api.models.job import RepairJob, JobStatusUpdate, Rating
from tests.utils.test_db import override_get_db
from tests.api.v1.test_jobs import (
    override_get_current_user_admin,
    override_get_current_user_engineer,
    override_get_current_user_customer,
    test_client,
    db,
    admin_user,
    engineer_user,
    customer_user,
    test_address
)


# Setup test data
@pytest.fixture
def setup_test_data(db: Session, customer_user: User, engineer_user: User, admin_user: User, test_address):
    """
    Set up test data for reporting tests.
    
    Creates multiple jobs in various statuses for testing reporting functionality.
    """
    # Create jobs in various statuses
    jobs = []
    
    # PENDING_ASSIGNMENT job
    job1 = RepairJob(
        customer_id=customer_user.id,
        address_id=test_address.id,
        laptop_manufacturer="Report Test 1",
        laptop_model="Report Model 1",
        laptop_serial_number="REPORT001",
        reported_symptoms="Job for reporting tests",
        repair_type_requested=RepairType.HARDWARE,
        status=JobStatus.PENDING_ASSIGNMENT,
        payment_status=PaymentStatus.PENDING,
        customer_consent_for_lab=False
    )
    db.add(job1)
    
    # ASSIGNED job
    job2 = RepairJob(
        customer_id=customer_user.id,
        engineer_id=engineer_user.id,
        address_id=test_address.id,
        laptop_manufacturer="Report Test 2",
        laptop_model="Report Model 2",
        laptop_serial_number="REPORT002",
        reported_symptoms="Job for reporting tests",
        repair_type_requested=RepairType.SOFTWARE,
        status=JobStatus.ASSIGNED,
        payment_status=PaymentStatus.PENDING,
        customer_consent_for_lab=False
    )
    db.add(job2)
    
    # COMPLETED job with rating
    job3 = RepairJob(
        customer_id=customer_user.id,
        engineer_id=engineer_user.id,
        address_id=test_address.id,
        laptop_manufacturer="Report Test 3",
        laptop_model="Report Model 3",
        laptop_serial_number="REPORT003",
        reported_symptoms="Job for reporting tests",
        repair_type_requested=RepairType.HARDWARE,
        status=JobStatus.COMPLETED,
        payment_status=PaymentStatus.COMPLETED,
        customer_consent_for_lab=False,
        final_cost=100.00
    )
    db.add(job3)
    
    # Commit to get IDs
    db.commit()
    
    # Add status updates for job3
    status_update1 = JobStatusUpdate(
        job_id=job3.id,
        user_id=admin_user.id,
        previous_status=JobStatus.PENDING_ASSIGNMENT,
        new_status=JobStatus.ASSIGNED,
        notes="Assigned to engineer"
    )
    db.add(status_update1)
    
    status_update2 = JobStatusUpdate(
        job_id=job3.id,
        user_id=engineer_user.id,
        previous_status=JobStatus.ASSIGNED,
        new_status=JobStatus.COMPLETED,
        notes="Job completed"
    )
    db.add(status_update2)
    
    # Add rating for job3
    rating = Rating(
        job_id=job3.id,
        customer_id=customer_user.id,
        engineer_id=engineer_user.id,
        score=5,
        comment="Excellent service"
    )
    db.add(rating)
    
    # In-lab job
    job4 = RepairJob(
        customer_id=customer_user.id,
        engineer_id=engineer_user.id,
        address_id=test_address.id,
        laptop_manufacturer="Report Test 4",
        laptop_model="Report Model 4",
        laptop_serial_number="REPORT004",
        reported_symptoms="Job for reporting tests",
        repair_type_requested=RepairType.HARDWARE,
        status=JobStatus.LAB_DIAGNOSIS,
        payment_status=PaymentStatus.PENDING,
        customer_consent_for_lab=True
    )
    db.add(job4)
    
    db.commit()
    
    return [job1, job2, job3, job4]


def test_dashboard_report_admin_access(
    test_client: TestClient,
    admin_user: User,
    setup_test_data
):
    """
    Test that admin users can access the dashboard report.
    """
    # Override the user dependency
    app.dependency_overrides[get_current_user] = override_get_current_user_admin(admin_user)
    
    # Make the request
    response = test_client.get("/api/v1/admin/reports/dashboard")
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    
    # Check response structure
    assert "job_status_counts" in data
    assert "average_rating" in data
    assert "pending_assignments" in data
    assert "jobs_in_lab" in data
    assert "completed_last_30_days" in data
    assert "total_customers" in data
    assert "total_engineers" in data
    
    # Verify specific values based on test data
    assert data["job_status_counts"].get("PENDING_ASSIGNMENT", 0) >= 1
    assert data["job_status_counts"].get("ASSIGNED", 0) >= 1
    assert data["job_status_counts"].get("COMPLETED", 0) >= 1
    assert data["job_status_counts"].get("LAB_DIAGNOSIS", 0) >= 1
    
    # Clean up
    app.dependency_overrides.clear()


def test_engineer_productivity_admin_access(
    test_client: TestClient,
    admin_user: User,
    setup_test_data
):
    """
    Test that admin users can access the engineer productivity report.
    """
    # Override the user dependency
    app.dependency_overrides[get_current_user] = override_get_current_user_admin(admin_user)
    
    # Make the request
    response = test_client.get("/api/v1/admin/reports/engineer-productivity")
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    
    # Check response structure
    assert "time_period" in data
    assert "engineers" in data
    assert isinstance(data["engineers"], list)
    
    # If engineers data is present, check its structure
    if data["engineers"]:
        engineer = data["engineers"][0]
        assert "id" in engineer
        assert "name" in engineer
        assert "jobs_completed" in engineer
        # avg_completion_time may be None if no completed jobs
        assert "avg_rating" in engineer
    
    # Clean up
    app.dependency_overrides.clear()


def test_non_admin_access_forbidden(
    test_client: TestClient,
    engineer_user: User,
    setup_test_data
):
    """
    Test that non-admin users cannot access the admin reports.
    """
    # Override the user dependency
    app.dependency_overrides[get_current_user] = override_get_current_user_engineer(engineer_user)
    
    # Try to access dashboard report
    response = test_client.get("/api/v1/admin/reports/dashboard")
    assert response.status_code == 403
    
    # Try to access engineer productivity report
    response = test_client.get("/api/v1/admin/reports/engineer-productivity")
    assert response.status_code == 403
    
    # Clean up
    app.dependency_overrides.clear()


def test_engineer_productivity_with_days_param(
    test_client: TestClient,
    admin_user: User,
    setup_test_data
):
    """
    Test the engineer productivity report with different days parameter.
    """
    # Override the user dependency
    app.dependency_overrides[get_current_user] = override_get_current_user_admin(admin_user)
    
    # Test with different days parameters
    test_days = [7, 30, 90]
    
    for days in test_days:
        # Make the request
        response = test_client.get(f"/api/v1/admin/reports/engineer-productivity?days={days}")
        
        # Check response
        assert response.status_code == 200
        data = response.json()
        
        # Verify time period matches
        assert f"Last {days} days" in data["time_period"]
    
    # Clean up
    app.dependency_overrides.clear() 