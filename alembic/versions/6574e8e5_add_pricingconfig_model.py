"""Add PricingConfig model

Revision ID: 6574e8e5
Revises: 2a3b4c5d6e7f
Create Date: 2025-04-06 16:02:29.806407

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '6574e8e5'
down_revision: Union[str, None] = '2a3b4c5d6e7f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop existing pricing_configs table if it exists
    op.drop_table('pricing_configs')
    
    # Create pricing_configs table with the correct schema
    op.create_table(
        'pricing_configs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        # Base Rates
        sa.Column('base_diagnostic_fee', sa.Float(), nullable=False),
        sa.Column('base_onsite_fee', sa.Float(), nullable=False),
        # Hourly Rates
        sa.Column('hourly_rate_hardware', sa.Float(), nullable=False),
        sa.Column('hourly_rate_software', sa.Float(), nullable=False),
        sa.Column('hourly_rate_network', sa.Float(), nullable=False),
        # Surcharges
        sa.Column('emergency_surcharge_percentage', sa.Float(), nullable=False, server_default='25.0'),
        sa.Column('weekend_surcharge_percentage', sa.Float(), nullable=False, server_default='15.0'),
        sa.Column('evening_surcharge_percentage', sa.Float(), nullable=False, server_default='10.0'),
        # Service Area Surcharge
        sa.Column('distance_surcharge_per_mile', sa.Float(), nullable=False, server_default='0.5'),
        sa.Column('base_service_radius_miles', sa.Float(), nullable=False, server_default='10.0'),
        # Status
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('is_default', sa.Boolean(), nullable=False, server_default='0'),
        # Timestamps
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index(op.f('ix_pricing_configs_id'), 'pricing_configs', ['id'], unique=False)
    op.create_index(op.f('ix_pricing_configs_is_active'), 'pricing_configs', ['is_active'], unique=False)


def downgrade() -> None:
    # Drop the pricing_configs table
    op.drop_index(op.f('ix_pricing_configs_is_active'), table_name='pricing_configs')
    op.drop_index(op.f('ix_pricing_configs_id'), table_name='pricing_configs')
    op.drop_table('pricing_configs')
