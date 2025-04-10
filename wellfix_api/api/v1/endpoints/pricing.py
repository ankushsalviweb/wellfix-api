"""
API endpoints for managing pricing configurations.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from wellfix_api.core.db import get_db
from wellfix_api.core.dependencies import get_current_user, require_admin as get_current_admin_user
from wellfix_api.models.user import User
from wellfix_api.models.enums import RepairType
from wellfix_api.crud import pricing as pricing_crud
from wellfix_api.schemas.pricing import (
    PricingConfigCreate,
    PricingConfigUpdate,
    PricingConfigResponse,
    PricingConfigListResponse,
)


router = APIRouter(tags=["pricing"])


@router.get("", response_model=PricingConfigListResponse)
def list_pricing_configs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    repair_type: Optional[str] = Query(None, description="Filter by repair type"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    search: Optional[str] = Query(None, description="Search term for item name or description"),
    sort_by: str = Query("id", description="Field to sort by"),
    sort_order: str = Query("asc", description="Sort order (asc or desc)"),
):
    """
    List pricing configurations with optional filtering and sorting.
    
    This endpoint is accessible to all authenticated users, but primarily intended for:
    - Engineers: To view available pricing configurations
    - Admins: To manage pricing configurations
    """
    # Validate repair_type if provided
    if repair_type:
        try:
            RepairType(repair_type)
        except ValueError:
            valid_types = [t.value for t in RepairType]
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid repair type. Must be one of: {', '.join(valid_types)}"
            )
    
    # Validate sort_by
    allowed_sort_fields = ["id", "item_name", "repair_type", "base_price", "is_active", "created_at", "updated_at"]
    if sort_by not in allowed_sort_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid sort field. Must be one of: {', '.join(allowed_sort_fields)}"
        )
    
    # Validate sort_order
    if sort_order.lower() not in ["asc", "desc"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sort order must be 'asc' or 'desc'"
        )
    
    # Get pricing configurations
    pricing_configs, total = pricing_crud.get_pricing_configs(
        db=db,
        skip=skip,
        limit=limit,
        repair_type=repair_type,
        is_active=is_active,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    return {
        "pricing_configs": pricing_configs,
        "count": total
    }


@router.get("/{pricing_config_id}", response_model=PricingConfigResponse)
def get_pricing_config(
    pricing_config_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get a specific pricing configuration by ID.
    
    This endpoint is accessible to all authenticated users.
    """
    pricing_config = pricing_crud.get_pricing_config(db, pricing_config_id)
    if not pricing_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pricing configuration not found"
        )
    return pricing_config


@router.post("", response_model=PricingConfigResponse, status_code=status.HTTP_201_CREATED)
def create_pricing_config(
    pricing_config_in: PricingConfigCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user),
):
    """
    Create a new pricing configuration.
    
    This endpoint is only accessible to admin users.
    """
    return pricing_crud.create_pricing_config(db, pricing_config_in, current_admin)


@router.patch("/{pricing_config_id}", response_model=PricingConfigResponse)
def update_pricing_config(
    pricing_config_id: int,
    pricing_config_in: PricingConfigUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user),
):
    """
    Update an existing pricing configuration.
    
    This endpoint is only accessible to admin users.
    """
    pricing_config = pricing_crud.update_pricing_config(db, pricing_config_id, pricing_config_in, current_admin)
    if not pricing_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pricing configuration not found"
        )
    return pricing_config


@router.delete("/{pricing_config_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_pricing_config(
    pricing_config_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user),
):
    """
    Delete a pricing configuration.
    
    This endpoint is only accessible to admin users.
    """
    result = pricing_crud.delete_pricing_config(db, pricing_config_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pricing configuration not found"
        )
    return None 