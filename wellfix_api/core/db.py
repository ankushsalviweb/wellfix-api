from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from typing import Generator

# Ensure this import works. If it fails here, the issue might be in config.py or .env
from wellfix_api.core.config import settings

# Create the SQLAlchemy engine using the database URL from settings
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

# Create a configured "Session" class
# autocommit=False and autoflush=False are common defaults for web apps
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a base class for declarative models
Base = declarative_base()

def get_db() -> Generator:
    """FastAPI dependency to inject a database session into path operations."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 