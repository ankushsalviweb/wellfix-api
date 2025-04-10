import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from wellfix_api.models.user import User
from wellfix_api.models.address import Address
from wellfix_api.core.db import Base

@pytest.fixture
def db_session():
    """Create a test in-memory database session."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

@pytest.fixture
def test_user(db_session):
    """Create a test user."""
    user = User(
        email="test@example.com",
        password_hash="hashed_password",
        first_name="Test",
        last_name="User",
        phone_number="1234567890",
        role="CUSTOMER",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    return user

def test_create_address(db_session, test_user):
    """Test creating an address."""
    # Create a new address
    address = Address(
        user_id=test_user.id,
        street_address="123 Test St",
        city="Test City",
        state="Test State",
        pincode="12345",
        is_default=True
    )
    
    # Add the address to the database
    db_session.add(address)
    db_session.commit()
    
    # Query the address from the database
    retrieved_address = db_session.query(Address).filter_by(user_id=test_user.id).first()
    
    # Check that the address was retrieved
    assert retrieved_address is not None
    assert retrieved_address.street_address == "123 Test St"
    assert retrieved_address.city == "Test City"
    assert retrieved_address.state == "Test State"
    assert retrieved_address.pincode == "12345"
    assert retrieved_address.is_default == True

def test_user_address_relationship(db_session, test_user):
    """Test the relationship between User and Address."""
    # Create addresses for the user
    address1 = Address(
        user_id=test_user.id,
        street_address="123 Test St",
        city="Test City",
        state="Test State",
        pincode="12345",
        is_default=True
    )
    
    address2 = Address(
        user_id=test_user.id,
        street_address="456 Other St",
        city="Other City",
        state="Other State",
        pincode="67890",
        is_default=False
    )
    
    # Add the addresses to the database
    db_session.add(address1)
    db_session.add(address2)
    db_session.commit()
    
    # Refresh the user object to load the addresses
    db_session.refresh(test_user)
    
    # Check that the user has the addresses
    assert len(test_user.addresses) == 2
    assert test_user.addresses[0].street_address == "123 Test St"
    assert test_user.addresses[1].street_address == "456 Other St"
    
    # Check that the addresses have the correct user
    assert address1.user.id == test_user.id
    assert address2.user.id == test_user.id 