"""Add Marketplace Fields to Agents Table

Revision ID: add_marketplace_fields_to_agents
Revises: payment_tables
Create Date: 2026-01-10 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_marketplace_fields_to_agents'
down_revision = 'payment_tables'
branch_labels = None
depends_on = None

def upgrade():
    # Add marketplace-related fields to agents table
    op.add_column('agents', sa.Column('is_marketplace_published', sa.Boolean(), server_default='false', nullable=False))
    op.add_column('agents', sa.Column('marketplace_listing_id', sa.Integer(), nullable=True))
    
    # Add foreign key constraint
    op.create_foreign_key(
        'fk_agents_marketplace_listing',
        'agents',
        'marketplace_listings',
        ['marketplace_listing_id'],
        ['id'],
        ondelete='SET NULL'
    )
    
    # Create index for marketplace queries
    op.create_index('idx_agents_marketplace_published', 'agents', ['is_marketplace_published'])


def downgrade():
    # Drop index
    op.drop_index('idx_agents_marketplace_published')
    
    # Drop foreign key constraint
    op.drop_constraint('fk_agents_marketplace_listing', 'agents', type_='foreignkey')
    
    # Drop columns
    op.drop_column('agents', 'marketplace_listing_id')
    op.drop_column('agents', 'is_marketplace_published')
