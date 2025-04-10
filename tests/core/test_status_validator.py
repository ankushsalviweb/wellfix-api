"""
Test the status validator module which enforces the job status state machine.
"""

import pytest
from wellfix_api.core.status_validator import is_transition_allowed, get_allowed_transitions
from wellfix_api.models.enums import JobStatus
from wellfix_api.models.user import UserRole


class TestStatusTransitions:
    """Test suite for job status transitions validation."""

    def test_no_transition_returns_true(self):
        """Test that no transition (same status) is always allowed."""
        # For all roles and statuses, transitioning to the same status should be allowed
        for role in [UserRole.ADMIN, UserRole.ENGINEER, UserRole.CUSTOMER]:
            for status in JobStatus:
                assert is_transition_allowed(status, status, role) is True

    def test_admin_transitions(self):
        """Test valid transitions for admin role."""
        # Test a sampling of valid transitions for admin
        valid_transitions = [
            (JobStatus.PENDING_ASSIGNMENT, JobStatus.ASSIGNED),
            (JobStatus.ASSIGNED, JobStatus.PENDING_VISIT),
            (JobStatus.PENDING_VISIT, JobStatus.ON_SITE_DIAGNOSIS),
            (JobStatus.ON_SITE_DIAGNOSIS, JobStatus.REPAIR_IN_PROGRESS_ON_SITE),
            (JobStatus.ON_SITE_DIAGNOSIS, JobStatus.ESCALATED_TO_LAB),
            (JobStatus.ESCALATED_TO_LAB, JobStatus.PENDING_PICKUP_FOR_LAB),
            (JobStatus.PENDING_PICKUP_FOR_LAB, JobStatus.IN_TRANSIT_TO_LAB),
            (JobStatus.IN_TRANSIT_TO_LAB, JobStatus.LAB_DIAGNOSIS),
            (JobStatus.LAB_DIAGNOSIS, JobStatus.PENDING_QUOTE_APPROVAL),
            (JobStatus.PENDING_QUOTE_APPROVAL, JobStatus.REPAIR_IN_PROGRESS_LAB),
            (JobStatus.REPAIR_IN_PROGRESS_LAB, JobStatus.PENDING_RETURN_DELIVERY),
            (JobStatus.PENDING_RETURN_DELIVERY, JobStatus.IN_TRANSIT_FROM_LAB),
            (JobStatus.IN_TRANSIT_FROM_LAB, JobStatus.PENDING_PAYMENT),
            (JobStatus.PENDING_PAYMENT, JobStatus.COMPLETED),
            # Cancellation should be possible at most stages
            (JobStatus.PENDING_ASSIGNMENT, JobStatus.CANCELLED),
            (JobStatus.REPAIR_IN_PROGRESS_ON_SITE, JobStatus.CANCELLED),
            (JobStatus.PENDING_PAYMENT, JobStatus.CANCELLED),
        ]

        for current, next_status in valid_transitions:
            assert is_transition_allowed(current, next_status, UserRole.ADMIN) is True

    def test_admin_invalid_transitions(self):
        """Test invalid transitions for admin role."""
        # Test a sampling of invalid transitions for admin
        invalid_transitions = [
            # Can't skip steps
            (JobStatus.PENDING_ASSIGNMENT, JobStatus.ON_SITE_DIAGNOSIS),
            (JobStatus.PENDING_ASSIGNMENT, JobStatus.COMPLETED),
            # Can't go backwards in flow
            (JobStatus.ASSIGNED, JobStatus.PENDING_ASSIGNMENT),
            (JobStatus.ON_SITE_DIAGNOSIS, JobStatus.PENDING_VISIT),
            (JobStatus.COMPLETED, JobStatus.PENDING_PAYMENT),
            # Can't transition from terminal states
            (JobStatus.COMPLETED, JobStatus.ASSIGNED),
            (JobStatus.CANCELLED, JobStatus.PENDING_ASSIGNMENT),
        ]

        for current, next_status in invalid_transitions:
            assert is_transition_allowed(current, next_status, UserRole.ADMIN) is False

    def test_engineer_transitions(self):
        """Test valid transitions for engineer role."""
        # Test a sampling of valid transitions for engineer
        valid_transitions = [
            (JobStatus.ASSIGNED, JobStatus.PENDING_VISIT),
            (JobStatus.ASSIGNED, JobStatus.PENDING_PICKUP_FOR_LAB),
            (JobStatus.PENDING_VISIT, JobStatus.ON_SITE_DIAGNOSIS),
            (JobStatus.ON_SITE_DIAGNOSIS, JobStatus.REPAIR_IN_PROGRESS_ON_SITE),
            (JobStatus.ON_SITE_DIAGNOSIS, JobStatus.ESCALATED_TO_LAB),
            (JobStatus.ESCALATED_TO_LAB, JobStatus.PENDING_PICKUP_FOR_LAB),
            (JobStatus.PENDING_PICKUP_FOR_LAB, JobStatus.IN_TRANSIT_TO_LAB),
            (JobStatus.IN_TRANSIT_TO_LAB, JobStatus.LAB_DIAGNOSIS),
            (JobStatus.LAB_DIAGNOSIS, JobStatus.REPAIR_IN_PROGRESS_LAB),
            (JobStatus.REPAIR_IN_PROGRESS_LAB, JobStatus.PENDING_RETURN_DELIVERY),
            (JobStatus.PENDING_RETURN_DELIVERY, JobStatus.IN_TRANSIT_FROM_LAB),
            (JobStatus.IN_TRANSIT_FROM_LAB, JobStatus.PENDING_PAYMENT),
            (JobStatus.PENDING_PAYMENT, JobStatus.COMPLETED),
        ]

        for current, next_status in valid_transitions:
            assert is_transition_allowed(current, next_status, UserRole.ENGINEER) is True

    def test_engineer_invalid_transitions(self):
        """Test invalid transitions for engineer role."""
        # Test a sampling of invalid transitions for engineer
        invalid_transitions = [
            # Engineers can't assign jobs
            (JobStatus.PENDING_ASSIGNMENT, JobStatus.ASSIGNED),
            # Engineers can't cancel jobs
            (JobStatus.PENDING_ASSIGNMENT, JobStatus.CANCELLED),
            (JobStatus.PENDING_VISIT, JobStatus.CANCELLED),
            # Engineers can't skip steps
            (JobStatus.ASSIGNED, JobStatus.COMPLETED),
            # Can't transition from terminal states
            (JobStatus.COMPLETED, JobStatus.PENDING_PAYMENT),
            (JobStatus.CANCELLED, JobStatus.ASSIGNED),
        ]

        for current, next_status in invalid_transitions:
            assert is_transition_allowed(current, next_status, UserRole.ENGINEER) is False

    def test_customer_transitions(self):
        """Test valid transitions for customer role."""
        # Test all valid transitions for customer
        valid_transitions = [
            # Customers can cancel jobs at early stages
            (JobStatus.PENDING_ASSIGNMENT, JobStatus.CANCELLED),
            (JobStatus.ASSIGNED, JobStatus.CANCELLED),
            (JobStatus.PENDING_PICKUP_FOR_LAB, JobStatus.CANCELLED),
            (JobStatus.PENDING_VISIT, JobStatus.CANCELLED),
            # Customers can approve quotes
            (JobStatus.PENDING_QUOTE_APPROVAL, JobStatus.REPAIR_IN_PROGRESS_LAB),
            (JobStatus.PENDING_QUOTE_APPROVAL, JobStatus.REPAIR_IN_PROGRESS_ON_SITE),
            (JobStatus.PENDING_QUOTE_APPROVAL, JobStatus.CANCELLED),
        ]

        for current, next_status in valid_transitions:
            assert is_transition_allowed(current, next_status, UserRole.CUSTOMER) is True

    def test_customer_invalid_transitions(self):
        """Test invalid transitions for customer role."""
        # Test a sampling of invalid transitions for customer
        invalid_transitions = [
            # Customers can't make operational transitions
            (JobStatus.PENDING_ASSIGNMENT, JobStatus.ASSIGNED),
            (JobStatus.ASSIGNED, JobStatus.PENDING_VISIT),
            (JobStatus.PENDING_VISIT, JobStatus.ON_SITE_DIAGNOSIS),
            (JobStatus.ON_SITE_DIAGNOSIS, JobStatus.REPAIR_IN_PROGRESS_ON_SITE),
            (JobStatus.PENDING_PAYMENT, JobStatus.COMPLETED),
            # Customers can't cancel jobs after certain stages
            (JobStatus.REPAIR_IN_PROGRESS_ON_SITE, JobStatus.CANCELLED),
            (JobStatus.COMPLETED, JobStatus.CANCELLED),
        ]

        for current, next_status in invalid_transitions:
            assert is_transition_allowed(current, next_status, UserRole.CUSTOMER) is False

    def test_unknown_role_transitions(self):
        """Test that transitions for unknown roles are not allowed."""
        # Unknown role should not be able to make any transitions
        for current in JobStatus:
            for next_status in JobStatus:
                if current != next_status:  # Skip same-status tests
                    assert is_transition_allowed(current, next_status, "UNKNOWN_ROLE") is False

    def test_get_allowed_transitions_admin(self):
        """Test getting allowed transitions for admin role."""
        # Test a few key status points for admin
        assert set(get_allowed_transitions(JobStatus.PENDING_ASSIGNMENT, UserRole.ADMIN)) == {
            JobStatus.ASSIGNED, 
            JobStatus.CANCELLED
        }
        
        assert set(get_allowed_transitions(JobStatus.ON_SITE_DIAGNOSIS, UserRole.ADMIN)) == {
            JobStatus.REPAIR_IN_PROGRESS_ON_SITE,
            JobStatus.PENDING_QUOTE_APPROVAL,
            JobStatus.CANCELLED,
            JobStatus.ESCALATED_TO_LAB
        }
        
        # Terminal states should have no transitions
        assert len(get_allowed_transitions(JobStatus.COMPLETED, UserRole.ADMIN)) == 0
        assert len(get_allowed_transitions(JobStatus.CANCELLED, UserRole.ADMIN)) == 0

    def test_get_allowed_transitions_engineer(self):
        """Test getting allowed transitions for engineer role."""
        # Test a few key status points for engineer
        assert set(get_allowed_transitions(JobStatus.ASSIGNED, UserRole.ENGINEER)) == {
            JobStatus.PENDING_PICKUP_FOR_LAB,
            JobStatus.PENDING_VISIT,
        }
        
        assert set(get_allowed_transitions(JobStatus.ON_SITE_DIAGNOSIS, UserRole.ENGINEER)) == {
            JobStatus.REPAIR_IN_PROGRESS_ON_SITE,
            JobStatus.PENDING_QUOTE_APPROVAL,
            JobStatus.ESCALATED_TO_LAB
        }
        
        # Engineers can't assign jobs
        assert len(get_allowed_transitions(JobStatus.PENDING_ASSIGNMENT, UserRole.ENGINEER)) == 0
        
        # Terminal states should have no transitions
        assert len(get_allowed_transitions(JobStatus.COMPLETED, UserRole.ENGINEER)) == 0

    def test_get_allowed_transitions_customer(self):
        """Test getting allowed transitions for customer role."""
        # Test a few key status points for customer
        assert set(get_allowed_transitions(JobStatus.PENDING_ASSIGNMENT, UserRole.CUSTOMER)) == {
            JobStatus.CANCELLED
        }
        
        assert set(get_allowed_transitions(JobStatus.PENDING_QUOTE_APPROVAL, UserRole.CUSTOMER)) == {
            JobStatus.REPAIR_IN_PROGRESS_LAB,
            JobStatus.REPAIR_IN_PROGRESS_ON_SITE,
            JobStatus.CANCELLED
        }
        
        # Customers can't make changes during most operational steps
        assert len(get_allowed_transitions(JobStatus.ON_SITE_DIAGNOSIS, UserRole.CUSTOMER)) == 0
        
        # Terminal states should have no transitions
        assert len(get_allowed_transitions(JobStatus.COMPLETED, UserRole.CUSTOMER)) == 0

    def test_get_allowed_transitions_unknown_role(self):
        """Test getting allowed transitions for unknown role."""
        # Unknown roles should have no transitions
        assert len(get_allowed_transitions(JobStatus.PENDING_ASSIGNMENT, "UNKNOWN_ROLE")) == 0 