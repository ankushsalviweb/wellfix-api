import uuid
import pytest
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from wellfix_api.models.service_area import ServiceableArea
from wellfix_api.models.user import User, UserRole

@pytest.fixture
def test_admin(db_session: Session):
    """Create a test admin user for service area tests."""
    user_id = str(uuid.uuid4())
    admin = User(
        id=user_id,
        email=f"test_admin_{user_id[:8]}@example.com",
        password_hash="dummy_hash",
        first_name="Test",
        last_name="Admin",
        phone_number="0000000000",
        role=UserRole.ADMIN.value,
        is_active=True
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    return admin

def test_create_service_area(db_session: Session, test_admin: User):
    """Test creating a serviceable area with admin association."""
    # Create a serviceable area
    pincode = "123456"
    service_area = ServiceableArea(
        pincode=pincode,
        is_active=True,
        added_by_admin_id=test_admin.id
    )
    db_session.add(service_area)
    db_session.commit()
    db_session.refresh(service_area)
    
    # Test that the service area was created with correct attributes
    assert service_area.pincode == pincode
    assert service_area.is_active is True
    assert service_area.added_by_admin_id == test_admin.id
    assert service_area.created_at is not None
    
    # Test the relationship with admin
    assert service_area.created_by.id == test_admin.id
    assert service_area.created_by.email == test_admin.email
    assert service_area.created_by.role == UserRole.ADMIN.value

def test_admin_service_areas_relationship(db_session: Session, test_admin: User):
    """Test the relationship between admin and managed service areas."""
    # Create multiple serviceable areas managed by the same admin
    pincodes = ["100001", "100002", "100003"]
    
    for pincode in pincodes:
        service_area = ServiceableArea(
            pincode=pincode,
            is_active=True,
            added_by_admin_id=test_admin.id
        )
        db_session.add(service_area)
    
    db_session.commit()
    
    # Refresh the admin to get the updated relationships
    db_session.refresh(test_admin)
    
    # Test that the admin is associated with all the areas
    managed_areas = test_admin.managed_areas
    assert len(managed_areas) == len(pincodes)
    
    # Check that all pincodes are in the admin's managed areas
    managed_pincodes = [area.pincode for area in managed_areas]
    for pincode in pincodes:
        assert pincode in managed_pincodes

def test_service_area_deactivation(db_session: Session, test_admin: User):
    """Test deactivating a serviceable area."""
    # Create an active serviceable area
    pincode = "200001"
    service_area = ServiceableArea(
        pincode=pincode,
        is_active=True,
        added_by_admin_id=test_admin.id
    )
    db_session.add(service_area)
    db_session.commit()
    db_session.refresh(service_area)
    
    # Deactivate the area
    service_area.is_active = False
    db_session.commit()
    db_session.refresh(service_area)
    
    # Test that the service area was deactivated
    assert service_area.is_active is False
    
    # Query the area to make sure it's still in the database
    deactivated_area = db_session.query(ServiceableArea).filter(
        ServiceableArea.pincode == pincode
    ).first()
    
    assert deactivated_area is not None
    assert deactivated_area.is_active is False 