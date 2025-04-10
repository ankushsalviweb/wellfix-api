"""Add RepairJob models

Revision ID: 2a3b4c5d6e7f
Revises: 1a2b3c4d5e6f
Create Date: 2023-04-05 20:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from alembic import context

# revision identifiers, used by Alembic.
revision = '2a3b4c5d6e7f'
down_revision = '1a2b3c4d5e6f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Get the dialect of the database
    dialect = context.get_context().dialect.name
    
    # Create enum types for PostgreSQL
    if dialect == 'postgresql':
        # Create job_status enum
        op.execute("""
        CREATE TYPE job_status AS ENUM (
            'PENDING_APPROVAL', 'PENDING_ASSIGNMENT', 'ASSIGNED_TO_ENGINEER', 
            'EN_ROUTE', 'ON_SITE_DIAGNOSIS', 'PARTS_ORDERED', 
            'REPAIR_IN_PROGRESS_ON_SITE', 'ESCALATED_TO_LAB', 'PENDING_PICKUP_FOR_LAB', 
            'IN_TRANSIT_TO_LAB', 'LAB_DIAGNOSIS', 'PENDING_QUOTE_APPROVAL', 
            'REPAIR_IN_PROGRESS_LAB', 'PENDING_RETURN_DELIVERY', 'IN_TRANSIT_FROM_LAB', 
            'PENDING_PAYMENT', 'COMPLETED', 'CANCELLED'
        )
        """)
        
        # Create repair_type enum
        op.execute("""
        CREATE TYPE repair_type AS ENUM (
            'ON_SITE_PART', 'LAB_DIAGNOSIS', 'LAB_MOTHERBOARD'
        )
        """)
        
        # Create payment_status enum
        op.execute("""
        CREATE TYPE payment_status AS ENUM (
            'PENDING', 'PAID', 'WAIVED'
        )
        """)
        
        job_status_type = sa.Enum(
            'PENDING_APPROVAL', 'PENDING_ASSIGNMENT', 'ASSIGNED_TO_ENGINEER', 
            'EN_ROUTE', 'ON_SITE_DIAGNOSIS', 'PARTS_ORDERED', 
            'REPAIR_IN_PROGRESS_ON_SITE', 'ESCALATED_TO_LAB', 'PENDING_PICKUP_FOR_LAB', 
            'IN_TRANSIT_TO_LAB', 'LAB_DIAGNOSIS', 'PENDING_QUOTE_APPROVAL', 
            'REPAIR_IN_PROGRESS_LAB', 'PENDING_RETURN_DELIVERY', 'IN_TRANSIT_FROM_LAB', 
            'PENDING_PAYMENT', 'COMPLETED', 'CANCELLED',
            name='job_status'
        )
        
        repair_type_type = sa.Enum(
            'ON_SITE_PART', 'LAB_DIAGNOSIS', 'LAB_MOTHERBOARD',
            name='repair_type'
        )
        
        payment_status_type = sa.Enum(
            'PENDING', 'PAID', 'WAIVED',
            name='payment_status'
        )
    else:
        # For SQLite and other databases, use strings
        job_status_type = sa.String(30)
        repair_type_type = sa.String(20)
        payment_status_type = sa.String(10)
    
    # Create serviceable_areas table
    op.create_table(
        'serviceable_areas',
        sa.Column('pincode', sa.String(10), primary_key=True, index=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('1')),
        sa.Column('added_by_admin_id', sa.String(36), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['added_by_admin_id'], ['users.id'], ondelete='SET NULL'),
    )
    
    # Create repair_jobs table
    op.create_table(
        'repair_jobs',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('customer_id', sa.String(36), nullable=False),
        sa.Column('engineer_id', sa.String(36), nullable=True),
        sa.Column('address_id', sa.String(36), nullable=False),
        sa.Column('laptop_manufacturer', sa.String(100), nullable=False),
        sa.Column('laptop_model', sa.String(100), nullable=False),
        sa.Column('laptop_serial_number', sa.String(100), nullable=True),
        sa.Column('reported_symptoms', sa.Text(), nullable=False),
        sa.Column('repair_type_requested', repair_type_type, nullable=False, server_default='ON_SITE_PART'),
        sa.Column('status', job_status_type, nullable=False, server_default='PENDING_ASSIGNMENT'),
        sa.Column('scheduled_datetime', sa.DateTime(), nullable=True),
        sa.Column('estimated_cost', sa.Float(), nullable=True),
        sa.Column('final_cost', sa.Float(), nullable=True),
        sa.Column('payment_status', payment_status_type, nullable=False, server_default='PENDING'),
        sa.Column('engineer_notes', sa.Text(), nullable=True),
        sa.Column('admin_notes', sa.Text(), nullable=True),
        sa.Column('customer_consent_for_lab', sa.Boolean(), nullable=False, server_default=sa.text('0')),
        sa.Column('cancellation_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['customer_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['engineer_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['address_id'], ['addresses.id'], ondelete='RESTRICT'),
    )
    
    # Create job_status_updates table
    op.create_table(
        'job_status_updates',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('job_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(36), nullable=True),
        sa.Column('previous_status', job_status_type, nullable=False),
        sa.Column('new_status', job_status_type, nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['job_id'], ['repair_jobs.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
    )
    
    # Create ratings table
    op.create_table(
        'ratings',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('job_id', sa.Integer(), nullable=False),
        sa.Column('customer_id', sa.String(36), nullable=False),
        sa.Column('engineer_id', sa.String(36), nullable=True),
        sa.Column('score', sa.Integer(), nullable=False),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['job_id'], ['repair_jobs.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['customer_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['engineer_id'], ['users.id'], ondelete='SET NULL'),
        sa.UniqueConstraint('job_id'),
    )


def downgrade() -> None:
    # Drop tables
    op.drop_table('ratings')
    op.drop_table('job_status_updates')
    op.drop_table('repair_jobs')
    op.drop_table('serviceable_areas')
    
    # Get the dialect of the database
    dialect = context.get_context().dialect.name
    
    # Drop enum types if PostgreSQL
    if dialect == 'postgresql':
        op.execute("DROP TYPE payment_status")
        op.execute("DROP TYPE repair_type")
        op.execute("DROP TYPE job_status")