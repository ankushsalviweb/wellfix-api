"""
API endpoints for user profiles.
"""

from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from wellfix_api.core.db import get_db
from wellfix_api.core.dependencies import get_current_user
from wellfix_api.models.user import User

router = APIRouter()

@router.get("/me", response_model=dict)
async def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get current user's profile information.
    """
    # This is a placeholder that returns basic user info
    # In a real implementation, you would return the user's profile data
    return {
        "id": current_user.id,
        "email": current_user.email,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "role": current_user.role
    } 