"""
Direct tests for the jobs implementation functionality.
"""

import pytest
import pytest_asyncio
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
import uuid
import asyncio

from wellfix_api.api.v1.endpoints.jobs import create_job
from wellfix_api.models.user import User, UserRole
from wellfix_api.models.address import Address
from wellfix_api.models.service_area import ServiceableArea
from wellfix_api.models.job import RepairJob
from wellfix_api.models.enums import JobStatus, RepairType, PaymentStatus
from wellfix_api.schemas.job import JobCreate
from wellfix_api.crud.crud_job import create_job as crud_create_job
from wellfix_api.crud.crud_address import get_address
from wellfix_api.crud.crud_service_area import is_pincode_serviceable
from fastapi import HTTPException


@pytest.mark.usefixtures("db_session")
class TestJobsImplementation:
    """Tests for the job creation functionality without API layer."""
    
    @pytest.mark.asyncio
    async def test_create_job_validation_address_ownership(self, db_session):
        """Test that creating a job validates address ownership."""
        # Set up
        customer_id = str(uuid.uuid4())
        other_user_id = str(uuid.uuid4())
        address_id = str(uuid.uuid4())
        
        # Create a user
        customer = User(
            id=customer_id,
            email="test@example.com",
            password_hash="test_hash",
            first_name="Test",
            last_name="User",
            phone_number="1234567890",
            role=UserRole.CUSTOMER,
            is_active=True
        )
        db_session.add(customer)
        
        # Create an address that belongs to another user
        address = Address(
            id=address_id,
            user_id=other_user_id,
            street_address="123 Test St",
            city="Test City",
            state="Test State",
            pincode="12345",
            is_default=True
        )
        db_session.add(address)
        db_session.commit()
        
        # Create job data
        job_data = JobCreate(
            address_id=address_id,
            laptop_manufacturer="Dell",
            laptop_model="XPS 13",
            reported_symptoms="Not working",
            repair_type_requested=RepairType.HARDWARE
        )
        
        # Mock the address lookup to return our test address
        with patch('wellfix_api.crud.crud_address.get_address', return_value=address):
            # Act and Assert
            with pytest.raises(HTTPException) as excinfo:
                await create_job(
                    job_data=job_data,
                    db=db_session,
                    current_user=customer
                )
            
            # Verify that the error message is about address ownership
            assert "does not belong to the current user" in str(excinfo.value.detail)
    
    @pytest.mark.asyncio
    async def test_create_job_validation_serviceable_area(self, db_session):
        """Test that creating a job validates the address is in a serviceable area."""
        # Set up
        customer_id = str(uuid.uuid4())
        address_id = str(uuid.uuid4())
        
        # Create a user
        customer = User(
            id=customer_id,
            email="test@example.com",
            password_hash="test_hash",
            first_name="Test",
            last_name="User",
            phone_number="1234567890",
            role=UserRole.CUSTOMER,
            is_active=True
        )
        db_session.add(customer)
        
        # Create an address
        address = Address(
            id=address_id,
            user_id=customer_id,
            street_address="123 Test St",
            city="Test City",
            state="Test State",
            pincode="12345",
            is_default=True
        )
        db_session.add(address)
        db_session.commit()
        
        # Create job data
        job_data = JobCreate(
            address_id=address_id,
            laptop_manufacturer="Dell",
            laptop_model="XPS 13",
            reported_symptoms="Not working",
            repair_type_requested=RepairType.HARDWARE
        )
        
        # Mock the address lookup to return our test address
        with patch('wellfix_api.crud.crud_address.get_address', return_value=address):
            # Mock the serviceable area check to return False
            with patch('wellfix_api.crud.crud_service_area.is_pincode_serviceable', return_value=False):
                # Act and Assert
                with pytest.raises(HTTPException) as excinfo:
                    await create_job(
                        job_data=job_data,
                        db=db_session,
                        current_user=customer
                    )
                
                # Verify that the error message is about serviceable area
                assert "not in a serviceable area" in str(excinfo.value.detail)
    
    @pytest.mark.asyncio
    async def test_create_job_notification_called(self, db_session):
        """Test that creating a job calls the notification function."""
        # Set up
        customer_id = str(uuid.uuid4())
        address_id = str(uuid.uuid4())
        
        # Create a user
        customer = User(
            id=customer_id,
            email="test@example.com",
            password_hash="test_hash",
            first_name="Test",
            last_name="User",
            phone_number="1234567890",
            role=UserRole.CUSTOMER,
            is_active=True
        )
        db_session.add(customer)
        
        # Create an address
        address = Address(
            id=address_id,
            user_id=customer_id,
            street_address="123 Test St",
            city="Test City",
            state="Test State",
            pincode="12345",
            is_default=True
        )
        db_session.add(address)
        db_session.commit()
        
        # Create job data
        job_data = JobCreate(
            address_id=address_id,
            laptop_manufacturer="Dell",
            laptop_model="XPS 13",
            reported_symptoms="Not working",
            repair_type_requested=RepairType.HARDWARE
        )
        
        # Create a sample job that would be returned from the database
        test_job = RepairJob(
            id=99,
            customer_id=customer_id,
            address_id=address_id,
            status=JobStatus.PENDING_ASSIGNMENT,
            laptop_manufacturer="Dell",
            laptop_model="XPS 13",
            reported_symptoms="Not working",
            repair_type_requested=RepairType.HARDWARE
        )
        
        # Mock the address lookup to return our test address
        with patch('wellfix_api.crud.crud_address.get_address', return_value=address):
            # Mock the serviceable area check to return True
            with patch('wellfix_api.crud.crud_service_area.is_pincode_serviceable', return_value=True):
                # Use Side_effect to call a function that captures the args
                created_job_data = {}
                
                def mock_create_job(db, job_data, customer_id):
                    """Mock version of create_job that returns our test job"""
                    created_job_data['args'] = (db, job_data, customer_id)
                    return test_job
                
                # Mock the job creation to return our test job
                with patch('wellfix_api.crud.crud_job.create_job', side_effect=mock_create_job):
                    # Mock the notification function
                    with patch('wellfix_api.api.v1.endpoints.jobs.notify_admin_new_job') as mock_notify:
                        # Act
                        result = await create_job(
                            job_data=job_data,
                            db=db_session,
                            current_user=customer
                        )
                        
                        # Assert
                        mock_notify.assert_called_once_with(test_job)
                        assert result == test_job 