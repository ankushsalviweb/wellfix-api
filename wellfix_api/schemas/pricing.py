"""
Pricing configuration schemas.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


# Base schema for common PricingConfig attributes
class PricingConfigBase(BaseModel):
    """Base schema for pricing configuration attributes."""
    name: str = Field(..., description="Name of the pricing configuration", max_length=100)
    description: Optional[str] = Field(None, description="Optional description of the pricing configuration")
    
    # Base Rates
    base_diagnostic_fee: float = Field(..., description="Base fee for diagnostic service", ge=0)
    base_onsite_fee: float = Field(..., description="Base fee for on-site service", ge=0)
    
    # Hourly Rates
    hourly_rate_hardware: float = Field(..., description="Hourly rate for hardware repairs", ge=0)
    hourly_rate_software: float = Field(..., description="Hourly rate for software repairs", ge=0)
    hourly_rate_network: float = Field(..., description="Hourly rate for network repairs", ge=0)
    
    # Surcharges
    emergency_surcharge_percentage: float = Field(25.0, description="Percentage surcharge for emergency service", ge=0)
    weekend_surcharge_percentage: float = Field(15.0, description="Percentage surcharge for weekend service", ge=0)
    evening_surcharge_percentage: float = Field(10.0, description="Percentage surcharge for evening service", ge=0)
    
    # Service Area Surcharge
    distance_surcharge_per_mile: float = Field(0.5, description="Surcharge per mile beyond base service area", ge=0)
    base_service_radius_miles: float = Field(10.0, description="Base service area radius in miles", ge=0)
    
    # Status
    is_active: bool = Field(True, description="Whether this pricing configuration is active")
    

# Schema for creating a new pricing configuration
class PricingConfigCreate(PricingConfigBase):
    """Schema for creating a new pricing configuration."""
    is_default: bool = Field(False, description="Whether this pricing configuration is the default")


# Schema for updating an existing pricing configuration
class PricingConfigUpdate(BaseModel):
    """Schema for updating an existing pricing configuration."""
    name: Optional[str] = Field(None, description="Name of the pricing configuration", max_length=100)
    description: Optional[str] = Field(None, description="Description of the pricing configuration")
    
    # Base Rates
    base_diagnostic_fee: Optional[float] = Field(None, description="Base fee for diagnostic service", ge=0)
    base_onsite_fee: Optional[float] = Field(None, description="Base fee for on-site service", ge=0)
    
    # Hourly Rates
    hourly_rate_hardware: Optional[float] = Field(None, description="Hourly rate for hardware repairs", ge=0)
    hourly_rate_software: Optional[float] = Field(None, description="Hourly rate for software repairs", ge=0)
    hourly_rate_network: Optional[float] = Field(None, description="Hourly rate for network repairs", ge=0)
    
    # Surcharges
    emergency_surcharge_percentage: Optional[float] = Field(None, description="Percentage surcharge for emergency service", ge=0)
    weekend_surcharge_percentage: Optional[float] = Field(None, description="Percentage surcharge for weekend service", ge=0)
    evening_surcharge_percentage: Optional[float] = Field(None, description="Percentage surcharge for evening service", ge=0)
    
    # Service Area Surcharge
    distance_surcharge_per_mile: Optional[float] = Field(None, description="Surcharge per mile beyond base service area", ge=0)
    base_service_radius_miles: Optional[float] = Field(None, description="Base service area radius in miles", ge=0)
    
    # Status
    is_active: Optional[bool] = Field(None, description="Whether this pricing configuration is active")
    is_default: Optional[bool] = Field(None, description="Whether this pricing configuration is the default")


# Schema for reading a pricing configuration
class PricingConfigResponse(PricingConfigBase):
    """Schema for reading a pricing configuration."""
    id: int
    is_default: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Schema for listing pricing configurations
class PricingConfigListResponse(BaseModel):
    """Schema for listing pricing configurations."""
    count: int
    pricing_configs: list[PricingConfigResponse]
    
    model_config = ConfigDict(from_attributes=True) 