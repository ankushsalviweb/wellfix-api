from typing import Any
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from wellfix_api.core.db import get_db
from wellfix_api.core.dependencies import get_current_user
from wellfix_api.core.security import verify_password, create_access_token
from wellfix_api.schemas import User, UserCreate, Token
from wellfix_api.models.user import User as DBUser
from wellfix_api.crud import get_user_by_email, create_user

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(
    user_in: UserCreate,
    db: Session = Depends(get_db)
) -> Any:
    """
    Register a new customer user.
    """
    # Check if email already exists
    user = get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Email already registered"
        )
    
    # Create new user
    user = create_user(db, user_in=user_in)
    
    # Generate access token
    access_token = create_access_token(subject=user.id)
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.post("/login", response_model=Token)
def login(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    # Get user by email
    user = get_user_by_email(db, email=form_data.username)
    logger.info(f"Login attempt for email: {form_data.username}")
    
    # Check if user exists and password is correct
    if not user or not verify_password(form_data.password, user.password_hash):
        logger.warning(f"Login failed for email: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if not user.is_active:
        logger.warning(f"Login attempt for inactive user: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    # Generate access token
    logger.info(f"User authenticated successfully: {user.email}, ID: {user.id}")
    access_token = create_access_token(subject=user.id)
    logger.info(f"Access token created for user: {user.email}")
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.get("/me", response_model=User)
def read_users_me(
    current_user: DBUser = Depends(get_current_user)
) -> Any:
    """
    Get current user information.
    """
    logger.info(f"Returning current user info: {current_user.email}")
    return current_user 