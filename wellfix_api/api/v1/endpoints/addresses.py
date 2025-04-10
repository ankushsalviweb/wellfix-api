"""
API endpoints for address management.
"""

from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.orm import Session
from uuid import UUID

from wellfix_api.core.db import get_db
from wellfix_api.core.dependencies import get_current_user
from wellfix_api.models.user import User
from wellfix_api.schemas.address import Address, AddressList, AddressCreate, AddressUpdate
from wellfix_api.crud import crud_address, crud_service_area
from wellfix_api.core import error_messages as em

router = APIRouter(tags=["Addresses"])

@router.get("", response_model=AddressList)
async def list_addresses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Retrieve addresses for the authenticated user.
    """
    addresses = crud_address.get_user_addresses(db, current_user.id)
    return {
        "items": addresses,
        "total": len(addresses)
    }

@router.post("", response_model=Address, status_code=status.HTTP_201_CREATED)
async def create_address(
    address_in: AddressCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Create a new address for the authenticated user.
    
    Validates that the provided pincode is in a serviceable area before creating.
    """
    # Validate that the pincode is in a serviceable area
    is_serviceable = crud_service_area.is_pincode_serviceable(db, address_in.pincode)
    if not is_serviceable:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=em.JOB_LOCATION_NOT_SERVICEABLE
        )
    
    # Create the address
    return crud_address.create_user_address(db, address_in, current_user.id)

@router.get("/{address_id}", response_model=Address)
async def get_address(
    address_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Retrieve a specific address by ID.
    
    Users can only access their own addresses.
    """
    address = crud_address.get_address(db, address_id)
    if not address or address.user_id != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=em.not_found("Address", str(address_id))
        )
    return address

@router.patch("/{address_id}", response_model=Address)
async def update_address(
    address_id: UUID,
    address_in: AddressUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Update an address.
    
    Users can only update their own addresses.
    If updating the pincode, validates that the new pincode is in a serviceable area.
    """
    # Get the address and check ownership
    address = crud_address.get_address(db, address_id)
    if not address or address.user_id != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=em.not_found("Address", str(address_id))
        )
    
    # If updating pincode, validate it's serviceable
    update_data = address_in.model_dump(exclude_unset=True)
    if "pincode" in update_data:
        is_serviceable = crud_service_area.is_pincode_serviceable(db, update_data["pincode"])
        if not is_serviceable:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=em.JOB_LOCATION_NOT_SERVICEABLE
            )
    
    # Update the address
    return crud_address.update_address(db, address, address_in)

@router.delete("/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_address(
    address_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> None:
    """
    Delete an address.
    
    Users can only delete their own addresses.
    """
    # Get the address and check ownership
    address = crud_address.get_address(db, address_id)
    if not address or address.user_id != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=em.not_found("Address", str(address_id))
        )
    
    # Delete the address
    crud_address.delete_address(db, address)
    return None 