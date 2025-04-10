"""
Test database utilities for testing.
"""

from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from wellfix_api.core.db import Base, get_db

# Import all models to ensure they are registered with Base.metadata
from wellfix_api.models.user import User
from wellfix_api.models.address import Address
from wellfix_api.models.service_area import ServiceableArea
from wellfix_api.models.job import Job, RepairJob, JobStatusUpdate, Rating
from wellfix_api.models.profile import Profile

# Create an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool  # Use StaticPool to maintain connection between transactions
)

# Create a TestingSessionLocal class for creating db sessions
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create all tables in the test database
Base.metadata.create_all(bind=engine)

def override_get_db() -> Generator:
    """
    Override the get_db dependency to use the test database.
    """
    # Create a fresh session for each request
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close() 