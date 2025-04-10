import pytest
import uuid
from fastapi.testclient import TestClient
import logging

from wellfix_api.models.user import UserRole
from wellfix_api.core.security import get_password_hash
from wellfix_api.models.user import User
from wellfix_api.crud import get_user_by_email
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
def create_test_user(db_session, request):
    """Create a test user in the database with a unique email."""
    # Generate a unique email based on test name
    unique_id = str(uuid.uuid4())[:8]
    test_name = request.node.name if hasattr(request, "node") else "unknown"
    unique_email = f"test_{test_name}_{unique_id}@example.com"
    
    # Check if user already exists (for session-scoped db_session)
    existing_user = get_user_by_email(db_session, unique_email)
    if existing_user:
        logger.info(f"User with email {unique_email} already exists, using existing user")
        return existing_user
    
    logger.info(f"Creating new test user with email {unique_email}")
    db_user = User(
        email=unique_email,
        password_hash=get_password_hash("testpassword"),
        first_name="Test",
        last_name="User",
        phone_number="1234567890",
        role=UserRole.CUSTOMER,
        is_active=True
    )
    db_session.add(db_user)
    db_session.commit()
    db_session.refresh(db_user)
    
    # For debugging, explicitly query for the user we just created
    queried_user = get_user_by_email(db_session, unique_email)
    logger.info(f"Verified user in DB - email: {queried_user.email}, id: {queried_user.id}")
    
    # Clean up function for the fixture
    def cleanup():
        try:
            # Only perform cleanup if we created a new user
            if not existing_user:
                logger.info(f"Cleaning up test user {unique_email}")
                # Don't actually delete, just inactivate to not lose the FK relationships
                db_user.is_active = False
                db_session.commit()
        except Exception as e:
            logger.error(f"Error cleaning up test user: {e}")
            db_session.rollback()
    
    request.addfinalizer(cleanup)
    return db_user

def test_get_user_me(test_client, create_test_user):
    """Test getting current user profile."""
    # Override the get_current_user dependency with our test user
    original_dependency = app.dependency_overrides.get(get_current_user)
    app.dependency_overrides[get_current_user] = get_user_override(create_test_user)
    
    try:
        # Use the /users/me endpoint
        response = test_client.get("/api/v1/users/me")
        
        # Check the response
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == create_test_user.email
        assert data["first_name"] == "Test"
        assert data["last_name"] == "User"
        assert data["phone_number"] == "1234567890"
        assert data["role"] == "CUSTOMER"
    finally:
        # Restore the original dependency (or clear if none)
        if original_dependency:
            app.dependency_overrides[get_current_user] = original_dependency
        else:
            app.dependency_overrides.pop(get_current_user, None)

def test_update_user_me(test_client, create_test_user, db_session):
    """Test updating current user profile."""
    # Override the get_current_user dependency with our test user
    original_dependency = app.dependency_overrides.get(get_current_user)
    app.dependency_overrides[get_current_user] = get_user_override(create_test_user)
    
    try:
        # Update user profile data
        update_data = {
            "first_name": "Updated",
            "last_name": "Name",
            "phone_number": "9876543210"
        }
        
        # Send PATCH request
        response = test_client.patch("/api/v1/users/me", json=update_data)
        
        # Check the response
        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "Updated"
        assert data["last_name"] == "Name"
        assert data["phone_number"] == "9876543210"
        assert data["email"] == create_test_user.email  # Email should remain unchanged
        
        # Verify the database was updated
        db_session.refresh(create_test_user)
        assert create_test_user.first_name == "Updated"
        assert create_test_user.last_name == "Name"
        assert create_test_user.phone_number == "9876543210"
    finally:
        # Restore the original dependency (or clear if none)
        if original_dependency:
            app.dependency_overrides[get_current_user] = original_dependency
        else:
            app.dependency_overrides.pop(get_current_user, None)

def test_update_user_me_email(test_client, create_test_user, db_session):
    """Test updating user email."""
    # Override the get_current_user dependency with our test user
    original_dependency = app.dependency_overrides.get(get_current_user)
    app.dependency_overrides[get_current_user] = get_user_override(create_test_user)
    
    try:
        # Create a new unique email
        new_email = f"updated_{uuid.uuid4()}@example.com"
        
        # Update only the email
        update_data = {
            "email": new_email
        }
        
        # Send PATCH request
        response = test_client.patch("/api/v1/users/me", json=update_data)
        
        # Check the response
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == new_email
        
        # Verify the database was updated
        db_session.refresh(create_test_user)
        assert create_test_user.email == new_email
    finally:
        # Restore the original dependency (or clear if none)
        if original_dependency:
            app.dependency_overrides[get_current_user] = original_dependency
        else:
            app.dependency_overrides.pop(get_current_user, None)

def test_update_user_me_password(test_client, create_test_user, db_session):
    """Test updating user password."""
    # Override the get_current_user dependency with our test user
    original_dependency = app.dependency_overrides.get(get_current_user)
    app.dependency_overrides[get_current_user] = get_user_override(create_test_user)
    
    # Store the original password hash
    original_hash = create_test_user.password_hash
    
    try:
        # Update only the password
        update_data = {
            "password": "newpassword123"
        }
        
        # Send PATCH request
        response = test_client.patch("/api/v1/users/me", json=update_data)
        
        # Check the response
        assert response.status_code == 200
        
        # Verify the password hash was updated in the database
        db_session.refresh(create_test_user)
        assert create_test_user.password_hash != original_hash
    finally:
        # Restore the original dependency (or clear if none)
        if original_dependency:
            app.dependency_overrides[get_current_user] = original_dependency
        else:
            app.dependency_overrides.pop(get_current_user, None)

def test_update_user_me_invalid_role(test_client, create_test_user):
    """Test that a normal user cannot update their role."""
    # Override the get_current_user dependency with our test user
    original_dependency = app.dependency_overrides.get(get_current_user)
    app.dependency_overrides[get_current_user] = get_user_override(create_test_user)
    
    try:
        # Try to update the role to ADMIN
        update_data = {
            "role": "ADMIN"
        }
        
        # Send PATCH request
        response = test_client.patch("/api/v1/users/me", json=update_data)
        
        # Should be forbidden
        assert response.status_code == 403
        assert "Role cannot be changed by the user" in response.text
    finally:
        # Restore the original dependency (or clear if none)
        if original_dependency:
            app.dependency_overrides[get_current_user] = original_dependency
        else:
            app.dependency_overrides.pop(get_current_user, None) 