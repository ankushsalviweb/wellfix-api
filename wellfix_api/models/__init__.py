"""
Database models package for the WellFix API.
"""

# Import all models here to make them available to the Alembic migrations
from wellfix_api.models.user import User, UserRole
from wellfix_api.models.profile import Profile
from wellfix_api.models.job import Job, RepairJob, JobStatusUpdate
from wellfix_api.models.job_history import JobHistory
from wellfix_api.models.enums import JobStatus, PaymentStatus, DeviceType, RepairType
from wellfix_api.models.address import Address
from wellfix_api.models.service_area import ServiceableArea
