"""
Schemas package for API validation and serialization.
"""

from .user import User, UserCreate, UserUpdate, UserInDB, UserBase
from .address import Address, AddressCreate, AddressUpdate, AddressBase
from .token import Token, TokenData, TokenPayload
from .service_area import ServiceAreaStatus, ServiceableArea, ServiceableAreaCreate, ServiceableAreaUpdate, ServiceableAreaList
from .job import (
    # Job creation and response schemas
    JobCreate, JobSummary, JobDetail, JobList,
    # Status and updates
    JobStatusUpdateCreate, JobStatusUpdateResponse,
    # Other operations
    JobNoteCreate, JobQuoteUpdate, PaymentStatusUpdate, JobCancellation, JobAssignment
)
