from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func

from wellfix_api.models.service_area import ServiceableArea
from wellfix_api.schemas.service_area import ServiceableAreaCreate, ServiceableAreaUpdate


def get_service_area(db: Session, pincode: str) -> Optional[ServiceableArea]:
    """
    Get a serviceable area by pincode.
    
    Args:
        db: Database session
        pincode: The pincode to look up
        
    Returns:
        ServiceableArea object if found, None otherwise
    """
    return db.query(ServiceableArea).filter(ServiceableArea.pincode == pincode).first()


def get_active_service_area(db: Session, pincode: str) -> Optional[ServiceableArea]:
    """
    Get an active serviceable area by pincode.
    
    Args:
        db: Database session
        pincode: The pincode to look up
        
    Returns:
        ServiceableArea object if found and active, None otherwise
    """
    return db.query(ServiceableArea).filter(
        ServiceableArea.pincode == pincode,
        ServiceableArea.is_active == True
    ).first()


def is_pincode_serviceable(db: Session, pincode: str) -> bool:
    """
    Check if a pincode is active in serviceable areas.
    
    Args:
        db: Database session
        pincode: The pincode to check
        
    Returns:
        True if the pincode is serviceable, False otherwise
    """
    area = get_active_service_area(db, pincode)
    return area is not None


def list_service_areas(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    active_only: bool = False
) -> Tuple[List[ServiceableArea], int]:
    """
    List serviceable areas with pagination.
    
    Args:
        db: Database session
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
        active_only: If True, only return active serviceable areas
        
    Returns:
        Tuple containing (list of ServiceableArea objects, total count)
    """
    query = db.query(ServiceableArea)
    
    if active_only:
        query = query.filter(ServiceableArea.is_active == True)
    
    # Get total count for pagination
    total = query.count()
    
    # Apply pagination
    service_areas = query.order_by(ServiceableArea.pincode).offset(skip).limit(limit).all()
    
    return service_areas, total


def create_service_area(
    db: Session, 
    service_area: ServiceableAreaCreate, 
    admin_id: str
) -> ServiceableArea:
    """
    Create a new serviceable area.
    
    Args:
        db: Database session
        service_area: ServiceableAreaCreate schema with area data
        admin_id: ID of the admin creating the area
        
    Returns:
        The created ServiceableArea object
    """
    db_service_area = ServiceableArea(
        pincode=service_area.pincode,
        is_active=service_area.is_active,
        added_by_admin_id=admin_id
    )
    db.add(db_service_area)
    db.commit()
    db.refresh(db_service_area)
    return db_service_area


def update_service_area(
    db: Session, 
    pincode: str, 
    service_area_update: ServiceableAreaUpdate
) -> Optional[ServiceableArea]:
    """
    Update a serviceable area.
    
    Args:
        db: Database session
        pincode: The pincode of the area to update
        service_area_update: ServiceableAreaUpdate schema with fields to update
        
    Returns:
        Updated ServiceableArea object if found, None otherwise
    """
    db_service_area = get_service_area(db, pincode)
    if not db_service_area:
        return None
    
    # Update fields that are not None
    update_data = service_area_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_service_area, key, value)
    
    db.commit()
    db.refresh(db_service_area)
    return db_service_area 