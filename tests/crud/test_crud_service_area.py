import uuid
import pytest
from sqlalchemy.orm import Session

from wellfix_api.models.service_area import ServiceableArea
from wellfix_api.models.user import User, UserRole
from wellfix_api.schemas.service_area import ServiceableAreaCreate, ServiceableAreaUpdate
from wellfix_api.crud.crud_service_area import (
    get_service_area,
    get_active_service_area,
    is_pincode_serviceable,
    list_service_areas,
    create_service_area,
    update_service_area
)

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

@pytest.fixture
def test_service_areas(db_session: Session, test_admin: User):
    """Create multiple test service areas."""
    areas = []
    for i in range(5):
        # Create some active and some inactive areas
        is_active = (i % 2 == 0)
        # Use UUID to ensure uniqueness
        unique_id = str(uuid.uuid4())[:8]
        pincode = f"area_{unique_id}"

        area = ServiceableArea(
            pincode=pincode,
            is_active=is_active,
            added_by_admin_id=test_admin.id
        )
        db_session.add(area)
        areas.append(area)

    db_session.commit()
    return areas

def test_get_service_area(db_session: Session, test_service_areas: list[ServiceableArea]):
    """Test getting a service area by pincode."""
    # Get an existing area
    test_area = test_service_areas[0]
    area = get_service_area(db_session, test_area.pincode)
    
    assert area is not None
    assert area.pincode == test_area.pincode
    assert area.is_active == test_area.is_active
    assert area.added_by_admin_id == test_area.added_by_admin_id
    
    # Try to get a non-existent area
    area = get_service_area(db_session, "99999")
    assert area is None

def test_get_active_service_area(db_session: Session, test_service_areas: list[ServiceableArea]):
    """Test getting an active service area by pincode."""
    # Find an active area from test_service_areas
    active_area = next(area for area in test_service_areas if area.is_active)
    
    # Get the active area by pincode
    area = get_active_service_area(db_session, active_area.pincode)
    assert area is not None
    assert area.pincode == active_area.pincode
    assert area.is_active is True
    
    # Find an inactive area from test_service_areas
    inactive_area = next(area for area in test_service_areas if not area.is_active)
    
    # Try to get the inactive area, should return None
    area = get_active_service_area(db_session, inactive_area.pincode)
    assert area is None

def test_is_pincode_serviceable(db_session: Session, test_service_areas: list[ServiceableArea]):
    """Test checking if a pincode is serviceable."""
    # Find an active area from test_service_areas
    active_area = next(area for area in test_service_areas if area.is_active)
    
    # Check if the active area's pincode is serviceable
    is_serviceable = is_pincode_serviceable(db_session, active_area.pincode)
    assert is_serviceable is True
    
    # Find an inactive area from test_service_areas
    inactive_area = next(area for area in test_service_areas if not area.is_active)
    
    # Check if the inactive area's pincode is serviceable
    is_serviceable = is_pincode_serviceable(db_session, inactive_area.pincode)
    assert is_serviceable is False
    
    # Check a non-existent pincode
    is_serviceable = is_pincode_serviceable(db_session, "99999")
    assert is_serviceable is False

def test_list_service_areas(db_session: Session, test_service_areas: list[ServiceableArea]):
    """Test listing service areas with pagination."""
    # Count how many areas exist in total (there might be leftovers from other tests)
    total_areas_in_db = db_session.query(ServiceableArea).count()
    
    # Test listing all areas
    areas, total = list_service_areas(db_session)
    assert len(areas) == total_areas_in_db
    assert total == total_areas_in_db
    
    # Ensure our test areas are included in the results
    area_pincodes = [area.pincode for area in areas]
    for test_area in test_service_areas:
        assert test_area.pincode in area_pincodes
    
    # Test listing only active areas
    active_areas, total_active = list_service_areas(db_session, active_only=True)
    active_count = db_session.query(ServiceableArea).filter(ServiceableArea.is_active == True).count()
    assert len(active_areas) == active_count
    assert total_active == active_count
    
    # Test pagination
    areas_page1, total = list_service_areas(db_session, skip=0, limit=2)
    assert len(areas_page1) == 2
    assert total == total_areas_in_db
    
    areas_page2, total = list_service_areas(db_session, skip=2, limit=2)
    assert len(areas_page2) == 2
    assert total == total_areas_in_db
    
    # Check that there's no overlap between pages
    page1_pincodes = [area.pincode for area in areas_page1]
    page2_pincodes = [area.pincode for area in areas_page2]
    assert len(set(page1_pincodes).intersection(set(page2_pincodes))) == 0

def test_create_service_area(db_session: Session, test_admin: User):
    """Test creating a service area."""
    # Create a new service area
    pincode = "500001"
    service_area_create = ServiceableAreaCreate(pincode=pincode, is_active=True)
    
    created_area = create_service_area(db_session, service_area_create, test_admin.id)
    
    assert created_area.pincode == pincode
    assert created_area.is_active is True
    assert created_area.added_by_admin_id == test_admin.id
    assert created_area.created_at is not None
    
    # Verify that it exists in the database
    db_area = db_session.query(ServiceableArea).filter(ServiceableArea.pincode == pincode).first()
    assert db_area is not None
    assert db_area.pincode == pincode
    assert db_area.is_active is True

def test_update_service_area(db_session: Session, test_service_areas: list[ServiceableArea]):
    """Test updating a service area."""
    # Create a new test area with a known state to update
    test_pincode = f"test_update_{uuid.uuid4().hex[:6]}"
    initial_is_active = True
    admin_id = test_service_areas[0].added_by_admin_id
    
    area_to_update = ServiceableArea(
        pincode=test_pincode,
        is_active=initial_is_active,
        added_by_admin_id=admin_id
    )
    db_session.add(area_to_update)
    db_session.commit()
    db_session.refresh(area_to_update)
    
    try:
        # Create an update schema to flip the is_active state
        update_data = ServiceableAreaUpdate(is_active=not initial_is_active)
        
        # Update the area
        updated_area = update_service_area(db_session, area_to_update.pincode, update_data)
        
        assert updated_area is not None
        assert updated_area.pincode == area_to_update.pincode
        assert updated_area.is_active != initial_is_active
        
        # Verify the update in the database
        db_area = db_session.query(ServiceableArea).filter(
            ServiceableArea.pincode == area_to_update.pincode
        ).first()
        
        assert db_area is not None
        assert db_area.is_active != initial_is_active
        
        # Try to update a non-existent area
        non_existent_update = update_service_area(db_session, "99999", update_data)
        assert non_existent_update is None
    finally:
        # Clean up the test area
        db_session.delete(area_to_update)
        db_session.commit() 