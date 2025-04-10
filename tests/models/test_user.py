import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from wellfix_api.models.user import User, UserRole
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

def test_create_user(db_session):
    """Test creating a user."""
    # Create a new user
    user = User(
        email="test@example.com",
        password_hash="hashed_password",
        first_name="Test",
        last_name="User",
        phone_number="1234567890",
        role="CUSTOMER",
        is_active=True
    )
    
    # Add the user to the database
    db_session.add(user)
    db_session.commit()
    
    # Query the user from the database
    retrieved_user = db_session.query(User).filter_by(email="test@example.com").first()
    
    # Check that the user was retrieved
    assert retrieved_user is not None
    assert retrieved_user.email == "test@example.com"
    assert retrieved_user.first_name == "Test"
    assert retrieved_user.last_name == "User"
    assert retrieved_user.role == "CUSTOMER"
    assert retrieved_user.is_active == True 