"""
API endpoints for admin pricing configuration management.
"""

from typing import Optional, Any
import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from wellfix_api.core.db import get_db
from wellfix_api.core.dependencies import require_admin as get_current_admin_user
from wellfix_api.crud import crud_pricing
from wellfix_api.schemas.pricing import (
    PricingConfigResponse,
    PricingConfigCreate, 
    PricingConfigUpdate,
    PricingConfigListResponse
)
from wellfix_api.core import error_messages as em

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=PricingConfigListResponse)
def list_pricing_configs(
    *,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    current_user = Depends(get_current_admin_user)
) -> Any:
    """
    List pricing configurations with optional filtering.
    
    Only accessible by admin users.
    """
    try:
        result = crud_pricing.list_pricing_configs(
            db=db,
            skip=skip,
            limit=limit,
            is_active=is_active
        )
        return result
    except Exception as e:
        logger.error(f"Error listing pricing configs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=em.INTERNAL_SERVER_ERROR
        )


@router.post("/", response_model=PricingConfigResponse, status_code=status.HTTP_201_CREATED)
def create_pricing_config(
    *,
    db: Session = Depends(get_db),
    config_in: PricingConfigCreate,
    current_user = Depends(get_current_admin_user)
) -> Any:
    """
    Create a new pricing configuration.
    
    Only accessible by admin users.
    """
    try:
        # Create the new pricing config
        new_config = crud_pricing.create_pricing_config(db=db, config_in=config_in)
        return new_config
    except ValueError as e:
        logger.warning(f"Validation error creating pricing config: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating pricing config: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=em.INTERNAL_SERVER_ERROR
        )


@router.get("/{config_id}", response_model=PricingConfigResponse)
def get_pricing_config(
    *,
    db: Session = Depends(get_db),
    config_id: int,
    current_user = Depends(get_current_admin_user)
) -> Any:
    """
    Get a specific pricing configuration by ID.
    
    Only accessible by admin users.
    """
    try:
        config = crud_pricing.get_pricing_config(db=db, config_id=config_id)
        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=em.not_found("Pricing configuration", str(config_id))
            )
        return config
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving pricing config {config_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=em.INTERNAL_SERVER_ERROR
        )


@router.patch("/{config_id}", response_model=PricingConfigResponse)
def update_pricing_config(
    *,
    db: Session = Depends(get_db),
    config_id: int,
    config_in: PricingConfigUpdate,
    current_user = Depends(get_current_admin_user)
) -> Any:
    """
    Update a pricing configuration.
    
    Only accessible by admin users.
    """
    try:
        # Check if the config exists
        existing_config = crud_pricing.get_pricing_config(db=db, config_id=config_id)
        if not existing_config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=em.not_found("Pricing configuration", str(config_id))
            )
        
        # Update the config
        updated_config = crud_pricing.update_pricing_config(
            db=db, 
            config_id=config_id, 
            config_in=config_in
        )
        
        return updated_config
    except ValueError as e:
        logger.warning(f"Validation error updating pricing config {config_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=em.BUSINESS_RULE_VIOLATION.format(message=str(e))
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating pricing config {config_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=em.INTERNAL_SERVER_ERROR
        )


@router.delete("/{config_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
def delete_pricing_config(
    *,
    db: Session = Depends(get_db),
    config_id: int,
    current_user = Depends(get_current_admin_user)
) -> None:
    """
    Delete a pricing configuration.
    
    Only accessible by admin users.
    """
    try:
        # Try to delete the config
        success = crud_pricing.delete_pricing_config(db=db, config_id=config_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=em.not_found("Pricing configuration", str(config_id))
            )
        
        # Return None for status code 204 - No Content
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting pricing config {config_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=em.INTERNAL_SERVER_ERROR
        ) 