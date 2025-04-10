import pytest
import uuid
from fastapi.testclient import TestClient
import logging

from wellfix_api.models.service_area import ServiceableArea
from wellfix_api.models.user import User, UserRole
from wellfix_api.core.security import get_password_hash
from wellfix_api.core.db import get_db
from wellfix_api.main import app

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@pytest.fixture(scope="function")
def test_client(db_session):
    """Create a custom test client that properly overrides the get_db dependency."""
    def override_get_db():
        """Return the session-scoped database session."""
        try:
            yield db_session
        finally:
            pass

    # Override database dependency
    app.dependency_overrides[get_db] = override_get_db
    
    # Create test client
    with TestClient(app) as client:
        yield client
    
    # Clean up override after test
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def admin_user(db_session, request):
    """Create an admin user in the database."""
    # Generate a unique email
    unique_id = str(uuid.uuid4())[:8]
    admin_email = f"admin_{unique_id}@example.com"
    
    admin = User(
        id=str(uuid.uuid4()),
        email=admin_email,
        password_hash=get_password_hash("adminpassword"),
        first_name="Admin",
        last_name="User",
        phone_number="0000000000",
        role=UserRole.ADMIN,
        is_active=True
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    
    # Clean up function for the fixture
    def cleanup():
        admin.is_active = False
        db_session.commit()
    
    request.addfinalizer(cleanup)
    return admin

@pytest.fixture(scope="function")
def active_service_area(db_session, admin_user, request):
    """Create an active serviceable area."""
    pincode = f"active_{uuid.uuid4().hex[:6]}"
    service_area = ServiceableArea(
        pincode=pincode,
        is_active=True,
        added_by_admin_id=admin_user.id
    )
    db_session.add(service_area)
    db_session.commit()
    db_session.refresh(service_area)
    
    # Clean up function for the fixture
    def cleanup():
        db_session.delete(service_area)
        db_session.commit()
    
    request.addfinalizer(cleanup)
    return service_area

@pytest.fixture(scope="function")
def inactive_service_area(db_session, admin_user, request):
    """Create an inactive serviceable area."""
    pincode = f"inactive_{uuid.uuid4().hex[:6]}"
    service_area = ServiceableArea(
        pincode=pincode,
        is_active=False,
        added_by_admin_id=admin_user.id
    )
    db_session.add(service_area)
    db_session.commit()
    db_session.refresh(service_area)
    
    # Clean up function for the fixture
    def cleanup():
        db_session.delete(service_area)
        db_session.commit()
    
    request.addfinalizer(cleanup)
    return service_area

def test_check_active_service_area(test_client, active_service_area):
    """Test that checking an active serviceable area returns true."""
    # Make the request
    response = test_client.get(f"/api/v1/service-areas/check/{active_service_area.pincode}")
    
    # Check the response
    assert response.status_code == 200
    data = response.json()
    assert data["pincode"] == active_service_area.pincode
    assert data["is_serviceable"] is True

def test_check_inactive_service_area(test_client, inactive_service_area):
    """Test that checking an inactive serviceable area returns false."""
    # Make the request
    response = test_client.get(f"/api/v1/service-areas/check/{inactive_service_area.pincode}")
    
    # Check the response
    assert response.status_code == 200
    data = response.json()
    assert data["pincode"] == inactive_service_area.pincode
    assert data["is_serviceable"] is False

def test_check_nonexistent_service_area(test_client):
    """Test that checking a non-existent serviceable area returns false."""
    # Generate a non-existent pincode
    non_existent_pincode = f"nonexistent_{uuid.uuid4().hex[:6]}"
    
    # Make the request
    response = test_client.get(f"/api/v1/service-areas/check/{non_existent_pincode}")
    
    # Check the response
    assert response.status_code == 200
    data = response.json()
    assert data["pincode"] == non_existent_pincode
    assert data["is_serviceable"] is False 