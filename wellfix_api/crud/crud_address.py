from typing import List, Optional, Dict, Any, Union
from uuid import UUID

from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder

from wellfix_api.models.address import Address
from wellfix_api.schemas import AddressCreate, AddressUpdate

def create_user_address(
    db: Session, 
    address_in: AddressCreate, 
    user_id: UUID
) -> Address:
    """Create a new address for a user."""
    # Check if this will be the first address
    is_first_address = db.query(Address).filter(Address.user_id == user_id).count() == 0
    
    # If this is the first address, make it default regardless of input
    if is_first_address:
        address_in_data = address_in.model_dump()
        address_in_data["is_default"] = True
    else:
        address_in_data = address_in.model_dump()
        # If setting this address as default, unset default on all other addresses
        if address_in_data.get("is_default", False):
            db.query(Address).filter(
                Address.user_id == user_id,
                Address.is_default == True
            ).update({"is_default": False})
    
    db_address = Address(**address_in_data, user_id=user_id)
    db.add(db_address)
    db.commit()
    db.refresh(db_address)
    return db_address

def get_user_addresses(db: Session, user_id: UUID) -> List[Address]:
    """Get all addresses for a user."""
    return db.query(Address).filter(Address.user_id == user_id).all()

def get_address(db: Session, address_id: UUID) -> Optional[Address]:
    """Get an address by ID."""
    return db.query(Address).filter(Address.id == address_id).first()

def update_address(
    db: Session,
    address: Address,
    address_in: Union[AddressUpdate, Dict[str, Any]]
) -> Address:
    """Update an address."""
    # Convert to dict if it's a schema
    if isinstance(address_in, dict):
        update_data = address_in
    else:
        update_data = address_in.model_dump(exclude_unset=True)
    
    # If setting this as default, unset others
    if update_data.get("is_default", False) and not address.is_default:
        db.query(Address).filter(
            Address.user_id == address.user_id,
            Address.is_default == True
        ).update({"is_default": False})
    
    # Update address attributes
    for field, value in update_data.items():
        if hasattr(address, field) and value is not None:
            setattr(address, field, value)
    
    db.add(address)
    db.commit()
    db.refresh(address)
    return address

def delete_address(db: Session, address: Address) -> None:
    """Delete an address."""
    # Check if it's the default address
    was_default = address.is_default
    user_id = address.user_id
    
    # Delete the address
    db.delete(address)
    db.commit()
    
    # If it was the default and there are other addresses, make one of them default
    if was_default:
        remaining_address = db.query(Address).filter(
            Address.user_id == user_id
        ).first()
        
        if remaining_address:
            remaining_address.is_default = True
            db.add(remaining_address)
            db.commit() 