from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from wellfix_api.core.db import get_db
from wellfix_api.core.dependencies import get_current_user
from wellfix_api.schemas import User, UserUpdate, Address, AddressCreate, AddressUpdate
from wellfix_api.models.user import User as DBUser
from wellfix_api.models.address import Address as DBAddress
from wellfix_api.crud import update_user, get_user_addresses, create_user_address, get_address, update_address, delete_address

router = APIRouter()

@router.get("/me", response_model=User)
def read_user_me(
    current_user: DBUser = Depends(get_current_user)
) -> Any:
    """
    Get current user profile.
    """
    return current_user

@router.patch("/me", response_model=User)
def update_user_me(
    user_in: UserUpdate,
    current_user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Update current user profile.
    """
    # Admin role can't be self-assigned
    if user_in.role is not None and user_in.role != current_user.role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Role cannot be changed by the user"
        )
    
    user = update_user(db, user=current_user, user_in=user_in)
    return user

# --- Address Management ---

@router.get("/me/addresses", response_model=List[Address])
def read_user_addresses(
    current_user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get all addresses for current user.
    """
    return get_user_addresses(db, user_id=current_user.id)

@router.post("/me/addresses", response_model=Address, status_code=status.HTTP_201_CREATED)
def create_address(
    address_in: AddressCreate,
    current_user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Create a new address for current user.
    """
    # TODO: In a future phase, we would validate the pincode against ServiceableArea
    return create_user_address(db, address_in=address_in, user_id=current_user.id)

@router.get("/me/addresses/{address_id}", response_model=Address)
def read_address(
    address_id: str,
    current_user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get a specific address for current user.
    """
    address = get_address(db, address_id=address_id)
    if not address or address.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Address not found"
        )
    return address

@router.patch("/me/addresses/{address_id}", response_model=Address)
def update_user_address(
    address_id: str,
    address_in: AddressUpdate,
    current_user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Update a specific address for current user.
    """
    address = get_address(db, address_id=address_id)
    if not address or address.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Address not found"
        )
    
    # TODO: In a future phase, we would validate the pincode against ServiceableArea
    return update_address(db, address=address, address_in=address_in)

@router.delete("/me/addresses/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_address(
    address_id: str,
    current_user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> None:
    """
    Delete a specific address for current user.
    """
    address = get_address(db, address_id=address_id)
    if not address or address.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Address not found"
        )
    
    delete_address(db, address=address) 