"""
Job status transition validator.

This module defines the valid state transitions for jobs based on user roles.
"""

from typing import Dict, List, Optional, Set, Tuple
from wellfix_api.models.enums import JobStatus
from wellfix_api.models.user import UserRole


# Define valid transitions for each role
# Format: {current_status: {set of valid next statuses}}

# Admin can perform all transitions
ADMIN_TRANSITIONS: Dict[JobStatus, Set[JobStatus]] = {
    JobStatus.PENDING_ASSIGNMENT: {
        JobStatus.ASSIGNED, 
        JobStatus.CANCELLED
    },
    JobStatus.ASSIGNED: {
        JobStatus.PENDING_PICKUP_FOR_LAB,
        JobStatus.PENDING_VISIT,
        JobStatus.CANCELLED
    },
    JobStatus.PENDING_PICKUP_FOR_LAB: {
        JobStatus.IN_TRANSIT_TO_LAB,
        JobStatus.CANCELLED,
        JobStatus.ON_SITE_DIAGNOSIS  # Fallback to on-site if lab transit not possible
    },
    JobStatus.IN_TRANSIT_TO_LAB: {
        JobStatus.LAB_DIAGNOSIS,
        JobStatus.CANCELLED
    },
    JobStatus.PENDING_VISIT: {
        JobStatus.ON_SITE_DIAGNOSIS,
        JobStatus.CANCELLED,
        JobStatus.ESCALATED_TO_LAB  # If on-site diagnosis not possible
    },
    JobStatus.ON_SITE_DIAGNOSIS: {
        JobStatus.REPAIR_IN_PROGRESS_ON_SITE,
        JobStatus.PENDING_QUOTE_APPROVAL,
        JobStatus.CANCELLED,
        JobStatus.ESCALATED_TO_LAB
    },
    JobStatus.LAB_DIAGNOSIS: {
        JobStatus.REPAIR_IN_PROGRESS_LAB,
        JobStatus.PENDING_QUOTE_APPROVAL,
        JobStatus.CANCELLED
    },
    JobStatus.ESCALATED_TO_LAB: {
        JobStatus.PENDING_PICKUP_FOR_LAB,
        JobStatus.CANCELLED
    },
    JobStatus.PENDING_QUOTE_APPROVAL: {
        JobStatus.REPAIR_IN_PROGRESS_LAB,
        JobStatus.REPAIR_IN_PROGRESS_ON_SITE,
        JobStatus.CANCELLED
    },
    JobStatus.REPAIR_IN_PROGRESS_LAB: {
        JobStatus.PENDING_RETURN_DELIVERY,
        JobStatus.PENDING_PAYMENT,
        JobStatus.CANCELLED
    },
    JobStatus.REPAIR_IN_PROGRESS_ON_SITE: {
        JobStatus.PENDING_PAYMENT,
        JobStatus.CANCELLED
    },
    JobStatus.PENDING_RETURN_DELIVERY: {
        JobStatus.IN_TRANSIT_FROM_LAB,
        JobStatus.CANCELLED
    },
    JobStatus.IN_TRANSIT_FROM_LAB: {
        JobStatus.PENDING_PAYMENT,
        JobStatus.CANCELLED
    },
    JobStatus.PENDING_PAYMENT: {
        JobStatus.COMPLETED,
        JobStatus.CANCELLED
    },
    # Terminal states - no transitions out
    JobStatus.COMPLETED: set(),
    JobStatus.CANCELLED: set()
}

# Engineer transitions are more limited
ENGINEER_TRANSITIONS: Dict[JobStatus, Set[JobStatus]] = {
    # Engineers can't assign jobs or cancel jobs
    JobStatus.PENDING_ASSIGNMENT: set(),
    
    # Engineers can update from assigned to in-progress states
    JobStatus.ASSIGNED: {
        JobStatus.PENDING_PICKUP_FOR_LAB,
        JobStatus.PENDING_VISIT,
    },
    JobStatus.PENDING_PICKUP_FOR_LAB: {
        JobStatus.IN_TRANSIT_TO_LAB,
        JobStatus.ON_SITE_DIAGNOSIS  # Fallback to on-site if lab transit not possible
    },
    JobStatus.IN_TRANSIT_TO_LAB: {
        JobStatus.LAB_DIAGNOSIS,
    },
    JobStatus.PENDING_VISIT: {
        JobStatus.ON_SITE_DIAGNOSIS,
        JobStatus.ESCALATED_TO_LAB  # If on-site diagnosis not possible
    },
    JobStatus.ON_SITE_DIAGNOSIS: {
        JobStatus.REPAIR_IN_PROGRESS_ON_SITE,
        JobStatus.PENDING_QUOTE_APPROVAL,
        JobStatus.ESCALATED_TO_LAB
    },
    JobStatus.LAB_DIAGNOSIS: {
        JobStatus.REPAIR_IN_PROGRESS_LAB,
        JobStatus.PENDING_QUOTE_APPROVAL,
    },
    JobStatus.ESCALATED_TO_LAB: {
        JobStatus.PENDING_PICKUP_FOR_LAB,
    },
    # Engineers can't directly approve quotes
    JobStatus.PENDING_QUOTE_APPROVAL: set(),
    
    JobStatus.REPAIR_IN_PROGRESS_LAB: {
        JobStatus.PENDING_RETURN_DELIVERY,
        JobStatus.PENDING_PAYMENT,
    },
    JobStatus.REPAIR_IN_PROGRESS_ON_SITE: {
        JobStatus.PENDING_PAYMENT,
    },
    JobStatus.PENDING_RETURN_DELIVERY: {
        JobStatus.IN_TRANSIT_FROM_LAB,
    },
    JobStatus.IN_TRANSIT_FROM_LAB: {
        JobStatus.PENDING_PAYMENT,
    },
    JobStatus.PENDING_PAYMENT: {
        JobStatus.COMPLETED,
    },
    # Terminal states - no transitions out
    JobStatus.COMPLETED: set(),
    JobStatus.CANCELLED: set()
}

# Customer transitions are very limited
CUSTOMER_TRANSITIONS: Dict[JobStatus, Set[JobStatus]] = {
    # Customers can only cancel jobs and approve quotes
    JobStatus.PENDING_ASSIGNMENT: {
        JobStatus.CANCELLED
    },
    JobStatus.ASSIGNED: {
        JobStatus.CANCELLED
    },
    JobStatus.PENDING_PICKUP_FOR_LAB: {
        JobStatus.CANCELLED
    },
    JobStatus.PENDING_VISIT: {
        JobStatus.CANCELLED
    },
    # After diagnosis begins, customers can only cancel or accept quotes
    JobStatus.PENDING_QUOTE_APPROVAL: {
        JobStatus.REPAIR_IN_PROGRESS_LAB,
        JobStatus.REPAIR_IN_PROGRESS_ON_SITE,
        JobStatus.CANCELLED
    },
    # Terminal states and all other states - no transitions
    JobStatus.IN_TRANSIT_TO_LAB: set(),
    JobStatus.LAB_DIAGNOSIS: set(),
    JobStatus.ON_SITE_DIAGNOSIS: set(),
    JobStatus.ESCALATED_TO_LAB: set(),
    JobStatus.REPAIR_IN_PROGRESS_LAB: set(),
    JobStatus.REPAIR_IN_PROGRESS_ON_SITE: set(),
    JobStatus.PENDING_RETURN_DELIVERY: set(),
    JobStatus.IN_TRANSIT_FROM_LAB: set(),
    JobStatus.PENDING_PAYMENT: set(),
    JobStatus.COMPLETED: set(),
    JobStatus.CANCELLED: set()
}


def is_transition_allowed(
    current_status: JobStatus, 
    new_status: JobStatus, 
    user_role: UserRole
) -> bool:
    """
    Check if a status transition is allowed based on the current status, 
    new status, and user role.
    
    Args:
        current_status: The current status of the job
        new_status: The proposed new status for the job
        user_role: The role of the user attempting to make the transition
    
    Returns:
        True if the transition is allowed, False otherwise
    """
    # No transition needed if status is the same
    if current_status == new_status:
        return True
    
    # Get the appropriate transition map based on user role
    if user_role == UserRole.ADMIN:
        transitions = ADMIN_TRANSITIONS
    elif user_role == UserRole.ENGINEER:
        transitions = ENGINEER_TRANSITIONS
    elif user_role == UserRole.CUSTOMER:
        transitions = CUSTOMER_TRANSITIONS
    else:
        # Unknown roles can't make transitions
        return False
    
    # Check if transition is allowed
    allowed_next_statuses = transitions.get(current_status, set())
    return new_status in allowed_next_statuses


def get_allowed_transitions(current_status: JobStatus, role: UserRole) -> List[JobStatus]:
    """
    Get all allowed next statuses for a given current status and user role.
    
    Args:
        current_status: The current status of the job
        role: The role of the user 
        
    Returns:
        List[JobStatus]: List of allowed next statuses
    """
    # Get the appropriate transition map based on user role
    if role == UserRole.ADMIN:
        transitions = ADMIN_TRANSITIONS
    elif role == UserRole.ENGINEER:
        transitions = ENGINEER_TRANSITIONS
    elif role == UserRole.CUSTOMER:
        transitions = CUSTOMER_TRANSITIONS
    else:
        # Unknown roles don't have transitions
        return []
    
    # Return allowed transitions for the current status, or empty list if none
    return list(transitions.get(current_status, set())) 