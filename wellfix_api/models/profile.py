"""
Database model for user profiles.
"""

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from wellfix_api.core.db import Base

# Helper function for datetime.now with UTC timezone
def utc_now():
    return datetime.now(timezone.utc)

class Profile(Base):
    """
    Database model for user profiles.
    Contains additional information about users not stored in the main User model.
    """
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    bio = Column(Text, nullable=True)
    avatar_url = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False, default=utc_now)
    updated_at = Column(DateTime, nullable=False, default=utc_now, onupdate=utc_now)
    
    # Relationships
    user = relationship("User", back_populates="profile") 