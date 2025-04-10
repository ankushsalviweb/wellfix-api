import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from wellfix_api.core.db import Base

class Address(Base):
    __tablename__ = "addresses"

    # Use String type for ID to be compatible with both PostgreSQL UUID and SQLite
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False) # Ensure cascade delete if user is deleted
    street_address = Column(String, nullable=False)
    city = Column(String, nullable=False)
    state = Column(String, nullable=False)
    pincode = Column(String, index=True, nullable=False)
    is_default = Column(Boolean, default=False, nullable=False)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # --- Relationships ---
    user = relationship("User", back_populates="addresses")
    jobs = relationship("RepairJob", back_populates="address")

    def __repr__(self):
        return f"<Address(id={self.id}, user_id={self.user_id}, pincode='{self.pincode}')>" 