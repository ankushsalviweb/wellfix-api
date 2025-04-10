"""
Integration tests for Admin Pricing API endpoints.
"""

from typing import Dict, Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from wellfix_api.main import app
from wellfix_api.core.config import settings
from wellfix_api.core.dependencies import get_current_user, require_admin
from wellfix_api.models.user import User, UserRole
from wellfix_api.crud import crud_pricing
from wellfix_api.schemas.pricing import PricingConfigCreate


@pytest.fixture(scope="function")
def test_admin_user(db_session: Session) -> User:
    """Create a test admin user."""
    import uuid
    from datetime import datetime
    
    # Check if admin exists
    admin = db_session.query(User).filter(User.email == "testadmin@example.com").first()
    if admin:
        return admin
    
    # Create a test admin user with fixed UUID
    admin = User(
        id="33333333-3333-3333-3333-333333333333",
        email="testadmin@example.com",
        password_hash="hashed_password",
        first_name="Test",
        last_name="Admin",
        phone_number="1234567890",
        role=UserRole.ADMIN,
        is_active=True,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    return admin


@pytest.fixture(scope="function")
def admin_access(test_admin_user: User):
    """Override authentication dependencies to return test admin user."""
    
    def override_get_current_user():
        return test_admin_user
        
    def override_require_admin():
        return test_admin_user
        
    # Set up dependency overrides
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[require_admin] = override_require_admin
    
    yield
    
    # Clean up
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_customer_user(db_session: Session) -> User:
    """Create a test customer user."""
    import uuid
    from datetime import datetime
    
    # Check if customer exists
    customer = db_session.query(User).filter(User.email == "testcustomer@example.com").first()
    if customer:
        return customer
    
    # Create a test customer user with fixed UUID
    customer = User(
        id="44444444-4444-4444-4444-444444444444",
        email="testcustomer@example.com",
        password_hash="hashed_password",
        first_name="Test",
        last_name="Customer",
        phone_number="1234567891",
        role=UserRole.CUSTOMER,
        is_active=True,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    db_session.add(customer)
    db_session.commit()
    db_session.refresh(customer)
    return customer


@pytest.fixture(scope="function")
def customer_access(test_customer_user: User):
    """Override authentication dependencies to return test customer user."""
    
    def override_get_current_user():
        return test_customer_user
    
    # Set up dependency override
    app.dependency_overrides[get_current_user] = override_get_current_user
    
    yield
    
    # Clean up
    app.dependency_overrides.clear()


def create_test_pricing_config(db_session: Session) -> Dict[str, Any]:
    """Helper to create a test pricing configuration."""
    config_in = PricingConfigCreate(
        name="Test Standard Pricing",
        description="Standard pricing for repair services",
        base_diagnostic_fee=50.0,
        base_onsite_fee=25.0,
        hourly_rate_hardware=75.0,
        hourly_rate_software=65.0,
        hourly_rate_network=70.0,
        is_default=True
    )
    
    config = crud_pricing.create_pricing_config(db=db_session, config_in=config_in)
    
    return {
        "id": config.id,
        "name": config.name,
        "base_diagnostic_fee": config.base_diagnostic_fee
    }


def test_create_pricing_config(client: TestClient, admin_access, db_session: Session) -> None:
    """Test creating a pricing configuration as admin."""
    data = {
        "name": "New Pricing Config",
        "description": "New pricing for repair services",
        "base_diagnostic_fee": 60.0,
        "base_onsite_fee": 30.0,
        "hourly_rate_hardware": 80.0,
        "hourly_rate_software": 70.0,
        "hourly_rate_network": 75.0,
        "is_default": False
    }
    
    response = client.post(
        f"{settings.API_V1_STR}/admin/pricing/",
        json=data
    )
    
    assert response.status_code == 201
    content = response.json()
    assert content["name"] == "New Pricing Config"
    assert content["base_diagnostic_fee"] == 60.0
    assert content["is_default"] is False
    assert "id" in content


def test_create_pricing_config_unauthorized(client: TestClient, customer_access) -> None:
    """Test creating a pricing configuration as non-admin (should fail)."""
    data = {
        "name": "New Pricing Config",
        "description": "New pricing for repair services",
        "base_diagnostic_fee": 60.0,
        "base_onsite_fee": 30.0,
        "hourly_rate_hardware": 80.0,
        "hourly_rate_software": 70.0,
        "hourly_rate_network": 75.0,
        "is_default": False
    }
    
    response = client.post(
        f"{settings.API_V1_STR}/admin/pricing/",
        json=data
    )
    
    assert response.status_code == 403  # Forbidden


def test_read_pricing_configs(client: TestClient, admin_access, db_session: Session) -> None:
    """Test reading all pricing configurations as admin."""
    # Create a test config
    create_test_pricing_config(db_session)
    
    response = client.get(
        f"{settings.API_V1_STR}/admin/pricing/"
    )
    
    assert response.status_code == 200
    content = response.json()
    assert "count" in content
    assert "pricing_configs" in content
    assert content["count"] > 0
    assert len(content["pricing_configs"]) > 0


def test_read_pricing_config(client: TestClient, admin_access, db_session: Session) -> None:
    """Test reading a specific pricing configuration as admin."""
    # Create a test config
    config = create_test_pricing_config(db_session)
    
    response = client.get(
        f"{settings.API_V1_STR}/admin/pricing/{config['id']}"
    )
    
    assert response.status_code == 200
    content = response.json()
    assert content["id"] == config["id"]
    assert content["name"] == config["name"]


def test_read_pricing_config_not_found(client: TestClient, admin_access) -> None:
    """Test reading a non-existent pricing configuration."""
    response = client.get(
        f"{settings.API_V1_STR}/admin/pricing/9999"
    )
    
    assert response.status_code == 404


def test_update_pricing_config(client: TestClient, admin_access, db_session: Session) -> None:
    """Test updating a pricing configuration as admin."""
    # Create a test config
    config = create_test_pricing_config(db_session)
    
    update_data = {
        "name": "Updated Pricing Config",
        "base_diagnostic_fee": 65.0
    }
    
    response = client.patch(
        f"{settings.API_V1_STR}/admin/pricing/{config['id']}",
        json=update_data
    )
    
    assert response.status_code == 200
    content = response.json()
    assert content["id"] == config["id"]
    assert content["name"] == "Updated Pricing Config"
    assert content["base_diagnostic_fee"] == 65.0


def test_update_pricing_config_not_found(client: TestClient, admin_access) -> None:
    """Test updating a non-existent pricing configuration."""
    update_data = {
        "name": "Updated Pricing Config",
        "base_diagnostic_fee": 65.0
    }
    
    response = client.patch(
        f"{settings.API_V1_STR}/admin/pricing/9999",
        json=update_data
    )
    
    assert response.status_code == 404


def test_delete_pricing_config(client: TestClient, admin_access, db_session: Session) -> None:
    """Test deleting a pricing configuration as admin."""
    # Create a test config
    config = create_test_pricing_config(db_session)
    
    response = client.delete(
        f"{settings.API_V1_STR}/admin/pricing/{config['id']}"
    )
    
    assert response.status_code == 204
    
    # Verify it's deleted
    response = client.get(
        f"{settings.API_V1_STR}/admin/pricing/{config['id']}"
    )
    
    assert response.status_code == 404


def test_delete_pricing_config_not_found(client: TestClient, admin_access) -> None:
    """Test deleting a non-existent pricing configuration."""
    response = client.delete(
        f"{settings.API_V1_STR}/admin/pricing/9999"
    )
    
    assert response.status_code == 404 