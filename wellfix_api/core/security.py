from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Union

from passlib.context import CryptContext
from jose import jwt
from uuid import UUID

from wellfix_api.core.config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Create a password hash."""
    return pwd_context.hash(password)

def create_access_token(
    subject: Union[str, UUID], 
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token.
    
    Args:
        subject: The subject of the token, typically user ID.
        expires_delta: Optional expiration time, defaults to settings.ACCESS_TOKEN_EXPIRE_MINUTES.
        
    Returns:
        Encoded JWT token string.
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    # Convert UUID to string if needed
    if isinstance(subject, UUID):
        subject = str(subject)
        
    to_encode = {"exp": expire, "sub": subject}
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.JWT_SECRET_KEY, 
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt 