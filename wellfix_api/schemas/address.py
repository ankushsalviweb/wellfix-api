"""
Address schemas.
"""

from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from datetime import datetime

# Base Address schema for common attributes
class AddressBase(BaseModel):
    """Base schema for address attributes."""
    street_address: str = Field(..., description="Street address")
    city: str = Field(..., description="City")
    state: str = Field(..., description="State/province")
    pincode: str = Field(..., description="Postal/ZIP code")
    is_default: bool = Field(False, description="Whether this is the default address")

# Schema for creating a new address
class AddressCreate(AddressBase):
    """Schema for creating a new address."""
    pass

# Schema for updating an existing address
class AddressUpdate(BaseModel):
    """Schema for updating an address."""
    street_address: Optional[str] = Field(None, description="Street address")
    city: Optional[str] = Field(None, description="City")
    state: Optional[str] = Field(None, description="State/province")
    pincode: Optional[str] = Field(None, description="Postal/ZIP code")
    is_default: Optional[bool] = Field(None, description="Whether this is the default address")

# Schema for reading an address
class Address(AddressBase):
    """Schema for reading an address."""
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# Schema for listing addresses
class AddressList(BaseModel):
    """Schema for listing addresses with pagination."""
    items: List[Address]
    total: int
    
    model_config = ConfigDict(from_attributes=True) 