"""
CRUD operations for pricing configurations.
"""

from typing import List, Optional, Dict, Any

from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from wellfix_api.models.pricing import PricingConfig
from wellfix_api.schemas.pricing import PricingConfigCreate, PricingConfigUpdate


def create_pricing_config(db: Session, config_in: PricingConfigCreate) -> PricingConfig:
    """
    Create a new pricing configuration.
    
    If is_default is True, make all other configs non-default first.
    """
    if config_in.is_default:
        # If this is set as default, unset all other defaults
        db.query(PricingConfig).filter(PricingConfig.is_default == True).update({"is_default": False})
    
    # Create the new config
    db_config = PricingConfig(
        name=config_in.name,
        description=config_in.description,
        base_diagnostic_fee=config_in.base_diagnostic_fee,
        base_onsite_fee=config_in.base_onsite_fee,
        hourly_rate_hardware=config_in.hourly_rate_hardware,
        hourly_rate_software=config_in.hourly_rate_software,
        hourly_rate_network=config_in.hourly_rate_network,
        emergency_surcharge_percentage=config_in.emergency_surcharge_percentage,
        weekend_surcharge_percentage=config_in.weekend_surcharge_percentage,
        evening_surcharge_percentage=config_in.evening_surcharge_percentage,
        distance_surcharge_per_mile=config_in.distance_surcharge_per_mile,
        base_service_radius_miles=config_in.base_service_radius_miles,
        is_active=config_in.is_active,
        is_default=config_in.is_default
    )
    
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    
    return db_config


def get_pricing_config(db: Session, config_id: int) -> Optional[PricingConfig]:
    """
    Get a pricing configuration by ID.
    """
    return db.query(PricingConfig).filter(PricingConfig.id == config_id).first()


def get_default_pricing_config(db: Session) -> Optional[PricingConfig]:
    """
    Get the default pricing configuration.
    
    Returns the active default configuration, or any active configuration if no default exists.
    """
    # First, try to get the active default config
    default_config = db.query(PricingConfig).filter(
        PricingConfig.is_default == True,
        PricingConfig.is_active == True
    ).first()
    
    # If no active default exists, return any active config
    if not default_config:
        default_config = db.query(PricingConfig).filter(
            PricingConfig.is_active == True
        ).first()
    
    return default_config


def list_pricing_configs(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None
) -> Dict[str, Any]:
    """
    List pricing configurations with optional filtering.
    
    Args:
        db: Database session
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return (pagination)
        is_active: Optional filter for active status
        
    Returns:
        Dictionary with 'count' and 'pricing_configs' fields
    """
    query = db.query(PricingConfig)
    
    # Apply filters if provided
    if is_active is not None:
        query = query.filter(PricingConfig.is_active == is_active)
    
    # Get total count for pagination
    total = query.count()
    
    # Apply pagination
    configs = query.order_by(PricingConfig.id).offset(skip).limit(limit).all()
    
    return {
        "count": total,
        "pricing_configs": configs
    }


def update_pricing_config(
    db: Session,
    config_id: int,
    config_in: PricingConfigUpdate
) -> Optional[PricingConfig]:
    """
    Update a pricing configuration.
    
    If is_default is being set to True, make all other configs non-default first.
    """
    db_config = get_pricing_config(db, config_id)
    if not db_config:
        return None
    
    # If setting this config as default, unset other defaults
    if config_in.is_default and config_in.is_default != db_config.is_default:
        db.query(PricingConfig).filter(
            PricingConfig.is_default == True,
            PricingConfig.id != config_id
        ).update({"is_default": False})
    
    # Update config with provided values
    update_data = config_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_config, field, value)
    
    db.commit()
    db.refresh(db_config)
    
    return db_config


def delete_pricing_config(db: Session, config_id: int) -> bool:
    """
    Delete a pricing configuration.
    
    If the config is the default, another config will be set as default if available.
    """
    db_config = get_pricing_config(db, config_id)
    if not db_config:
        return False
    
    # Check if this is the default config
    was_default = db_config.is_default
    
    # Delete the config
    db.delete(db_config)
    
    # If this was the default, set another config as default if available
    if was_default:
        # Find another active config
        new_default = db.query(PricingConfig).filter(
            PricingConfig.is_active == True
        ).first()
        
        if new_default:
            new_default.is_default = True
    
    db.commit()
    return True 