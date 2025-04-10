from typing import List, Optional, Dict, Any, Union
from uuid import UUID

from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder

from wellfix_api.models.user import User, UserRole
from wellfix_api.schemas import UserCreate, UserUpdate
from wellfix_api.core.security import get_password_hash

def get_user(db: Session, user_id: UUID) -> Optional[User]:
    """Get a user by ID."""
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get a user by email."""
    return db.query(User).filter(User.email == email).first()

def get_users(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    role: Optional[UserRole] = None
) -> List[User]:
    """Get a list of users with optional filtering by role."""
    query = db.query(User)
    if role:
        query = query.filter(User.role == role)
    return query.offset(skip).limit(limit).all()

def create_user(db: Session, user_in: UserCreate) -> User:
    """Create a new user."""
    # Convert UserCreate to dict and replace password with hashed version
    user_data = user_in.model_dump(exclude={"password"})
    hashed_password = get_password_hash(user_in.password)
    
    db_user = User(
        **user_data,
        password_hash=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(
    db: Session, 
    user: User,
    user_in: Union[UserUpdate, Dict[str, Any]]
) -> User:
    """Update a user."""
    # Convert to dict if it's a schema
    if isinstance(user_in, dict):
        update_data = user_in
    else:
        update_data = user_in.model_dump(exclude_unset=True)
    
    # If password is provided, hash it
    if "password" in update_data:
        update_data["password_hash"] = get_password_hash(update_data.pop("password"))
        
    # Update user attributes
    for field, value in update_data.items():
        if hasattr(user, field) and value is not None:
            setattr(user, field, value)
    
    db.add(user)
    db.commit()
    db.refresh(user)
    return user 