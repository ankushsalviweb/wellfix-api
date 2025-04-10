import uuid
import enum
from datetime import datetime, timezone
from enum import Enum, auto
from typing import Optional, List

from sqlalchemy import Column, String, Boolean, DateTime, Enum as SQLAlchemyEnum, ForeignKey, Text, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func # For server-side defaults like NOW()

from wellfix_api.core.db import Base

class UserRole(str, Enum):
    """User role enumeration."""
    CUSTOMER = "CUSTOMER"
    ENGINEER = "ENGINEER"
    ADMIN = "ADMIN"

class User(Base):
    """
    Database model for a user.

    Users can have different roles (admin, engineer, customer) and
    have different capabilities depending on their role.
    """
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    role = Column(SQLAlchemyEnum(UserRole), default=UserRole.CUSTOMER, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    profile = relationship("Profile", uselist=False, back_populates="user", cascade="all, delete-orphan")
    addresses = relationship("Address", back_populates="user", cascade="all, delete-orphan")
    # managed_areas is created by backref in ServiceableArea
    
    # Job relationships
    jobs_as_customer = relationship("Job", foreign_keys="[Job.customer_id]", back_populates="customer", cascade="all, delete-orphan")
    jobs_as_engineer = relationship("Job", foreign_keys="[Job.engineer_id]", back_populates="engineer")
    
    # RepairJob relationships
    customer_jobs = relationship("RepairJob", foreign_keys="[RepairJob.customer_id]", back_populates="customer", cascade="all, delete-orphan")
    engineer_jobs = relationship("RepairJob", foreign_keys="[RepairJob.engineer_id]", back_populates="engineer")

    def __repr__(self):
        return f"<User id={self.id} email={self.email} role={self.role}>" 