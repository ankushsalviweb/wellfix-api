from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, Float, DateTime, Enum, func
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from wellfix_api.core.db import Base
from wellfix_api.models.enums import JobStatus, RepairType, PaymentStatus

# Helper function for datetime.now with UTC timezone
def utc_now():
    return datetime.now(timezone.utc)

class Job(Base):
    """
    Database model for a repair job.
    """
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    
    # Customer information
    customer_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    customer = relationship("User", foreign_keys=[customer_id], back_populates="jobs_as_customer")
    
    # Assignment information
    engineer_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    engineer = relationship("User", foreign_keys=[engineer_id], back_populates="jobs_as_engineer")

    # Address for on-site service
    address_id = Column(Integer, ForeignKey("addresses.id", ondelete="SET NULL"), nullable=True)
    address = relationship("Address")
    
    # Laptop details
    laptop_manufacturer = Column(String(100), nullable=False)
    laptop_model = Column(String(100), nullable=False)
    laptop_serial_number = Column(String(100), nullable=True)
    reported_symptoms = Column(Text, nullable=False)
    repair_type_requested = Column(String(50), nullable=False)
    
    # Diagnosis and repair details
    technical_diagnosis = Column(Text, nullable=True)
    repairs_performed = Column(Text, nullable=True)
    parts_replaced = Column(Text, nullable=True)
    
    # Cost and payment
    estimated_cost = Column(Float, nullable=True)
    final_cost = Column(Float, nullable=True)
    payment_status = Column(Enum(PaymentStatus), nullable=False, default=PaymentStatus.PENDING)
    
    # Job status and flow control
    status = Column(Enum(JobStatus), nullable=False, default=JobStatus.PENDING_ASSIGNMENT, index=True)
    customer_consent_for_lab = Column(Boolean, nullable=False, default=False)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=utc_now)
    updated_at = Column(DateTime, nullable=False, default=utc_now, onupdate=utc_now)
    
    # Relationships
    history = relationship("JobHistory", back_populates="job", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Job id={self.id} status={self.status}>"


class RepairJob(Base):
    """
    RepairJob model: The central entity tracking a repair request from start to finish.
    """
    __tablename__ = "repair_jobs"

    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign keys to related entities
    customer_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    engineer_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    address_id = Column(Integer, ForeignKey("addresses.id", ondelete="RESTRICT"), nullable=True)
    
    # Laptop details
    laptop_manufacturer = Column(String(100), nullable=False)
    laptop_model = Column(String(100), nullable=False)
    laptop_serial_number = Column(String(100), nullable=True)
    
    # Repair details
    reported_symptoms = Column(Text, nullable=False)
    repair_type_requested = Column(
        Enum(RepairType), 
        nullable=False, 
        default=RepairType.HARDWARE
    )
    status = Column(
        Enum(JobStatus), 
        nullable=False, 
        default=JobStatus.PENDING_ASSIGNMENT
    )
    
    # Scheduling
    scheduled_datetime = Column(DateTime, nullable=True)
    
    # Financial
    estimated_cost = Column(Float, nullable=True)
    final_cost = Column(Float, nullable=True)
    payment_status = Column(
        Enum(PaymentStatus), 
        nullable=False, 
        default=PaymentStatus.PENDING
    )
    
    # Notes
    engineer_notes = Column(Text, nullable=True)
    admin_notes = Column(Text, nullable=True)
    
    # Special flags
    customer_consent_for_lab = Column(Boolean, default=False, nullable=False)
    cancellation_reason = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)
    
    # Relationships
    customer = relationship("User", foreign_keys=[customer_id], back_populates="customer_jobs")
    engineer = relationship("User", foreign_keys=[engineer_id], back_populates="engineer_jobs")
    address = relationship("Address", back_populates="jobs")
    status_updates = relationship("JobStatusUpdate", back_populates="job", cascade="all, delete-orphan")
    rating = relationship("Rating", back_populates="job", uselist=False, cascade="all, delete-orphan")


class JobStatusUpdate(Base):
    """
    JobStatusUpdate model: Logs changes to a job's status for tracking history.
    """
    __tablename__ = "job_status_updates"

    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign keys
    job_id = Column(Integer, ForeignKey("repair_jobs.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # Status change details
    previous_status = Column(Enum(JobStatus), nullable=True)
    new_status = Column(Enum(JobStatus), nullable=False)
    notes = Column(Text, nullable=True)
    
    # Timestamp
    timestamp = Column(DateTime, default=utc_now, nullable=False)
    
    # Relationships
    job = relationship("RepairJob", back_populates="status_updates")
    user = relationship("User", backref="status_updates")


class Rating(Base):
    """
    Rating model: Stores customer feedback for a completed job.
    """
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign keys
    job_id = Column(Integer, ForeignKey("repair_jobs.id", ondelete="CASCADE"), nullable=False, unique=True)
    customer_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    engineer_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # Rating details
    score = Column(Integer, nullable=False)
    comment = Column(Text, nullable=True)
    
    # Timestamp
    created_at = Column(DateTime, default=utc_now, nullable=False)
    
    # Relationships
    job = relationship("RepairJob", back_populates="rating")
    customer = relationship("User", foreign_keys=[customer_id], backref="submitted_ratings")
    engineer = relationship("User", foreign_keys=[engineer_id], backref="received_ratings") 