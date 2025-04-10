"""Initial User and Address models

Revision ID: 1a2b3c4d5e6f
Revises: 
Create Date: 2023-04-05 19:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from alembic import context

# revision identifiers, used by Alembic.
revision = '1a2b3c4d5e6f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Get the dialect of the database
    dialect = context.get_context().dialect.name
    
    # Create users table
    if dialect == 'postgresql':
        # PostgreSQL-specific: Create enum type
        op.execute("CREATE TYPE user_role AS ENUM ('CUSTOMER', 'ENGINEER', 'ADMIN')")
        user_role_type = sa.Enum('CUSTOMER', 'ENGINEER', 'ADMIN', name='user_role')
    else:
        # For SQLite and other databases, use string
        user_role_type = sa.String(10)
    
    # Create tables
    op.create_table(
        'users',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('password_hash', sa.String(), nullable=False),
        sa.Column('first_name', sa.String(), nullable=False),
        sa.Column('last_name', sa.String(), nullable=False),
        sa.Column('phone_number', sa.String(), nullable=False),
        sa.Column('role', user_role_type, nullable=False, server_default='CUSTOMER'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('1')),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.UniqueConstraint('email'),
    )
    op.create_index('ix_users_email', 'users', ['email'])
    
    # Create addresses table
    op.create_table(
        'addresses',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('street_address', sa.String(), nullable=False),
        sa.Column('city', sa.String(), nullable=False),
        sa.Column('state', sa.String(), nullable=False),
        sa.Column('pincode', sa.String(), nullable=False),
        sa.Column('is_default', sa.Boolean(), nullable=False, server_default=sa.text('0')),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_addresses_pincode', 'addresses', ['pincode'])


def downgrade() -> None:
    # Drop tables
    op.drop_table('addresses')
    op.drop_table('users')
    
    # Get the dialect of the database
    dialect = context.get_context().dialect.name
    
    # Drop enum type if PostgreSQL
    if dialect == 'postgresql':
        op.execute("DROP TYPE user_role") 