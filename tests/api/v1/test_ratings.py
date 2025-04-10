"""
Integration tests for rating endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from wellfix_api.main import app
from wellfix_api.models.user import User, UserRole
from wellfix_api.models.enums import JobStatus, PaymentStatus, RepairType
from wellfix_api.core.dependencies import get_db, get_current_user
from wellfix_api.models.job import RepairJob, Rating
from tests.utils.test_db import override_get_db
from tests.api.v1.test_jobs import (
    override_get_current_user_customer,
    override_get_current_user_engineer,
    override_get_current_user_admin,
    test_client,
    db,
    customer_user,
    engineer_user,
    admin_user,
    test_address
)


@pytest.fixture
def completed_job(db: Session, customer_user: User, engineer_user: User, test_address):
    """
    Create a completed job for testing ratings.
    """
    job = RepairJob(
        customer_id=customer_user.id,
        engineer_id=engineer_user.id,
        address_id=test_address.id,
        laptop_manufacturer="Completed Test",
        laptop_model="Completion Model",
        laptop_serial_number="COMPLETE123",
        reported_symptoms="Job for rating tests",
        repair_type_requested=RepairType.HARDWARE,
        status=JobStatus.COMPLETED,
        payment_status=PaymentStatus.COMPLETED,
        customer_consent_for_lab=False,
        final_cost=120.00
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


@pytest.fixture
def pending_job(db: Session, customer_user: User, test_address):
    """
    Create a pending job for testing inability to rate incomplete jobs.
    """
    job = RepairJob(
        customer_id=customer_user.id,
        address_id=test_address.id,
        laptop_manufacturer="Pending Test",
        laptop_model="Pending Model",
        laptop_serial_number="PENDING123",
        reported_symptoms="Pending job for rating tests",
        repair_type_requested=RepairType.HARDWARE,
        status=JobStatus.PENDING_ASSIGNMENT,
        payment_status=PaymentStatus.PENDING,
        customer_consent_for_lab=False
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def test_customer_submit_rating(test_client: TestClient, customer_user: User, completed_job: RepairJob):
    """
    Test that a customer can submit a rating for their completed job.
    """
    # Override the user dependency
    app.dependency_overrides[get_current_user] = override_get_current_user_customer(customer_user)
    
    # Prepare rating data
    rating_data = {
        "score": 5,
        "comment": "Excellent service, very satisfied!"
    }
    
    # Make the request
    response = test_client.post(f"/api/v1/jobs/{completed_job.id}/ratings", json=rating_data)
    
    # Check response
    assert response.status_code == 201
    data = response.json()
    assert data["job_id"] == completed_job.id
    assert data["customer_id"] == customer_user.id
    assert data["engineer_id"] == completed_job.engineer_id
    assert data["score"] == rating_data["score"]
    assert data["comment"] == rating_data["comment"]
    
    # Clean up
    app.dependency_overrides.clear()


def test_cannot_rate_incomplete_job(test_client: TestClient, customer_user: User, pending_job: RepairJob):
    """
    Test that a job can only be rated when it's in COMPLETED status.
    """
    # Override the user dependency
    app.dependency_overrides[get_current_user] = override_get_current_user_customer(customer_user)
    
    # Prepare rating data
    rating_data = {
        "score": 4,
        "comment": "Good service"
    }
    
    # Make the request - should fail
    response = test_client.post(f"/api/v1/jobs/{pending_job.id}/ratings", json=rating_data)
    
    # Check response - should be 422
    assert response.status_code == 422
    assert "Only completed jobs can be rated" in response.json()["detail"]
    
    # Clean up
    app.dependency_overrides.clear()


def test_cannot_rate_twice(
    test_client: TestClient, 
    customer_user: User, 
    completed_job: RepairJob,
    db: Session
):
    """
    Test that a job cannot be rated more than once.
    """
    # Create a rating first
    rating = Rating(
        job_id=completed_job.id,
        customer_id=customer_user.id,
        engineer_id=completed_job.engineer_id,
        score=4,
        comment="Initial rating"
    )
    db.add(rating)
    db.commit()
    
    # Override the user dependency
    app.dependency_overrides[get_current_user] = override_get_current_user_customer(customer_user)
    
    # Prepare rating data
    rating_data = {
        "score": 5,
        "comment": "Trying to rate again"
    }
    
    # Make the request - should fail
    response = test_client.post(f"/api/v1/jobs/{completed_job.id}/ratings", json=rating_data)
    
    # Check response - should be 422
    assert response.status_code == 422
    assert "already been rated" in response.json()["detail"]
    
    # Clean up
    app.dependency_overrides.clear()


def test_engineer_cannot_submit_rating(
    test_client: TestClient, 
    engineer_user: User, 
    completed_job: RepairJob
):
    """
    Test that only customers can submit ratings, not engineers.
    """
    # Override the user dependency
    app.dependency_overrides[get_current_user] = override_get_current_user_engineer(engineer_user)
    
    # Prepare rating data
    rating_data = {
        "score": 5,
        "comment": "Engineer trying to rate"
    }
    
    # Make the request - should fail
    response = test_client.post(f"/api/v1/jobs/{completed_job.id}/ratings", json=rating_data)
    
    # Check response - should be 403
    assert response.status_code == 403
    assert "Only customers can submit ratings" in response.json()["detail"]
    
    # Clean up
    app.dependency_overrides.clear()


def test_customer_can_get_own_rating(
    test_client: TestClient, 
    customer_user: User, 
    completed_job: RepairJob,
    db: Session
):
    """
    Test that a customer can retrieve a rating for their own job.
    """
    # Create a rating first
    rating = Rating(
        job_id=completed_job.id,
        customer_id=customer_user.id,
        engineer_id=completed_job.engineer_id,
        score=5,
        comment="Rating to retrieve"
    )
    db.add(rating)
    db.commit()
    
    # Override the user dependency
    app.dependency_overrides[get_current_user] = override_get_current_user_customer(customer_user)
    
    # Make the request
    response = test_client.get(f"/api/v1/jobs/{completed_job.id}/ratings")
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert data["job_id"] == completed_job.id
    assert data["score"] == 5
    assert data["comment"] == "Rating to retrieve"
    
    # Clean up
    app.dependency_overrides.clear()


def test_engineer_can_get_job_rating(
    test_client: TestClient, 
    engineer_user: User, 
    completed_job: RepairJob,
    db: Session
):
    """
    Test that the engineer assigned to a job can see its rating.
    """
    # Create a rating first
    rating = Rating(
        job_id=completed_job.id,
        customer_id=completed_job.customer_id,
        engineer_id=engineer_user.id,
        score=4,
        comment="Rating for engineer to see"
    )
    db.add(rating)
    db.commit()
    
    # Override the user dependency
    app.dependency_overrides[get_current_user] = override_get_current_user_engineer(engineer_user)
    
    # Make the request
    response = test_client.get(f"/api/v1/jobs/{completed_job.id}/ratings")
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert data["job_id"] == completed_job.id
    assert data["score"] == 4
    
    # Clean up
    app.dependency_overrides.clear()


def test_admin_list_ratings(
    test_client: TestClient, 
    admin_user: User, 
    db: Session,
    completed_job: RepairJob,
    engineer_user: User
):
    """
    Test that admins can list all ratings.
    """
    # Create some ratings
    rating1 = Rating(
        job_id=completed_job.id,
        customer_id=completed_job.customer_id,
        engineer_id=engineer_user.id,
        score=5,
        comment="First test rating"
    )
    db.add(rating1)
    
    # Add a second job and rating
    second_job = RepairJob(
        customer_id=completed_job.customer_id,
        engineer_id=engineer_user.id,
        address_id=completed_job.address_id,
        laptop_manufacturer="Second Test",
        laptop_model="Second Model",
        laptop_serial_number="SECOND123",
        reported_symptoms="Another job for rating tests",
        repair_type_requested=RepairType.SOFTWARE,
        status=JobStatus.COMPLETED,
        payment_status=PaymentStatus.COMPLETED,
        customer_consent_for_lab=False
    )
    db.add(second_job)
    db.flush()
    
    rating2 = Rating(
        job_id=second_job.id,
        customer_id=second_job.customer_id,
        engineer_id=engineer_user.id,
        score=3,
        comment="Second test rating"
    )
    db.add(rating2)
    db.commit()
    
    # Override the user dependency
    app.dependency_overrides[get_current_user] = override_get_current_user_admin(admin_user)
    
    # Make the request without filters
    response = test_client.get("/api/v1/admin/ratings")
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert data["count"] >= 2  # At least our 2 test ratings
    
    # Test with filter by engineer
    response = test_client.get(f"/api/v1/admin/ratings?engineer_id={engineer_user.id}")
    assert response.status_code == 200
    
    # Test with filter by min_score
    response = test_client.get("/api/v1/admin/ratings?min_score=4")
    assert response.status_code == 200
    filtered_data = response.json()
    # All ratings should have score >= 4
    for rating in filtered_data["ratings"]:
        assert rating["score"] >= 4
    
    # Clean up
    app.dependency_overrides.clear() 