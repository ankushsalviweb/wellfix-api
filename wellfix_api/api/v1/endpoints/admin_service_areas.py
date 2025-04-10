from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from wellfix_api.core.db import get_db
from wellfix_api.core.dependencies import require_admin, get_current_user
from wellfix_api.models.user import User
from wellfix_api.schemas.service_area import (
    ServiceableArea, 
    ServiceableAreaCreate, 
    ServiceableAreaUpdate,
    ServiceableAreaList
)
from wellfix_api.crud.crud_service_area import (
    get_service_area,
    list_service_areas,
    create_service_area,
    update_service_area
)

# Change router to not include prefix since it's already set in the main API router
router = APIRouter()

@router.get("", response_model=ServiceableAreaList)
async def get_all_serviceable_areas(
    skip: int = Query(0, ge=0, description="Number of areas to skip"),
    limit: int = Query(100, ge=1, le=100, description="Max number of areas to return"),
    active_only: bool = Query(False, description="Filter to only active areas"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
) -> Any:
    """
    Get all serviceable areas with pagination.
    
    Admin access required.
    """
    areas, total = list_service_areas(db, skip=skip, limit=limit, active_only=active_only)
    
    # Convert DB models to response schema
    response_areas = []
    for area in areas:
        # Get admin name if available
        admin_name = None
        if area.created_by and area.created_by.first_name and area.created_by.last_name:
            admin_name = f"{area.created_by.first_name} {area.created_by.last_name}"
        
        # Convert to response schema
        response_area = ServiceableArea.model_validate(area, from_attributes=True)
        response_area.admin_name = admin_name
        response_areas.append(response_area)
    
    return ServiceableAreaList(total=total, items=response_areas)

@router.post("", response_model=ServiceableArea, status_code=status.HTTP_201_CREATED)
async def create_serviceable_area(
    service_area: ServiceableAreaCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
) -> Any:
    """
    Create a new serviceable area.
    
    Admin access required.
    """
    # Check if the pincode already exists
    existing_area = get_service_area(db, service_area.pincode)
    if existing_area:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Pincode '{service_area.pincode}' is already registered"
        )
    
    # Create the new area
    db_area = create_service_area(db, service_area, current_user.id)
    
    # Add admin name to response
    response_area = ServiceableArea.model_validate(db_area, from_attributes=True)
    if current_user.first_name and current_user.last_name:
        response_area.admin_name = f"{current_user.first_name} {current_user.last_name}"
    
    return response_area

@router.patch("/{pincode}", response_model=ServiceableArea)
async def update_serviceable_area_status(
    pincode: str,
    update_data: ServiceableAreaUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
) -> Any:
    """
    Update a serviceable area status (active/inactive).
    
    Admin access required.
    """
    # Update the area
    db_area = update_service_area(db, pincode, update_data)
    if not db_area:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pincode '{pincode}' not found"
        )
    
    # Add admin name to response
    response_area = ServiceableArea.model_validate(db_area, from_attributes=True)
    if db_area.created_by and db_area.created_by.first_name and db_area.created_by.last_name:
        response_area.admin_name = f"{db_area.created_by.first_name} {db_area.created_by.last_name}"
    
    return response_area

@router.get("/{pincode}", response_model=ServiceableArea)
async def get_serviceable_area(
    pincode: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
) -> Any:
    """
    Get details for a specific serviceable area.
    
    Admin access required.
    """
    db_area = get_service_area(db, pincode)
    if not db_area:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pincode '{pincode}' not found"
        )
    
    # Add admin name to response
    response_area = ServiceableArea.model_validate(db_area, from_attributes=True)
    if db_area.created_by and db_area.created_by.first_name and db_area.created_by.last_name:
        response_area.admin_name = f"{db_area.created_by.first_name} {db_area.created_by.last_name}"
    
    return response_area 