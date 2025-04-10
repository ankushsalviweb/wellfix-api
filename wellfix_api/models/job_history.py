"""
Database model for tracking job history and status changes.
"""

from typing import Optional
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from wellfix_api.core.db import Base
from wellfix_api.models.enums import JobStatus

# Helper function for datetime.now with UTC timezone
def utc_now():
    return datetime.now(timezone.utc)

class JobHistory(Base):
    """
    Database model for tracking changes to a job's status.
    This provides an audit trail of all status changes and notes for a job.
    """
    __tablename__ = "job_history"

    id = Column(Integer, primary_key=True, index=True)
    
    # Job reference
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    job = relationship("Job", back_populates="history")
    
    # Status information
    status = Column(Enum(JobStatus), nullable=False)
    notes = Column(Text, nullable=True)
    
    # User who made the change
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    user = relationship("User")
    
    # Timestamp
    created_at = Column(DateTime, nullable=False, default=utc_now)
    
    def __repr__(self):
        return f"<JobHistory id={self.id} job_id={self.job_id} status={self.status}>" 