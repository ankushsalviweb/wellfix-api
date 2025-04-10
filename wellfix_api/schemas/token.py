from typing import Optional
from pydantic import BaseModel
from uuid import UUID

class Token(BaseModel):
    """Token schema returned to clients after successful authentication."""
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """Data extracted from JWT token."""
    user_id: Optional[UUID] = None

class TokenPayload(BaseModel):
    """Payload schema for JWT token."""
    sub: Optional[str] = None
    exp: Optional[int] = None 