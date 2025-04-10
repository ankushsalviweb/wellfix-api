"""
Enumeration types for the WellFix API.

This module defines all enum types used throughout the application
to ensure consistency and make database migrations easier.
"""

from enum import Enum, auto


class JobStatus(str, Enum):
    """
    Job status enumeration that defines all possible states a repair job can be in.
    The status flow follows a specific state machine based on the repair workflow.
    """
    # Initial status
    PENDING_ASSIGNMENT = "PENDING_ASSIGNMENT"  # Job created but not assigned to an engineer
    
    # Assignment and scheduling
    ASSIGNED = "ASSIGNED"  # Job assigned to an engineer
    PENDING_VISIT = "PENDING_VISIT"  # Waiting for engineer to visit (on-site flow)
    PENDING_PICKUP_FOR_LAB = "PENDING_PICKUP_FOR_LAB"  # Waiting for pickup to lab
    
    # Transit statuses
    IN_TRANSIT_TO_LAB = "IN_TRANSIT_TO_LAB"  # Device in transit to lab
    IN_TRANSIT_FROM_LAB = "IN_TRANSIT_FROM_LAB"  # Device in transit from lab back to customer
    
    # Diagnosis statuses
    ON_SITE_DIAGNOSIS = "ON_SITE_DIAGNOSIS"  # Engineer diagnosing on-site
    LAB_DIAGNOSIS = "LAB_DIAGNOSIS"  # Lab diagnosing issues
    ESCALATED_TO_LAB = "ESCALATED_TO_LAB"  # On-site diagnosis escalated to lab
    
    # Quote and approval
    PENDING_QUOTE_APPROVAL = "PENDING_QUOTE_APPROVAL"  # Waiting for customer to approve quote
    
    # Repair in progress
    REPAIR_IN_PROGRESS_LAB = "REPAIR_IN_PROGRESS_LAB"  # Repair happening in lab
    REPAIR_IN_PROGRESS_ON_SITE = "REPAIR_IN_PROGRESS_ON_SITE"  # Repair happening on-site
    
    # Final stages
    PENDING_RETURN_DELIVERY = "PENDING_RETURN_DELIVERY"  # Repair complete, waiting to arrange return
    PENDING_PAYMENT = "PENDING_PAYMENT"  # Waiting for payment
    
    # Terminal statuses
    COMPLETED = "COMPLETED"  # Job successfully completed
    CANCELLED = "CANCELLED"  # Job cancelled


class PaymentStatus(str, Enum):
    """
    Payment status enumeration for tracking job payments.
    """
    NOT_APPLICABLE = "NOT_APPLICABLE"  # No payment required (e.g., warranty repair)
    PENDING = "PENDING"  # Payment is pending
    COMPLETED = "COMPLETED"  # Payment has been made
    REFUNDED = "REFUNDED"  # Payment has been refunded
    FAILED = "FAILED"  # Payment attempt failed


class DeviceType(str, Enum):
    """
    Device type enumeration for categorizing the type of device being repaired.
    """
    LAPTOP = "LAPTOP"
    DESKTOP = "DESKTOP"
    TABLET = "TABLET"
    PHONE = "PHONE"
    OTHER = "OTHER"


class RepairType(str, Enum):
    """
    Repair type enumeration for categorizing the type of repair requested.
    """
    HARDWARE = "HARDWARE"  # Hardware repair (physical components)
    SOFTWARE = "SOFTWARE"  # Software repair or recovery
    DATA_RECOVERY = "DATA_RECOVERY"  # Data recovery
    UPGRADE = "UPGRADE"  # Upgrade components
    MAINTENANCE = "MAINTENANCE"  # Regular maintenance
    DIAGNOSTIC = "DIAGNOSTIC"  # Diagnostic only
    OTHER = "OTHER"  # Other/custom repair type 