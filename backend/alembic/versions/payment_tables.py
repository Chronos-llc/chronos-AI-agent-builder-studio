"""Payment Tables Migration

Revision ID: payment_tables
Revises: support_system_tables
Create Date: 2026-01-10 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'payment_tables'
down_revision = 'support_system_tables'
branch_labels = None
depends_on = None

def upgrade():
    bind = op.get_bind()
    is_postgres = bind.dialect.name == "postgresql"
    json_type = postgresql.JSONB() if is_postgres else sa.JSON()
    now_expr = sa.text("NOW()") if is_postgres else sa.text("CURRENT_TIMESTAMP")

    # Create payment_methods table
    op.create_table(
        'payment_methods',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('provider', sa.String(length=50), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('configuration', json_type, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=now_expr, nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=now_expr, nullable=False),
        
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create payment_settings table
    op.create_table(
        'payment_settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('currency', sa.String(length=3), server_default='USD', nullable=False),
        sa.Column('tax_rate', sa.Numeric(precision=5, scale=2), server_default='0.0', nullable=False),
        sa.Column('default_payment_method_id', sa.Integer(), nullable=True),
        sa.Column('settings', json_type, nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=now_expr, nullable=False),
        
        sa.ForeignKeyConstraint(['default_payment_method_id'], ['payment_methods.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for performance
    op.create_index('idx_payment_methods_provider', 'payment_methods', ['provider'])
    op.create_index('idx_payment_methods_active', 'payment_methods', ['is_active'])


def downgrade():
    # Drop indexes
    op.drop_index('idx_payment_methods_active')
    op.drop_index('idx_payment_methods_provider')
    
    # Drop tables
    op.drop_table('payment_settings')
    op.drop_table('payment_methods')
