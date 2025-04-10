from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

# Base ServiceableArea schema with common attributes
class ServiceableAreaBase(BaseModel):
    """Base schema for ServiceableArea with common attributes."""
    pincode: str = Field(..., description="Postal code (pincode) of the service area")
    is_active: bool = Field(True, description="Whether this pincode is currently serviceable")
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "pincode": "110001",
            "is_active": True
        }
    })

# Schema for creating a new ServiceableArea
class ServiceableAreaCreate(ServiceableAreaBase):
    """Schema for creating a new ServiceableArea."""
    pass

# Schema for updating an existing ServiceableArea
class ServiceableAreaUpdate(BaseModel):
    """Schema for updating an existing ServiceableArea."""
    is_active: Optional[bool] = Field(None, description="Update the active status of the pincode")

# Schema for ServiceableArea in database
class ServiceableAreaInDB(ServiceableAreaBase):
    """Full ServiceableArea schema as stored in the database."""
    added_by_admin_id: Optional[str] = Field(None, description="ID of the admin who added this area")
    created_at: datetime = Field(..., description="When this pincode was added to serviceable areas")

    model_config = ConfigDict(from_attributes=True)

# ServiceableArea schema for API responses
class ServiceableArea(ServiceableAreaBase):
    """ServiceableArea schema for API responses."""
    created_at: datetime = Field(..., description="When this pincode was added to serviceable areas")
    admin_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
        
# Schema for ServiceableArea list response
class ServiceableAreaList(BaseModel):
    """Schema for a list of ServiceableArea objects with pagination."""
    total: int
    items: list[ServiceableArea]

    model_config = ConfigDict(from_attributes=True)

class ServiceAreaStatus(BaseModel):
    """
    Schema for the response of the service area check endpoint.
    
    This schema is used to report whether a given pincode is serviceable.
    """
    pincode: str
    is_serviceable: bool
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "pincode": "560001",
            "is_serviceable": True
        }
    }) 