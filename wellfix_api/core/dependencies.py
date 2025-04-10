from typing import Generator, Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from pydantic import ValidationError
import logging

from wellfix_api.core.config import settings
from wellfix_api.core.db import get_db
from wellfix_api.models.user import User, UserRole
from wellfix_api.crud import get_user
from wellfix_api.schemas import TokenData
from wellfix_api.core import error_messages as em

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# OAuth2 token URL - will be used in Swagger UI
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


def validate_token(token: str) -> TokenData:
    """
    Validate JWT token and extract user ID.
    
    Args:
        token: JWT token
        
    Returns:
        TokenData containing validated user ID
        
    Raises:
        HTTPException: If token is invalid
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=em.INVALID_CREDENTIALS,
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode JWT token
        logger.debug(f"Decoding token with JWT algorithm: {settings.JWT_ALGORITHM}")
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id_str: str = payload.get("sub")
        logger.debug(f"Decoded user_id: {user_id_str}")
        
        if user_id_str is None:
            logger.error("No user_id found in token")
            raise credentials_exception
        
        # Validate token data
        token_data = TokenData(user_id=UUID(user_id_str))
        return token_data
        
    except (JWTError, ValidationError) as e:
        logger.error(f"JWT validation error: {str(e)}")
        raise credentials_exception


def get_user_by_id(db: Session, user_id: UUID) -> User:
    """
    Get user by ID from database.
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        User if found
        
    Raises:
        HTTPException: If user not found or inactive
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=em.INVALID_CREDENTIALS,
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Direct query for better debugging
        logger.debug(f"Querying for user with ID: {user_id}")
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            logger.error(f"User with ID {user_id} not found in database")
            # Try a raw query to see all users in the database for debugging
            all_users = db.query(User).all()
            logger.info(f"Current users in DB: {[u.email for u in all_users]}")
            raise credentials_exception
            
        # Check if user is active
        if not user.is_active:
            logger.error(f"User with ID {user_id} is inactive")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=em.INACTIVE_USER
            )
            
        return user
        
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise credentials_exception


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    Validate access token and return current user.
    Raise HTTP 401 if token invalid or user not found.
    """
    # Validate token and extract user ID
    token_data = validate_token(token)
    
    # Get user from database
    return get_user_by_id(db, token_data.user_id)


def require_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependency requiring admin role.
    Raise HTTP 403 if user is not an admin.
    """
    if current_user.role != UserRole.ADMIN:
        logger.warning(f"Non-admin user {current_user.id} attempted to access admin resource")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This action requires admin privileges"
        )
    return current_user 