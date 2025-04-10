"""
Pydantic schemas for job-related operations.
"""

from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, ConfigDict

from wellfix_api.models.enums import JobStatus, RepairType, PaymentStatus


# Base schemas for common fields
class AddressBase(BaseModel):
    """Base schema for address summary in job responses."""
    pincode: str
    city: str
    street_address: Optional[str] = None
    state: Optional[str] = None


class UserBase(BaseModel):
    """Base schema for user summary in job responses."""
    id: Union[int, str]
    first_name: str
    last_name: str
    email: str
    phone_number: str


# Job Status Update Schemas
class JobStatusUpdateBase(BaseModel):
    """Base schema for job status updates."""
    previous_status: Optional[JobStatus] = None
    new_status: JobStatus
    notes: Optional[str] = None
    timestamp: datetime
    user_id: Union[int, str]


class JobStatusUpdateCreate(BaseModel):
    """Schema for creating a job status update."""
    status: JobStatus = Field(..., description="The new status to set")
    notes: Optional[str] = Field(None, description="Optional notes about the status change")
    customer_consent_for_lab: Optional[bool] = Field(
        None, 
        description="Flag to indicate customer consent for lab work (required for certain transitions)"
    )


class JobStatusUpdateResponse(JobStatusUpdateBase):
    """Schema for status update responses."""
    id: int
    
    model_config = ConfigDict(from_attributes=True)


# Job Note Schemas
class JobNoteCreate(BaseModel):
    """Schema for adding notes to a job."""
    notes: str = Field(..., description="Notes to add to the job")


# Job Quote Schemas
class JobQuoteUpdate(BaseModel):
    """Schema for updating a job's cost quotes."""
    estimated_cost: Optional[float] = Field(None, description="The estimated cost of repair", ge=0)
    final_cost: Optional[float] = Field(None, description="The final cost of repair", ge=0)
    notes: Optional[str] = Field(None, description="Optional notes about the quote")


# Payment Status Schemas
class PaymentStatusUpdate(BaseModel):
    """Schema for updating a job's payment status."""
    payment_status: PaymentStatus = Field(..., description="The new payment status")
    notes: Optional[str] = Field(None, description="Optional notes about the payment")


# Job Cancellation Schemas
class JobCancellation(BaseModel):
    """Schema for cancelling a job."""
    reason: str = Field(..., description="Reason for cancellation")


# Job Creation and Listing Schemas
class JobCreate(BaseModel):
    """Schema for creating a new job."""
    address_id: Optional[str] = Field(None, description="ID of the service address")
    laptop_manufacturer: str = Field(..., description="Laptop manufacturer name")
    laptop_model: str = Field(..., description="Laptop model name/number")
    laptop_serial_number: Optional[str] = Field(None, description="Laptop serial number if available")
    reported_symptoms: str = Field(..., description="Description of the issues reported")
    repair_type_requested: RepairType = Field(..., description="Type of repair service requested")


class JobAssignment(BaseModel):
    """Schema for assigning an engineer to a job."""
    engineer_id: Optional[Union[int, str]] = Field(None, description="ID of the engineer to assign, or null to unassign")


# Job Response Schemas
class JobBase(BaseModel):
    """Base schema with common job fields."""
    laptop_manufacturer: str
    laptop_model: str
    laptop_serial_number: Optional[str] = None
    reported_symptoms: str
    repair_type_requested: RepairType
    status: JobStatus
    scheduled_datetime: Optional[datetime] = None
    estimated_cost: Optional[float] = None
    final_cost: Optional[float] = None
    payment_status: PaymentStatus
    customer_consent_for_lab: bool
    created_at: datetime
    updated_at: datetime


class JobSummary(JobBase):
    """Schema for job summaries in listings."""
    id: int
    customer_id: Union[int, str]
    engineer_id: Optional[Union[int, str]] = None
    address: AddressBase
    
    model_config = ConfigDict(from_attributes=True)


class JobDetail(JobBase):
    """Schema for detailed job information."""
    id: int
    customer_id: Union[int, str]
    engineer_id: Optional[Union[int, str]] = None
    address_id: Union[int, str]
    engineer_notes: Optional[str] = None
    admin_notes: Optional[str] = None
    cancellation_reason: Optional[str] = None
    
    # Expanded relationship data
    address: Optional[AddressBase] = None
    customer: Optional[UserBase] = None
    engineer: Optional[UserBase] = None
    status_updates: Optional[List[JobStatusUpdateResponse]] = None
    
    model_config = ConfigDict(from_attributes=True)


class JobList(BaseModel):
    """Schema for paginated job listings."""
    count: int
    jobs: List[JobSummary] 