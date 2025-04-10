"""
Tests for pricing configuration endpoints.
"""
import pytest
import uuid
from fastapi import status
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from wellfix_api.models.enums import RepairType
from wellfix_api.models.user import UserRole, User
from wellfix_api.models.pricing import PricingConfig
from wellfix_api.crud import pricing as pricing_crud
from wellfix_api.core.dependencies import get_current_user
from wellfix_api.core.db import get_db
from wellfix_api.main import app
from tests.utils.test_db import override_get_db, TestingSessionLocal


def override_get_current_user_admin(user: User):
    """
    Override the get_current_user dependency for admin users.
    """
    def get_current_user_override():
        return user
    return get_current_user_override


def override_get_current_user_customer(user: User):
    """
    Override the get_current_user dependency for customer users.
    """
    def get_current_user_override():
        return user
    return get_current_user_override


@pytest.fixture
def test_client():
    """
    Create a test client for pricing endpoint tests.
    """
    # Override the database dependency
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as client:
        yield client
    
    # Clean up after the test
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
def admin_token(test_client, admin_user):
    """
    Setup admin authentication by overriding the dependency.
    """
    app.dependency_overrides[get_current_user] = override_get_current_user_admin(admin_user)
    return "fake_admin_token"  # The token doesn't matter since we override the dependency


@pytest.fixture
def customer_token(test_client, customer_user):
    """
    Setup customer authentication by overriding the dependency.
    """
    app.dependency_overrides[get_current_user] = override_get_current_user_customer(customer_user)
    return "fake_customer_token"  # The token doesn't matter since we override the dependency


@pytest.fixture
def test_pricing_config(db: Session, admin_user):
    """Create a test pricing configuration."""
    pricing_config = PricingConfig(
        repair_type=RepairType.HARDWARE.value,
        item_name="Test Motherboard Replacement",
        description="Replacement of damaged motherboard",
        base_price=150.00,
        is_active=True,
        updated_by_admin_id=admin_user.id
    )
    db.add(pricing_config)
    db.commit()
    db.refresh(pricing_config)
    
    yield pricing_config
    
    # Check if the config still exists before attempting to delete it
    existing_config = db.query(PricingConfig).filter(PricingConfig.id == pricing_config.id).first()
    if existing_config:
        db.delete(existing_config)
        # Set confirm_deleted_rows=False to suppress the warning
        db.commit()


@pytest.fixture
def pricing_config_create_data():
    """Return data for creating a pricing configuration."""
    return {
        "repair_type": RepairType.SOFTWARE.value,
        "item_name": "OS Reinstallation",
        "description": "Reinstallation of operating system",
        "base_price": 75.50,
        "is_active": True
    }


@pytest.fixture
def pricing_config_update_data():
    """Return data for updating a pricing configuration."""
    return {
        "item_name": "Updated Motherboard Replacement",
        "base_price": 175.00
    }


def test_list_pricing_configs(test_client, admin_token, test_pricing_config):
    """Test listing pricing configurations."""
    # Print response for debugging
    response = test_client.get(
        "/api/v1/admin/pricing/pricing",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    print(f"Response status: {response.status_code}")
    print(f"Response body: {response.text}")
    
    # Print all routes in the app
    print("\nAll available routes:")
    from fastapi.routing import APIRoute
    for route in test_client.app.routes:
        if isinstance(route, APIRoute):
            print(f"{route.methods} {route.path}")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total"] > 0
    assert len(data["items"]) > 0
    assert any(item["id"] == test_pricing_config.id for item in data["items"])


def test_list_pricing_configs_with_filters(test_client, admin_token, test_pricing_config):
    """Test listing pricing configurations with filters."""
    response = test_client.get(
        f"/api/v1/admin/pricing/pricing?repair_type={RepairType.HARDWARE.value}&is_active=true",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total"] > 0
    assert all(item["repair_type"] == RepairType.HARDWARE.value for item in data["items"])
    assert all(item["is_active"] for item in data["items"])


def test_get_pricing_config(test_client, admin_token, test_pricing_config):
    """Test getting a specific pricing configuration."""
    response = test_client.get(
        f"/api/v1/admin/pricing/pricing/{test_pricing_config.id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == test_pricing_config.id
    assert data["repair_type"] == test_pricing_config.repair_type
    assert data["item_name"] == test_pricing_config.item_name
    assert data["base_price"] == test_pricing_config.base_price


def test_get_pricing_config_not_found(test_client, admin_token):
    """Test getting a non-existent pricing configuration."""
    response = test_client.get(
        "/api/v1/admin/pricing/pricing/99999",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_create_pricing_config(test_client, admin_token, pricing_config_create_data):
    """Test creating a pricing configuration."""
    response = test_client.post(
        "/api/v1/admin/pricing/pricing",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=pricing_config_create_data
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["repair_type"] == pricing_config_create_data["repair_type"]
    assert data["item_name"] == pricing_config_create_data["item_name"]
    assert data["base_price"] == pricing_config_create_data["base_price"]
    assert "id" in data


def test_create_pricing_config_invalid_data(test_client, admin_token):
    """Test creating a pricing configuration with invalid data."""
    # Missing required fields
    response = test_client.post(
        "/api/v1/admin/pricing/pricing",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"item_name": "Test"}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # Invalid repair type
    response = test_client.post(
        "/api/v1/admin/pricing/pricing",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "repair_type": "INVALID_TYPE",
            "item_name": "Test Item",
            "base_price": 100.00
        }
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # Negative price
    response = test_client.post(
        "/api/v1/admin/pricing/pricing",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "repair_type": RepairType.HARDWARE.value,
            "item_name": "Test Item",
            "base_price": -50.00
        }
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_create_pricing_config_unauthorized(test_client, customer_token, pricing_config_create_data):
    """Test creating a pricing configuration as a non-admin user."""
    response = test_client.post(
        "/api/v1/admin/pricing/pricing",
        headers={"Authorization": f"Bearer {customer_token}"},
        json=pricing_config_create_data
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_update_pricing_config(test_client, admin_token, test_pricing_config, pricing_config_update_data):
    """Test updating a pricing configuration."""
    response = test_client.patch(
        f"/api/v1/admin/pricing/pricing/{test_pricing_config.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=pricing_config_update_data
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == test_pricing_config.id
    assert data["item_name"] == pricing_config_update_data["item_name"]
    assert data["base_price"] == pricing_config_update_data["base_price"]
    # Other fields should remain unchanged
    assert data["repair_type"] == test_pricing_config.repair_type
    assert data["is_active"] == test_pricing_config.is_active


def test_update_pricing_config_not_found(test_client, admin_token, pricing_config_update_data):
    """Test updating a non-existent pricing configuration."""
    response = test_client.patch(
        "/api/v1/admin/pricing/pricing/99999",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=pricing_config_update_data
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_pricing_config_unauthorized(test_client, customer_token, test_pricing_config, pricing_config_update_data):
    """Test updating a pricing configuration as a non-admin user."""
    response = test_client.patch(
        f"/api/v1/admin/pricing/pricing/{test_pricing_config.id}",
        headers={"Authorization": f"Bearer {customer_token}"},
        json=pricing_config_update_data
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_delete_pricing_config(test_client, admin_token, test_pricing_config):
    """Test deleting a pricing configuration."""
    response = test_client.delete(
        f"/api/v1/admin/pricing/pricing/{test_pricing_config.id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verify it's actually deleted
    response = test_client.get(
        f"/api/v1/admin/pricing/pricing/{test_pricing_config.id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_pricing_config_not_found(test_client, admin_token):
    """Test deleting a non-existent pricing configuration."""
    response = test_client.delete(
        "/api/v1/admin/pricing/pricing/99999",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_pricing_config_unauthorized(test_client, customer_token, test_pricing_config):
    """Test deleting a pricing configuration as a non-admin user."""
    response = test_client.delete(
        f"/api/v1/admin/pricing/pricing/{test_pricing_config.id}",
        headers={"Authorization": f"Bearer {customer_token}"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN 