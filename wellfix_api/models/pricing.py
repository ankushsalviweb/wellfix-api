"""
Pricing configuration model for the application.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.orm import relationship

from wellfix_api.core.db import Base
from wellfix_api.models.enums import RepairType


def utc_now():
    """Helper function to get current UTC time."""
    return datetime.now(timezone.utc)


class PricingConfig(Base):
    """
    Database model for pricing configuration.
    
    Administrators can set different pricing parameters for the service,
    including base rates, hourly rates, and surcharges.
    """
    __tablename__ = "pricing_configs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    # Base Rates
    base_diagnostic_fee = Column(Float, nullable=False)
    base_onsite_fee = Column(Float, nullable=False)
    
    # Hourly Rates
    hourly_rate_hardware = Column(Float, nullable=False)
    hourly_rate_software = Column(Float, nullable=False)
    hourly_rate_network = Column(Float, nullable=False)
    
    # Surcharges
    emergency_surcharge_percentage = Column(Float, nullable=False, default=25.0)  # 25% surcharge for emergency service
    weekend_surcharge_percentage = Column(Float, nullable=False, default=15.0)    # 15% surcharge for weekend service
    evening_surcharge_percentage = Column(Float, nullable=False, default=10.0)    # 10% surcharge for evening service (after 6pm)
    
    # Service Area Surcharge
    distance_surcharge_per_mile = Column(Float, nullable=False, default=0.5)      # $0.50 per mile beyond base service area
    base_service_radius_miles = Column(Float, nullable=False, default=10.0)       # Base service area radius in miles
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_default = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)
    
    def __repr__(self):
        return f"<PricingConfig id={self.id} name={self.name} active={self.is_active}>" 