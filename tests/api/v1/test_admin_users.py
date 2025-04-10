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
def admin_user(db_session, request):
    """Create an admin user in the database."""
    # Generate a unique email
    unique_id = str(uuid.uuid4())[:8]
    admin_email = f"admin_{unique_id}@example.com"
    
    # Check if user already exists
    existing_user = get_user_by_email(db_session, admin_email)
    if existing_user:
        logger.info(f"Admin user with email {admin_email} already exists, using existing user")
        return existing_user
    
    logger.info(f"Creating new admin user with email {admin_email}")
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
        try:
            # Only perform cleanup if we created a new user
            if not existing_user:
                logger.info(f"Cleaning up admin user {admin_email}")
                admin.is_active = False
                db_session.commit()
        except Exception as e:
            logger.error(f"Error cleaning up admin user: {e}")
            db_session.rollback()
    
    request.addfinalizer(cleanup)
    return admin

@pytest.fixture(scope="function")
def normal_user(db_session, request):
    """Create a normal user in the database."""
    # Generate a unique email
    unique_id = str(uuid.uuid4())[:8]
    user_email = f"user_{unique_id}@example.com"
    
    # Check if user already exists
    existing_user = get_user_by_email(db_session, user_email)
    if existing_user:
        logger.info(f"User with email {user_email} already exists, using existing user")
        return existing_user
    
    logger.info(f"Creating new user with email {user_email}")
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
        try:
            # Only perform cleanup if we created a new user
            if not existing_user:
                logger.info(f"Cleaning up user {user_email}")
                user.is_active = False
                db_session.commit()
        except Exception as e:
            logger.error(f"Error cleaning up user: {e}")
            db_session.rollback()
    
    request.addfinalizer(cleanup)
    return user

def test_get_all_users_admin(test_client, admin_user, normal_user):
    """Test that an admin can retrieve all users."""
    # Override the get_current_user dependency with our admin user
    original_dependency = app.dependency_overrides.get(get_current_user)
    app.dependency_overrides[get_current_user] = get_user_override(admin_user)
    
    try:
        # Call the admin endpoint
        response = test_client.get("/api/v1/admin/users")
        
        # Check the response
        assert response.status_code == 200
        data = response.json()
        
        # Response could be a list or paginated object - handle both cases
        if isinstance(data, list):
            users = data
        elif isinstance(data, dict) and "items" in data:
            users = data["items"]
        else:
            assert False, f"Unexpected response format: {data}"
        
        # Ensure our test users are in the response
        user_ids = [user["id"] for user in users]
        assert str(admin_user.id) in user_ids
        assert str(normal_user.id) in user_ids
    finally:
        # Restore the original dependency (or clear if none)
        if original_dependency:
            app.dependency_overrides[get_current_user] = original_dependency
        else:
            app.dependency_overrides.pop(get_current_user, None)

def test_get_all_users_non_admin(test_client, normal_user):
    """Test that a non-admin cannot retrieve all users."""
    # Override the get_current_user dependency with our normal user
    original_dependency = app.dependency_overrides.get(get_current_user)
    app.dependency_overrides[get_current_user] = get_user_override(normal_user)
    
    try:
        # Call the admin endpoint
        response = test_client.get("/api/v1/admin/users")
        
        # Check the response - should be forbidden
        assert response.status_code == 403
        assert "This action requires admin privileges" in response.text
    finally:
        # Restore the original dependency (or clear if none)
        if original_dependency:
            app.dependency_overrides[get_current_user] = original_dependency
        else:
            app.dependency_overrides.pop(get_current_user, None)

def test_get_user_by_id_admin(test_client, admin_user, normal_user):
    """Test that an admin can retrieve a user by ID."""
    # Override the get_current_user dependency with our admin user
    original_dependency = app.dependency_overrides.get(get_current_user)
    app.dependency_overrides[get_current_user] = get_user_override(admin_user)
    
    try:
        # Call the admin endpoint
        response = test_client.get(f"/api/v1/admin/users/{normal_user.id}")
        
        # Check the response
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(normal_user.id)
        assert data["email"] == normal_user.email
        assert data["first_name"] == normal_user.first_name
        assert data["last_name"] == normal_user.last_name
    finally:
        # Restore the original dependency (or clear if none)
        if original_dependency:
            app.dependency_overrides[get_current_user] = original_dependency
        else:
            app.dependency_overrides.pop(get_current_user, None)

def test_get_user_by_id_non_admin(test_client, normal_user, admin_user):
    """Test that a non-admin cannot retrieve a user by ID."""
    # Override the get_current_user dependency with our normal user
    original_dependency = app.dependency_overrides.get(get_current_user)
    app.dependency_overrides[get_current_user] = get_user_override(normal_user)
    
    try:
        # Call the admin endpoint
        response = test_client.get(f"/api/v1/admin/users/{admin_user.id}")
        
        # Check the response - should be forbidden
        assert response.status_code == 403
        assert "This action requires admin privileges" in response.text
    finally:
        # Restore the original dependency (or clear if none)
        if original_dependency:
            app.dependency_overrides[get_current_user] = original_dependency
        else:
            app.dependency_overrides.pop(get_current_user, None)

def test_create_user_admin(test_client, admin_user, db_session):
    """Test that an admin can create a new user."""
    # Override the get_current_user dependency with our admin user
    original_dependency = app.dependency_overrides.get(get_current_user)
    app.dependency_overrides[get_current_user] = get_user_override(admin_user)
    
    try:
        # Create a new user data
        new_user_email = f"newuser_{uuid.uuid4()}@example.com"
        new_user_data = {
            "email": new_user_email,
            "password": "newpassword",
            "first_name": "New",
            "last_name": "User",
            "phone_number": "2222222222",
            "role": "ENGINEER"  # Testing engineer role creation
        }
        
        # Call the admin endpoint
        response = test_client.post("/api/v1/admin/users", json=new_user_data)
        
        # Check the response
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == new_user_email
        assert data["first_name"] == "New"
        assert data["last_name"] == "User"
        assert data["role"] == "ENGINEER"
        
        # Verify in the database
        created_user = get_user_by_email(db_session, new_user_email)
        assert created_user is not None
        assert created_user.email == new_user_email
        assert created_user.role == UserRole.ENGINEER
    finally:
        # Restore the original dependency (or clear if none)
        if original_dependency:
            app.dependency_overrides[get_current_user] = original_dependency
        else:
            app.dependency_overrides.pop(get_current_user, None)

def test_create_user_non_admin(test_client, normal_user):
    """Test that a non-admin cannot create a new user."""
    # Override the get_current_user dependency with our normal user
    original_dependency = app.dependency_overrides.get(get_current_user)
    app.dependency_overrides[get_current_user] = get_user_override(normal_user)
    
    try:
        # Create a new user data
        new_user_data = {
            "email": f"newuser_{uuid.uuid4()}@example.com",
            "password": "newpassword",
            "first_name": "New",
            "last_name": "User",
            "phone_number": "2222222222",
            "role": "ENGINEER"
        }
        
        # Call the admin endpoint
        response = test_client.post("/api/v1/admin/users", json=new_user_data)
        
        # Check the response - should be forbidden
        assert response.status_code == 403
        assert "This action requires admin privileges" in response.text
    finally:
        # Restore the original dependency (or clear if none)
        if original_dependency:
            app.dependency_overrides[get_current_user] = original_dependency
        else:
            app.dependency_overrides.pop(get_current_user, None)

def test_update_user_admin(test_client, admin_user, normal_user, db_session):
    """Test that an admin can update a user."""
    # Override the get_current_user dependency with our admin user
    original_dependency = app.dependency_overrides.get(get_current_user)
    app.dependency_overrides[get_current_user] = get_user_override(admin_user)
    
    try:
        # Update data
        update_data = {
            "first_name": "Updated",
            "last_name": "Name",
            "role": "ENGINEER"  # Change role
        }
        
        # Call the admin endpoint
        response = test_client.patch(f"/api/v1/admin/users/{normal_user.id}", json=update_data)
        
        # Check the response
        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "Updated"
        assert data["last_name"] == "Name"
        assert data["role"] == "ENGINEER"
        
        # Verify in the database
        db_session.refresh(normal_user)
        assert normal_user.first_name == "Updated"
        assert normal_user.last_name == "Name"
        assert normal_user.role == UserRole.ENGINEER
    finally:
        # Restore the original dependency (or clear if none)
        if original_dependency:
            app.dependency_overrides[get_current_user] = original_dependency
        else:
            app.dependency_overrides.pop(get_current_user, None)

def test_update_user_non_admin(test_client, normal_user, admin_user):
    """Test that a non-admin cannot update a user through admin endpoints."""
    # Override the get_current_user dependency with our normal user
    original_dependency = app.dependency_overrides.get(get_current_user)
    app.dependency_overrides[get_current_user] = get_user_override(normal_user)
    
    try:
        # Update data
        update_data = {
            "first_name": "Hacked",
            "role": "ADMIN"  # Try to become admin
        }
        
        # Call the admin endpoint
        response = test_client.patch(f"/api/v1/admin/users/{admin_user.id}", json=update_data)
        
        # Check the response - should be forbidden
        assert response.status_code == 403
        assert "This action requires admin privileges" in response.text
    finally:
        # Restore the original dependency (or clear if none)
        if original_dependency:
            app.dependency_overrides[get_current_user] = original_dependency
        else:
            app.dependency_overrides.pop(get_current_user, None) 