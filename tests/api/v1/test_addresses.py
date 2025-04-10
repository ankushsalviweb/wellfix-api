import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid import uuid4

from wellfix_api.main import app
from wellfix_api.models.user import User
from wellfix_api.models.address import Address
from wellfix_api.models.service_area import ServiceableArea

@pytest.fixture
def customer_token(db: Session):
    """Create a customer user and return a token for authentication."""
    user = User(
        id=str(uuid4()),
        email="customer@example.com",
        password_hash="hashed_password",
        first_name="Test",
        last_name="Customer",
        phone_number="1234567890",
        role="CUSTOMER",
        is_active=True
    )
    db.add(user)
    db.commit()
    
    # Mock authentication token
    return f"Bearer {user.id}"  # In a real test, would use a proper JWT

@pytest.fixture
def test_address(db: Session, customer_token):
    """Create a test address."""
    # Extract user_id from token
    user_id = customer_token.split(" ")[1]
    
    address = Address(
        id=str(uuid4()),
        user_id=user_id,
        street_address="123 Test St",
        city="Test City",
        state="Test State",
        pincode="12345",
        is_default=True
    )
    db.add(address)
    db.commit()
    return address

@pytest.fixture
def serviceable_area(db: Session):
    """Create a serviceable area for testing."""
    area = ServiceableArea(
        pincode="12345",
        is_active=True,
        added_by_admin_id="admin-id"
    )
    db.add(area)
    
    # Add another area that's not active
    inactive_area = ServiceableArea(
        pincode="67890",
        is_active=False,
        added_by_admin_id="admin-id"
    )
    db.add(inactive_area)
    
    db.commit()
    return area

def test_list_addresses(client: TestClient, customer_token, test_address):
    """Test the GET /addresses endpoint."""
    response = client.get(
        "/api/v1/addresses",
        headers={"Authorization": customer_token}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] > 0
    assert len(data["items"]) == data["total"]
    assert data["items"][0]["street_address"] == test_address.street_address

def test_get_address(client: TestClient, customer_token, test_address):
    """Test the GET /addresses/{address_id} endpoint."""
    response = client.get(
        f"/api/v1/addresses/{test_address.id}",
        headers={"Authorization": customer_token}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_address.id
    assert data["street_address"] == test_address.street_address

def test_get_address_not_found(client: TestClient, customer_token):
    """Test the GET /addresses/{address_id} endpoint with a non-existent address."""
    response = client.get(
        f"/api/v1/addresses/{uuid4()}",
        headers={"Authorization": customer_token}
    )
    
    assert response.status_code == 404

def test_create_address_success(client: TestClient, customer_token, serviceable_area):
    """Test the POST /addresses endpoint with a valid address."""
    response = client.post(
        "/api/v1/addresses",
        headers={"Authorization": customer_token},
        json={
            "street_address": "456 New St",
            "city": "New City",
            "state": "New State",
            "pincode": "12345",  # Serviceable pincode
            "is_default": False
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["street_address"] == "456 New St"
    assert data["pincode"] == "12345"

def test_create_address_non_serviceable(client: TestClient, customer_token):
    """Test the POST /addresses endpoint with a non-serviceable pincode."""
    response = client.post(
        "/api/v1/addresses",
        headers={"Authorization": customer_token},
        json={
            "street_address": "789 Bad St",
            "city": "Bad City",
            "state": "Bad State",
            "pincode": "99999",  # Non-serviceable pincode
            "is_default": False
        }
    )
    
    assert response.status_code == 422

def test_create_address_inactive_area(client: TestClient, customer_token, serviceable_area):
    """Test the POST /addresses endpoint with an inactive serviceable area."""
    response = client.post(
        "/api/v1/addresses",
        headers={"Authorization": customer_token},
        json={
            "street_address": "789 Inactive St",
            "city": "Inactive City",
            "state": "Inactive State",
            "pincode": "67890",  # Inactive serviceable area
            "is_default": False
        }
    )
    
    assert response.status_code == 422

def test_update_address(client: TestClient, customer_token, test_address, serviceable_area):
    """Test the PATCH /addresses/{address_id} endpoint."""
    response = client.patch(
        f"/api/v1/addresses/{test_address.id}",
        headers={"Authorization": customer_token},
        json={
            "street_address": "Updated Street"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["street_address"] == "Updated Street"
    assert data["city"] == test_address.city  # Unchanged field

def test_update_address_pincode(client: TestClient, customer_token, test_address, serviceable_area):
    """Test updating the pincode of an address."""
    # Try to update to a non-serviceable pincode
    response = client.patch(
        f"/api/v1/addresses/{test_address.id}",
        headers={"Authorization": customer_token},
        json={
            "pincode": "99999"  # Non-serviceable pincode
        }
    )
    
    assert response.status_code == 422
    
    # Try to update to an inactive serviceable area
    response = client.patch(
        f"/api/v1/addresses/{test_address.id}",
        headers={"Authorization": customer_token},
        json={
            "pincode": "67890"  # Inactive serviceable area
        }
    )
    
    assert response.status_code == 422

def test_delete_address(client: TestClient, customer_token, test_address):
    """Test the DELETE /addresses/{address_id} endpoint."""
    response = client.delete(
        f"/api/v1/addresses/{test_address.id}",
        headers={"Authorization": customer_token}
    )
    
    assert response.status_code == 204
    
    # Verify the address was deleted
    response = client.get(
        f"/api/v1/addresses/{test_address.id}",
        headers={"Authorization": customer_token}
    )
    
    assert response.status_code == 404 