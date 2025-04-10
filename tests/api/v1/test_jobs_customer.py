"""
Tests for the customer-facing job API endpoints.
"""

import pytest
from unittest.mock import patch
from fastapi import status

from wellfix_api.models.enums import JobStatus, RepairType, PaymentStatus


@pytest.mark.usefixtures("client", "db_session")
class TestCustomerJobEndpoints:
    """Tests for job endpoints from customer perspective."""
    
    def test_create_job_success(self, client, customer_token, test_address):
        """Test successful job creation."""
        # Use the customer's address created in the fixture
        job_data = {
            "address_id": str(test_address.id),
            "laptop_manufacturer": "Dell",
            "laptop_model": "XPS 15",
            "laptop_serial_number": "XPS15-12345",
            "reported_symptoms": "Display flickering and keyboard not responding",
            "repair_type_requested": RepairType.HARDWARE.value
        }
        
        # Mock the notification function to avoid actual logging during tests
        with patch('wellfix_api.api.v1.endpoints.jobs.notify_admin_new_job') as mock_notify:
            response = client.post(
                "/api/v1/jobs",
                json=job_data,
                headers={"Authorization": f"Bearer {customer_token}"}
            )
        
        # Verify the response
        assert response.status_code == status.HTTP_201_CREATED
        
        data = response.json()
        assert data["laptop_manufacturer"] == job_data["laptop_manufacturer"]
        assert data["laptop_model"] == job_data["laptop_model"]
        assert data["laptop_serial_number"] == job_data["laptop_serial_number"]
        assert data["reported_symptoms"] == job_data["reported_symptoms"]
        assert data["repair_type_requested"] == job_data["repair_type_requested"]
        assert data["status"] == JobStatus.PENDING_ASSIGNMENT.value
        assert data["payment_status"] == PaymentStatus.PENDING.value
        
        # Verify notification was called
        mock_notify.assert_called_once()
    
    def test_create_job_nonexistent_address(self, client, customer_token):
        """Test job creation with non-existent address ID."""
        job_data = {
            "address_id": "00000000-0000-0000-0000-000000000000",  # Non-existent UUID
            "laptop_manufacturer": "Dell",
            "laptop_model": "XPS 15",
            "reported_symptoms": "Display flickering",
            "repair_type_requested": RepairType.HARDWARE.value
        }
        
        response = client.post(
            "/api/v1/jobs",
            json=job_data,
            headers={"Authorization": f"Bearer {customer_token}"}
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Address not found" in response.json()["detail"]
    
    def test_create_job_unauthorized_address(self, client, customer_token, test_address_other_user):
        """Test job creation with address belonging to another user."""
        job_data = {
            "address_id": str(test_address_other_user.id),
            "laptop_manufacturer": "Dell",
            "laptop_model": "XPS 15",
            "reported_symptoms": "Display flickering",
            "repair_type_requested": RepairType.HARDWARE.value
        }
        
        response = client.post(
            "/api/v1/jobs",
            json=job_data,
            headers={"Authorization": f"Bearer {customer_token}"}
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "does not belong to the current user" in response.json()["detail"]
    
    def test_create_job_non_serviceable_area(self, client, customer_token, test_address_non_serviceable):
        """Test job creation with address in a non-serviceable area."""
        job_data = {
            "address_id": str(test_address_non_serviceable.id),
            "laptop_manufacturer": "Dell",
            "laptop_model": "XPS 15",
            "reported_symptoms": "Display flickering",
            "repair_type_requested": RepairType.HARDWARE.value
        }
        
        response = client.post(
            "/api/v1/jobs",
            json=job_data,
            headers={"Authorization": f"Bearer {customer_token}"}
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert "not in a serviceable area" in response.json()["detail"]
    
    def test_create_job_engineer_forbidden(self, client, engineer_token):
        """Test that engineers cannot create jobs."""
        job_data = {
            "laptop_manufacturer": "Dell",
            "laptop_model": "XPS 15",
            "reported_symptoms": "Display flickering",
            "repair_type_requested": RepairType.HARDWARE.value
        }
        
        response = client.post(
            "/api/v1/jobs",
            json=job_data,
            headers={"Authorization": f"Bearer {engineer_token}"}
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Only customers can create repair jobs" in response.json()["detail"]
    
    def test_create_job_admin_forbidden(self, client, admin_token):
        """Test that admins cannot create jobs."""
        job_data = {
            "laptop_manufacturer": "Dell",
            "laptop_model": "XPS 15",
            "reported_symptoms": "Display flickering",
            "repair_type_requested": RepairType.HARDWARE.value
        }
        
        response = client.post(
            "/api/v1/jobs",
            json=job_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Only customers can create repair jobs" in response.json()["detail"] 