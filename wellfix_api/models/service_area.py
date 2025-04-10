from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship

from wellfix_api.core.db import Base

class ServiceableArea(Base):
    """
    ServiceableArea model: Defines the pincodes where services are offered, managed by Admins.
    """
    __tablename__ = "serviceable_areas"

    # Using the pincode as the primary key
    pincode = Column(String(10), primary_key=True, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    added_by_admin_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationships
    created_by = relationship("User", foreign_keys=[added_by_admin_id], backref="managed_areas")
    
    def __repr__(self):
        return f"<ServiceableArea(pincode='{self.pincode}', is_active={self.is_active})>" 