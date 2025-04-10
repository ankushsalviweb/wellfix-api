"""
Unit tests for PricingConfig CRUD operations.
"""

import pytest
from sqlalchemy.orm import Session

from wellfix_api.crud import crud_pricing
from wellfix_api.schemas.pricing import PricingConfigCreate, PricingConfigUpdate
from wellfix_api.models.pricing import PricingConfig


def test_create_pricing_config(db: Session) -> None:
    """Test creating a pricing configuration."""
    config_in = PricingConfigCreate(
        name="Standard Pricing",
        description="Standard pricing for repair services",
        base_diagnostic_fee=50.0,
        base_onsite_fee=25.0,
        hourly_rate_hardware=75.0,
        hourly_rate_software=65.0,
        hourly_rate_network=70.0,
        is_default=True
    )
    
    config = crud_pricing.create_pricing_config(db=db, config_in=config_in)
    
    assert config.name == config_in.name
    assert config.description == config_in.description
    assert config.base_diagnostic_fee == config_in.base_diagnostic_fee
    assert config.is_default is True
    assert config.id is not None


def test_create_second_default_pricing_config(db: Session) -> None:
    """Test that creating a second default pricing config updates the first one."""
    # Create first default config
    config1_in = PricingConfigCreate(
        name="Standard Pricing",
        description="Standard pricing for repair services",
        base_diagnostic_fee=50.0,
        base_onsite_fee=25.0,
        hourly_rate_hardware=75.0,
        hourly_rate_software=65.0,
        hourly_rate_network=70.0,
        is_default=True
    )
    config1 = crud_pricing.create_pricing_config(db=db, config_in=config1_in)
    
    # Create second default config
    config2_in = PricingConfigCreate(
        name="Premium Pricing",
        description="Premium pricing for repair services",
        base_diagnostic_fee=75.0,
        base_onsite_fee=35.0,
        hourly_rate_hardware=95.0,
        hourly_rate_software=85.0,
        hourly_rate_network=90.0,
        is_default=True
    )
    config2 = crud_pricing.create_pricing_config(db=db, config_in=config2_in)
    
    # Refresh config1 from database
    db.refresh(config1)
    
    assert config1.is_default is False
    assert config2.is_default is True


def test_get_pricing_config(db: Session) -> None:
    """Test retrieving a pricing configuration by ID."""
    # Create a config
    config_in = PricingConfigCreate(
        name="Standard Pricing",
        description="Standard pricing for repair services",
        base_diagnostic_fee=50.0,
        base_onsite_fee=25.0,
        hourly_rate_hardware=75.0,
        hourly_rate_software=65.0,
        hourly_rate_network=70.0
    )
    created_config = crud_pricing.create_pricing_config(db=db, config_in=config_in)
    
    # Get the config
    retrieved_config = crud_pricing.get_pricing_config(db=db, config_id=created_config.id)
    
    assert retrieved_config is not None
    assert retrieved_config.id == created_config.id
    assert retrieved_config.name == created_config.name
    
    # Test non-existent config
    non_existent = crud_pricing.get_pricing_config(db=db, config_id=9999)
    assert non_existent is None


def test_get_default_pricing_config(db: Session) -> None:
    """Test retrieving the default pricing configuration."""
    # Create non-default config
    config1_in = PricingConfigCreate(
        name="Standard Pricing",
        description="Standard pricing for repair services",
        base_diagnostic_fee=50.0,
        base_onsite_fee=25.0,
        hourly_rate_hardware=75.0,
        hourly_rate_software=65.0,
        hourly_rate_network=70.0,
        is_default=False
    )
    crud_pricing.create_pricing_config(db=db, config_in=config1_in)
    
    # Create default config
    config2_in = PricingConfigCreate(
        name="Premium Pricing",
        description="Premium pricing for repair services",
        base_diagnostic_fee=75.0,
        base_onsite_fee=35.0,
        hourly_rate_hardware=95.0,
        hourly_rate_software=85.0,
        hourly_rate_network=90.0,
        is_default=True
    )
    created_default = crud_pricing.create_pricing_config(db=db, config_in=config2_in)
    
    # Get default config
    default_config = crud_pricing.get_default_pricing_config(db=db)
    
    assert default_config is not None
    assert default_config.id == created_default.id
    assert default_config.is_default is True


def test_list_pricing_configs(db: Session) -> None:
    """Test listing pricing configurations with filtering."""
    # Create multiple configs
    configs_data = [
        {
            "name": "Standard Pricing",
            "description": "Standard pricing for repair services",
            "base_diagnostic_fee": 50.0,
            "base_onsite_fee": 25.0,
            "hourly_rate_hardware": 75.0,
            "hourly_rate_software": 65.0,
            "hourly_rate_network": 70.0,
            "is_active": True
        },
        {
            "name": "Premium Pricing",
            "description": "Premium pricing for repair services",
            "base_diagnostic_fee": 75.0,
            "base_onsite_fee": 35.0,
            "hourly_rate_hardware": 95.0,
            "hourly_rate_software": 85.0,
            "hourly_rate_network": 90.0,
            "is_active": True
        },
        {
            "name": "Legacy Pricing",
            "description": "Old pricing structure",
            "base_diagnostic_fee": 40.0,
            "base_onsite_fee": 20.0,
            "hourly_rate_hardware": 60.0,
            "hourly_rate_software": 50.0,
            "hourly_rate_network": 55.0,
            "is_active": False
        }
    ]
    
    for config_data in configs_data:
        config_in = PricingConfigCreate(**config_data)
        crud_pricing.create_pricing_config(db=db, config_in=config_in)
    
    # List all configs
    result = crud_pricing.list_pricing_configs(db=db)
    assert result["count"] == 3
    assert len(result["pricing_configs"]) == 3
    
    # List only active configs
    active_result = crud_pricing.list_pricing_configs(db=db, is_active=True)
    assert active_result["count"] == 2
    assert len(active_result["pricing_configs"]) == 2
    
    # List only inactive configs
    inactive_result = crud_pricing.list_pricing_configs(db=db, is_active=False)
    assert inactive_result["count"] == 1
    assert len(inactive_result["pricing_configs"]) == 1
    assert inactive_result["pricing_configs"][0].name == "Legacy Pricing"


def test_update_pricing_config(db: Session) -> None:
    """Test updating a pricing configuration."""
    # Create a config
    config_in = PricingConfigCreate(
        name="Standard Pricing",
        description="Standard pricing for repair services",
        base_diagnostic_fee=50.0,
        base_onsite_fee=25.0,
        hourly_rate_hardware=75.0,
        hourly_rate_software=65.0,
        hourly_rate_network=70.0,
        is_default=False
    )
    created_config = crud_pricing.create_pricing_config(db=db, config_in=config_in)
    
    # Update the config
    update_data = PricingConfigUpdate(
        name="Updated Standard Pricing",
        base_diagnostic_fee=55.0,
        is_default=True
    )
    updated_config = crud_pricing.update_pricing_config(
        db=db, 
        config_id=created_config.id, 
        config_in=update_data
    )
    
    assert updated_config is not None
    assert updated_config.name == "Updated Standard Pricing"
    assert updated_config.base_diagnostic_fee == 55.0
    assert updated_config.base_onsite_fee == 25.0  # Unchanged
    assert updated_config.is_default is True
    
    # Test updating non-existent config
    non_existent = crud_pricing.update_pricing_config(db=db, config_id=9999, config_in=update_data)
    assert non_existent is None


def test_delete_pricing_config(db: Session) -> None:
    """Test deleting a pricing configuration."""
    # Create a config
    config_in = PricingConfigCreate(
        name="Standard Pricing",
        description="Standard pricing for repair services",
        base_diagnostic_fee=50.0,
        base_onsite_fee=25.0,
        hourly_rate_hardware=75.0,
        hourly_rate_software=65.0,
        hourly_rate_network=70.0
    )
    created_config = crud_pricing.create_pricing_config(db=db, config_in=config_in)
    
    # Delete the config
    success = crud_pricing.delete_pricing_config(db=db, config_id=created_config.id)
    assert success is True
    
    # Verify it's deleted
    deleted_config = crud_pricing.get_pricing_config(db=db, config_id=created_config.id)
    assert deleted_config is None
    
    # Test deleting non-existent config
    non_existent_success = crud_pricing.delete_pricing_config(db=db, config_id=9999)
    assert non_existent_success is False 