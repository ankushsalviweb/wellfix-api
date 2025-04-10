"""
Centralized error messages for consistent API responses.
"""

# Authentication and authorization errors
INVALID_CREDENTIALS = "Invalid credentials"
INACTIVE_USER = "Inactive user account"
PERMISSION_DENIED = "Insufficient permissions to perform this action"
TOKEN_EXPIRED = "Authentication token has expired"

# Resource errors
NOT_FOUND_TEMPLATE = "{resource_type} with ID {resource_id} not found"
ALREADY_EXISTS = "{resource_type} already exists"
DUPLICATE_ENTITY = "{resource_type} with this {field} already exists"

# Input validation errors
INVALID_INPUT = "Invalid input data"
INVALID_STATUS_TRANSITION = "Invalid status transition from {current_status} to {new_status}"

# Business logic errors
RELATED_ENTITY_NOT_FOUND = "Related {entity_type} with ID {entity_id} not found"
BUSINESS_RULE_VIOLATION = "{message}"

# Server errors
INTERNAL_SERVER_ERROR = "An internal server error occurred"
DATABASE_ERROR = "A database error occurred"

def not_found(resource_type: str, resource_id: str) -> str:
    """Generate a standardized not found error message."""
    return NOT_FOUND_TEMPLATE.format(resource_type=resource_type, resource_id=resource_id)

def already_exists(resource_type: str, field: str, value: str) -> str:
    """Generate a standardized already exists error message."""
    return DUPLICATE_ENTITY.format(resource_type=resource_type, field=field, value=value)

def invalid_status_transition(current_status: str, new_status: str, role: str = None) -> str:
    """Generate a standardized invalid status transition error message."""
    base_message = INVALID_STATUS_TRANSITION.format(
        current_status=current_status, 
        new_status=new_status
    )
    if role:
        return f"{base_message} for {role}"
    return base_message

# Resource errors
RESOURCE_IN_USE = "Resource is currently in use"

# Request errors
MISSING_REQUIRED_FIELD = "Missing required field"
INVALID_FIELD_FORMAT = "Invalid field format"
INVALID_ENUM_VALUE = "Invalid enum value"
PAGINATION_LIMIT_EXCEEDED = "Pagination limit exceeded"

# Business logic errors
INVALID_OPERATION = "Operation not allowed"
RESOURCE_CONFLICT = "Resource conflict"
INSUFFICIENT_FUNDS = "Insufficient funds"

# Server errors
EXTERNAL_SERVICE_ERROR = "External service error"

# Rating errors
RATING_ALREADY_EXISTS = "Rating already exists for this job"
JOB_NOT_COMPLETED = "Job must be completed before rating"

# Job errors
JOB_ALREADY_ASSIGNED = "Job already assigned to an engineer"
JOB_NOT_ASSIGNABLE = "Job cannot be assigned in its current state"
JOB_NOT_CANCELLABLE = "Job cannot be cancelled in its current state"
JOB_LOCATION_NOT_SERVICEABLE = "Job location is not in a serviceable area"

# Pricing errors
PRICING_VALIDATION_ERROR = "Pricing validation error"
DEFAULT_PRICING_REQUIRED = "At least one active default pricing configuration is required"

# Helper functions
def invalid_enum_value(field: str, valid_values: list) -> str:
    """Generate a standardized invalid enum value message."""
    valid_values_str = ", ".join(str(v) for v in valid_values)
    return f"Invalid {field}. Valid values are: {valid_values_str}"

def field_required(field: str) -> str:
    """Generate a standardized field required message."""
    return f"Field '{field}' is required" 