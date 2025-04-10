"""
Test fixtures for the API v1 endpoints.
"""

import pytest
import uuid
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from typing import Dict, Generator, List

from wellfix_api.main import app
from wellfix_api.core.db import get_db, SessionLocal
from wellfix_api.core.security import create_access_token
from wellfix_api.models.user import User, UserRole
from wellfix_api.models.address import Address
from wellfix_api.models.service_area import ServiceableArea
from wellfix_api.crud.crud_user import create_user
from wellfix_api.schemas.user import UserCreate
from wellfix_api.core.dependencies import get_current_user
from wellfix_api.models.enums import JobStatus, RepairType, PaymentStatus
from wellfix_api.models.job import RepairJob


@pytest.fixture
def client(db_session):
    """Test client with db session override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    
    # Clear dependency overrides after test
    app.dependency_overrides.clear()


# User fixtures with fixed UUIDs for testing
@pytest.fixture(scope="function")
def test_customer(db_session):
    """Create a test customer user with a fixed UUID."""
    # Use a fixed UUID to ensure consistency between token and database
    fixed_id = "11111111-1111-1111-1111-111111111111"
    
    # Generate a unique email with timestamp to avoid conflicts
    unique_email = f"test_customer_{datetime.now().timestamp()}@example.com"
    
    # Create user directly with the model to set a specific ID
    db_user = User(
        id=fixed_id,
        email=unique_email,
        password_hash="$2b$12$test_hash_for_testing_only",
        first_name="Test",
        last_name="Customer",
        phone_number="1234567890",
        role=UserRole.CUSTOMER,
        is_active=True,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db_session.add(db_user)
    db_session.commit()
    db_session.refresh(db_user)
    return db_user


@pytest.fixture(scope="function")
def test_engineer(db_session):
    """Create a test engineer user with a fixed UUID."""
    # Use a fixed UUID to ensure consistency between token and database
    fixed_id = "22222222-2222-2222-2222-222222222222"
    
    # Generate a unique email with timestamp to avoid conflicts
    unique_email = f"test_engineer_{datetime.now().timestamp()}@example.com"
    
    # Create user directly with the model to set a specific ID
    db_user = User(
        id=fixed_id,
        email=unique_email,
        password_hash="$2b$12$test_hash_for_testing_only",
        first_name="Test",
        last_name="Engineer",
        phone_number="1234567891",
        role=UserRole.ENGINEER,
        is_active=True,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db_session.add(db_user)
    db_session.commit()
    db_session.refresh(db_user)
    return db_user


@pytest.fixture(scope="function")
def test_admin(db_session):
    """Create a test admin user with a fixed UUID."""
    # Use a fixed UUID to ensure consistency between token and database
    fixed_id = "33333333-3333-3333-3333-333333333333"
    
    # Generate a unique email with timestamp to avoid conflicts
    unique_email = f"test_admin_{datetime.now().timestamp()}@example.com"
    
    # Create user directly with the model to set a specific ID
    db_user = User(
        id=fixed_id,
        email=unique_email,
        password_hash="$2b$12$test_hash_for_testing_only",
        first_name="Test",
        last_name="Admin",
        phone_number="1234567892",
        role=UserRole.ADMIN,
        is_active=True,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db_session.add(db_user)
    db_session.commit()
    db_session.refresh(db_user)
    return db_user


@pytest.fixture(scope="function")
def test_customer_2(db_session):
    """Create a second test customer user with a fixed UUID."""
    # Use a fixed UUID to ensure consistency between token and database
    fixed_id = "44444444-4444-4444-4444-444444444444"
    
    # Generate a unique email with timestamp to avoid conflicts
    unique_email = f"test_customer2_{datetime.now().timestamp()}@example.com"
    
    # Create user directly with the model to set a specific ID
    db_user = User(
        id=fixed_id,
        email=unique_email,
        password_hash="$2b$12$test_hash_for_testing_only",
        first_name="Test2",
        last_name="Customer2",
        phone_number="1234567893",
        role=UserRole.CUSTOMER,
        is_active=True,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db_session.add(db_user)
    db_session.commit()
    db_session.refresh(db_user)
    return db_user


# Token fixtures
@pytest.fixture(scope="function")
def customer_token(test_customer):
    """Generate a token for the test customer."""
    # Call the create_access_token function with the user's ID
    token = create_access_token(test_customer.id)
    
    # Also set up dependency override to ensure authentication works properly
    app.dependency_overrides[get_current_user] = lambda: test_customer
    
    return token


@pytest.fixture(scope="function")
def engineer_token(test_engineer):
    """Generate a token for the test engineer."""
    # Call the create_access_token function with the user's ID
    token = create_access_token(test_engineer.id)
    
    # Also set up dependency override to ensure authentication works properly
    app.dependency_overrides[get_current_user] = lambda: test_engineer
    
    return token


@pytest.fixture(scope="function")
def admin_token(test_admin):
    """Generate a token for the test admin."""
    # Call the create_access_token function with the user's ID
    token = create_access_token(test_admin.id)
    
    # Also set up dependency override to ensure authentication works properly
    app.dependency_overrides[get_current_user] = lambda: test_admin
    
    return token


# Helper functions for dependency overrides
def override_get_current_user_customer(user):
    """Create a function that returns a fixed customer user."""
    def get_current_user_override():
        return user
    return get_current_user_override

def override_get_current_user_engineer(user):
    """Create a function that returns a fixed engineer user."""
    def get_current_user_override():
        return user
    return get_current_user_override

def override_get_current_user_admin(user):
    """Create a function that returns a fixed admin user."""
    def get_current_user_override():
        return user
    return get_current_user_override

@pytest.fixture(autouse=True)
def reset_dependency_overrides():
    """Reset dependency overrides after each test."""
    yield
    app.dependency_overrides.clear()


# Serviceable area fixtures
@pytest.fixture(scope="function")
def test_serviceable_area(db_session, test_admin):
    """Create a test serviceable area."""
    area = ServiceableArea(
        pincode="110001",
        is_active=True,
        added_by_admin_id=test_admin.id
    )
    db_session.add(area)
    db_session.commit()
    db_session.refresh(area)
    return area


@pytest.fixture(scope="function")
def test_non_serviceable_area(db_session, test_admin):
    """Create a test non-serviceable area."""
    area = ServiceableArea(
        pincode="220001",
        is_active=False,
        added_by_admin_id=test_admin.id
    )
    db_session.add(area)
    db_session.commit()
    db_session.refresh(area)
    return area


# Address fixtures
@pytest.fixture(scope="function")
def test_address(db_session, test_customer, test_serviceable_area):
    """Create a test address for the test customer in a serviceable area."""
    address = Address(
        user_id=test_customer.id,
        pincode=test_serviceable_area.pincode,
        city="Test City",
        state="Test State",
        street_address="123 Test Street",
        is_default=True
    )
    db_session.add(address)
    db_session.commit()
    db_session.refresh(address)
    return address


@pytest.fixture(scope="function")
def test_address_other_user(db_session, test_customer_2, test_serviceable_area):
    """Create a test address for another user in a serviceable area."""
    address = Address(
        user_id=test_customer_2.id,
        pincode=test_serviceable_area.pincode,
        city="Test City 2",
        state="Test State 2",
        street_address="456 Test Street",
        is_default=True
    )
    db_session.add(address)
    db_session.commit()
    db_session.refresh(address)
    return address


@pytest.fixture(scope="function")
def test_address_non_serviceable(db_session, test_customer, test_non_serviceable_area):
    """Create a test address for the test customer in a non-serviceable area."""
    address = Address(
        user_id=test_customer.id,
        pincode=test_non_serviceable_area.pincode,
        city="Non Serviceable City",
        state="Non Serviceable State",
        street_address="789 Non Serviceable Street",
        is_default=False
    )
    db_session.add(address)
    db_session.commit()
    db_session.refresh(address)
    return address 