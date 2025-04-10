from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from wellfix_api.core.db import get_db
from wellfix_api.core.dependencies import require_admin
from wellfix_api.schemas import User, UserCreate, UserUpdate
from wellfix_api.models.user import User as DBUser, UserRole
from wellfix_api.crud import get_users, get_user, create_user, update_user

router = APIRouter()

@router.get("", response_model=List[User])
def read_users(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    role: Optional[UserRole] = Query(None, description="Filter users by role"),
    _: DBUser = Depends(require_admin)
) -> Any:
    """
    Get list of users. Admin only.
    """
    users = get_users(db, skip=skip, limit=limit, role=role)
    return users

@router.post("", response_model=User, status_code=status.HTTP_201_CREATED)
def create_admin_or_engineer(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    _: DBUser = Depends(require_admin)
) -> Any:
    """
    Create new admin or engineer user. Admin only.
    """
    # Ensure only Admin or Engineer roles can be created
    if user_in.role not in [UserRole.ADMIN, UserRole.ENGINEER]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Only Admin or Engineer roles can be created through this endpoint"
        )
    
    # Check if email already exists
    user = db.query(DBUser).filter(DBUser.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Email already registered"
        )
    
    return create_user(db, user_in=user_in)

@router.get("/{user_id}", response_model=User)
def read_user(
    user_id: str,
    db: Session = Depends(get_db),
    _: DBUser = Depends(require_admin)
) -> Any:
    """
    Get a specific user by ID. Admin only.
    """
    user = get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.patch("/{user_id}", response_model=User)
def update_user_admin(
    user_id: str,
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_admin: DBUser = Depends(require_admin)
) -> Any:
    """
    Update a user. Admin only.
    """
    user = get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent self-deactivation
    if str(user.id) == str(current_admin.id) and user_in.is_active is False:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="You cannot deactivate your own account"
        )
    
    return update_user(db, user=user, user_in=user_in) 