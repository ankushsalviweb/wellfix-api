import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from wellfix_api.core.db import Base, get_db
from wellfix_api.main import app
from wellfix_api.core.config import settings

# Test environment settings
TEST_JWT_SECRET_KEY = "test_key_for_development"
TEST_DATABASE_URL = "sqlite:///:memory:"

# Set up test environment variables
@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up test environment variables before tests are run."""
    original_env = {}
    
    # Store original environment variables
    for key in ["DATABASE_URL", "JWT_SECRET_KEY", "JWT_ALGORITHM", "ACCESS_TOKEN_EXPIRE_MINUTES"]:
        original_env[key] = os.environ.get(key)
    
    # Set test environment variables
    os.environ["DATABASE_URL"] = TEST_DATABASE_URL
    os.environ["JWT_SECRET_KEY"] = TEST_JWT_SECRET_KEY
    os.environ["JWT_ALGORITHM"] = "HS256"
    os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "1440"  # Clean value without comments
    
    # Update settings with new environment values directly
    settings.DATABASE_URL = TEST_DATABASE_URL
    settings.JWT_SECRET_KEY = TEST_JWT_SECRET_KEY
    settings.JWT_ALGORITHM = "HS256"
    settings.ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # Set directly as integer
    
    yield
    
    # Restore original environment variables
    for key, value in original_env.items():
        if value is not None:
            os.environ[key] = value
        elif key in os.environ:
            del os.environ[key]

@pytest.fixture(scope="session")
def test_db_engine():
    """Create a test database engine."""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

# Use function scope for the database session to reset between tests
@pytest.fixture(scope="function")
def db_session(test_db_engine):
    """Create a fresh test database session for each test function."""
    # Create tables
    Base.metadata.create_all(bind=test_db_engine)
    
    # Create session
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_db_engine)
    db = TestSessionLocal()
    
    try:
        yield db
    finally:
        db.close()
        
    # Drop tables after test
    Base.metadata.drop_all(bind=test_db_engine)
    # Recreate tables for next test
    Base.metadata.create_all(bind=test_db_engine) 