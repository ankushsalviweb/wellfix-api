import pytest
import uuid
from fastapi.testclient import TestClient
import logging

from wellfix_api.models.user import UserRole
from wellfix_api.models.service_area import ServiceableArea
from wellfix_api.core.security import get_password_hash
from wellfix_api.models.user import User
from wellfix_api.core.db import get_db
from wellfix_api.main import app
from wellfix_api.core.dependencies import get_current_user

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_user_override(user: User):
    """Create an override for the get_current_user dependency that returns a fixed user."""
    async def get_current_user_override():
        return user
    return get_current_user_override

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
def normal_user(db_session, request):
    """Create a normal user in the database."""
    # Generate a unique email
    unique_id = str(uuid.uuid4())[:8]
    user_email = f"user_{unique_id}@example.com"
    
    user = User(
        email=user_email,
        password_hash=get_password_hash("userpassword"),
        first_name="Normal",
        last_name="User",
        phone_number="1111111111",
        role=UserRole.CUSTOMER,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    # Clean up function for the fixture
    def cleanup():
        user.is_active = False
        db_session.commit()
    
    request.addfinalizer(cleanup)
    return user

@pytest.fixture(scope="function")
def test_service_area(db_session, admin_user, request):
    """Create a test serviceable area."""
    pincode = f"test_{uuid.uuid4().hex[:6]}"
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

def test_get_all_serviceable_areas_admin(test_client, admin_user, test_service_area):
    """Test that an admin can retrieve all serviceable areas."""
    # Override the get_current_user dependency with our admin user
    original_dependency = app.dependency_overrides.get(get_current_user)
    app.dependency_overrides[get_current_user] = get_user_override(admin_user)
    
    try:
        # Call the admin endpoint
        response = test_client.get("/api/v1/admin/serviceable-areas")
        
        # Check the response
        assert response.status_code == 200
        data = response.json()
        
        # Response should be a list object with items
        assert "items" in data
        assert "total" in data
        
        # Ensure our test service area is in the response
        area_pincodes = [area["pincode"] for area in data["items"]]
        assert test_service_area.pincode in area_pincodes
    finally:
        # Restore the original dependency (or clear if none)
        if original_dependency:
            app.dependency_overrides[get_current_user] = original_dependency
        else:
            app.dependency_overrides.pop(get_current_user, None)

def test_get_all_serviceable_areas_non_admin(test_client, normal_user, test_service_area):
    """Test that a non-admin cannot retrieve serviceable areas."""
    # Override the get_current_user dependency with our normal user
    original_dependency = app.dependency_overrides.get(get_current_user)
    app.dependency_overrides[get_current_user] = get_user_override(normal_user)
    
    try:
        # Call the admin endpoint
        response = test_client.get("/api/v1/admin/serviceable-areas")
        
        # Check the response - should be forbidden
        assert response.status_code == 403
        assert "This action requires admin privileges" in response.text
    finally:
        # Restore the original dependency (or clear if none)
        if original_dependency:
            app.dependency_overrides[get_current_user] = original_dependency
        else:
            app.dependency_overrides.pop(get_current_user, None)

def test_create_serviceable_area_admin(test_client, admin_user, db_session):
    """Test that an admin can create a new serviceable area."""
    # Override the get_current_user dependency with our admin user
    original_dependency = app.dependency_overrides.get(get_current_user)
    app.dependency_overrides[get_current_user] = get_user_override(admin_user)
    
    try:
        # Create a new area data
        pincode = f"new_{uuid.uuid4().hex[:6]}"
        area_data = {
            "pincode": pincode,
            "is_active": True
        }
        
        # Call the admin endpoint
        response = test_client.post("/api/v1/admin/serviceable-areas", json=area_data)
        
        # Check the response
        assert response.status_code == 201
        data = response.json()
        assert data["pincode"] == pincode
        assert data["is_active"] is True
        assert "created_at" in data
        
        # Verify in the database
        db_area = db_session.query(ServiceableArea).filter(ServiceableArea.pincode == pincode).first()
        assert db_area is not None
        assert db_area.is_active is True
        assert db_area.added_by_admin_id == admin_user.id
        
        # Clean up
        db_session.delete(db_area)
        db_session.commit()
    finally:
        # Restore the original dependency (or clear if none)
        if original_dependency:
            app.dependency_overrides[get_current_user] = original_dependency
        else:
            app.dependency_overrides.pop(get_current_user, None)

def test_create_serviceable_area_non_admin(test_client, normal_user):
    """Test that a non-admin cannot create a new serviceable area."""
    # Override the get_current_user dependency with our normal user
    original_dependency = app.dependency_overrides.get(get_current_user)
    app.dependency_overrides[get_current_user] = get_user_override(normal_user)
    
    try:
        # Create a new area data
        pincode = f"new_{uuid.uuid4().hex[:6]}"
        area_data = {
            "pincode": pincode,
            "is_active": True
        }
        
        # Call the admin endpoint
        response = test_client.post("/api/v1/admin/serviceable-areas", json=area_data)
        
        # Check the response - should be forbidden
        assert response.status_code == 403
        assert "This action requires admin privileges" in response.text
    finally:
        # Restore the original dependency (or clear if none)
        if original_dependency:
            app.dependency_overrides[get_current_user] = original_dependency
        else:
            app.dependency_overrides.pop(get_current_user, None)

def test_update_serviceable_area_admin(test_client, admin_user, test_service_area, db_session):
    """Test that an admin can update a serviceable area."""
    # Override the get_current_user dependency with our admin user
    original_dependency = app.dependency_overrides.get(get_current_user)
    app.dependency_overrides[get_current_user] = get_user_override(admin_user)
    
    try:
        # Create update data - toggle the is_active status
        update_data = {
            "is_active": not test_service_area.is_active
        }
        
        # Call the admin endpoint
        response = test_client.patch(f"/api/v1/admin/serviceable-areas/{test_service_area.pincode}", json=update_data)
        
        # Check the response
        assert response.status_code == 200
        data = response.json()
        assert data["pincode"] == test_service_area.pincode
        assert data["is_active"] == update_data["is_active"]
        
        # Verify in the database
        db_session.refresh(test_service_area)
        assert test_service_area.is_active == update_data["is_active"]
    finally:
        # Restore the original dependency (or clear if none)
        if original_dependency:
            app.dependency_overrides[get_current_user] = original_dependency
        else:
            app.dependency_overrides.pop(get_current_user, None)

def test_update_serviceable_area_non_admin(test_client, normal_user, test_service_area):
    """Test that a non-admin cannot update a serviceable area."""
    # Override the get_current_user dependency with our normal user
    original_dependency = app.dependency_overrides.get(get_current_user)
    app.dependency_overrides[get_current_user] = get_user_override(normal_user)
    
    try:
        # Create update data
        update_data = {
            "is_active": False
        }
        
        # Call the admin endpoint
        response = test_client.patch(f"/api/v1/admin/serviceable-areas/{test_service_area.pincode}", json=update_data)
        
        # Check the response - should be forbidden
        assert response.status_code == 403
        assert "This action requires admin privileges" in response.text
    finally:
        # Restore the original dependency (or clear if none)
        if original_dependency:
            app.dependency_overrides[get_current_user] = original_dependency
        else:
            app.dependency_overrides.pop(get_current_user, None)

def test_get_serviceable_area_admin(test_client, admin_user, test_service_area):
    """Test that an admin can get a specific serviceable area by pincode."""
    # Override the get_current_user dependency with our admin user
    original_dependency = app.dependency_overrides.get(get_current_user)
    app.dependency_overrides[get_current_user] = get_user_override(admin_user)
    
    try:
        # Call the admin endpoint
        response = test_client.get(f"/api/v1/admin/serviceable-areas/{test_service_area.pincode}")
        
        # Check the response
        assert response.status_code == 200
        data = response.json()
        assert data["pincode"] == test_service_area.pincode
        assert data["is_active"] == test_service_area.is_active
        assert "created_at" in data
    finally:
        # Restore the original dependency (or clear if none)
        if original_dependency:
            app.dependency_overrides[get_current_user] = original_dependency
        else:
            app.dependency_overrides.pop(get_current_user, None)

def test_get_nonexistent_serviceable_area_admin(test_client, admin_user):
    """Test that an admin gets a 404 when requesting a non-existent serviceable area."""
    # Override the get_current_user dependency with our admin user
    original_dependency = app.dependency_overrides.get(get_current_user)
    app.dependency_overrides[get_current_user] = get_user_override(admin_user)
    
    try:
        # Call the admin endpoint with a non-existent pincode
        non_existent_pincode = f"nonexistent_{uuid.uuid4().hex[:6]}"
        response = test_client.get(f"/api/v1/admin/serviceable-areas/{non_existent_pincode}")
        
        # Check the response - should be 404
        assert response.status_code == 404
        assert "not found" in response.text.lower()
    finally:
        # Restore the original dependency (or clear if none)
        if original_dependency:
            app.dependency_overrides[get_current_user] = original_dependency
        else:
            app.dependency_overrides.pop(get_current_user, None) 