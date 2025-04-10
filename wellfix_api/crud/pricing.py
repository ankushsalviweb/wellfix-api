"""
CRUD operations for pricing configurations.
"""
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import asc, desc, or_

from wellfix_api.models.pricing import PricingConfig
from wellfix_api.models.user import User
from wellfix_api.schemas.pricing import PricingConfigCreate, PricingConfigUpdate


def get_pricing_config(db: Session, pricing_config_id: int) -> Optional[PricingConfig]:
    """
    Get a single pricing configuration by ID.
    
    Args:
        db: Database session
        pricing_config_id: ID of the pricing configuration to retrieve
        
    Returns:
        The pricing configuration if found, None otherwise
    """
    return db.query(PricingConfig).filter(PricingConfig.id == pricing_config_id).first()


def get_pricing_configs(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    repair_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    sort_by: str = "id",
    sort_order: str = "asc"
) -> Tuple[List[PricingConfig], int]:
    """
    Get a list of pricing configurations with optional filtering and sorting.
    
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        repair_type: Filter by repair type
        is_active: Filter by active status
        search: Search term for item_name or description
        sort_by: Field to sort by
        sort_order: Sort order (asc or desc)
        
    Returns:
        A tuple containing the list of pricing configurations and the total count
    """
    query = db.query(PricingConfig)
    
    # Apply filters
    if repair_type:
        query = query.filter(PricingConfig.repair_type == repair_type)
    if is_active is not None:
        query = query.filter(PricingConfig.is_active == is_active)
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                PricingConfig.item_name.ilike(search_term),
                PricingConfig.description.ilike(search_term)
            )
        )
    
    # Get total count before pagination
    total = query.count()
    
    # Apply sorting
    sort_column = getattr(PricingConfig, sort_by, PricingConfig.id)
    if sort_order.lower() == "desc":
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(asc(sort_column))
    
    # Apply pagination
    return query.offset(skip).limit(limit).all(), total


def create_pricing_config(
    db: Session, 
    pricing_config: PricingConfigCreate, 
    admin: User
) -> PricingConfig:
    """
    Create a new pricing configuration.
    
    Args:
        db: Database session
        pricing_config: Pricing configuration data
        admin: The admin user creating the configuration
        
    Returns:
        The created pricing configuration
    """
    db_pricing_config = PricingConfig(
        repair_type=pricing_config.repair_type,
        item_name=pricing_config.item_name,
        description=pricing_config.description,
        base_price=pricing_config.base_price,
        is_active=pricing_config.is_active,
        updated_by_admin_id=admin.id
    )
    db.add(db_pricing_config)
    db.commit()
    db.refresh(db_pricing_config)
    return db_pricing_config


def update_pricing_config(
    db: Session, 
    pricing_config_id: int, 
    pricing_config_update: PricingConfigUpdate, 
    admin: User
) -> Optional[PricingConfig]:
    """
    Update an existing pricing configuration.
    
    Args:
        db: Database session
        pricing_config_id: ID of the pricing configuration to update
        pricing_config_update: Updated pricing configuration data
        admin: The admin user updating the configuration
        
    Returns:
        The updated pricing configuration if found, None otherwise
    """
    db_pricing_config = get_pricing_config(db, pricing_config_id)
    if not db_pricing_config:
        return None
    
    update_data = pricing_config_update.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(db_pricing_config, key, value)
    
    # Update the admin who made the change
    db_pricing_config.updated_by_admin_id = admin.id
    
    db.commit()
    db.refresh(db_pricing_config)
    return db_pricing_config


def delete_pricing_config(db: Session, pricing_config_id: int) -> bool:
    """
    Delete a pricing configuration.
    
    Args:
        db: Database session
        pricing_config_id: ID of the pricing configuration to delete
        
    Returns:
        True if the pricing configuration was deleted, False otherwise
    """
    db_pricing_config = get_pricing_config(db, pricing_config_id)
    if not db_pricing_config:
        return False
    
    db.delete(db_pricing_config)
    db.commit()
    return True 