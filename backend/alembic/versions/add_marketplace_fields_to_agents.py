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
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "agents" not in inspector.get_table_names():
        return
    existing_columns = {column["name"] for column in inspector.get_columns("agents")}

    # Add marketplace-related fields to agents table
    if "is_marketplace_published" not in existing_columns:
        op.add_column('agents', sa.Column('is_marketplace_published', sa.Boolean(), server_default='false', nullable=False))
    if "marketplace_listing_id" not in existing_columns:
        op.add_column('agents', sa.Column('marketplace_listing_id', sa.Integer(), nullable=True))
    
    # Add foreign key constraint
    if bind.dialect.name != "sqlite" and "marketplace_listing_id" in {column["name"] for column in inspector.get_columns("agents")}:
        op.create_foreign_key(
            'fk_agents_marketplace_listing',
            'agents',
            'marketplace_listings',
            ['marketplace_listing_id'],
            ['id'],
            ondelete='SET NULL'
        )
    
    # Create index for marketplace queries
    indexes = {index["name"] for index in inspector.get_indexes("agents")}
    if "idx_agents_marketplace_published" not in indexes:
        op.create_index('idx_agents_marketplace_published', 'agents', ['is_marketplace_published'])


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "agents" not in inspector.get_table_names():
        return
    existing_columns = {column["name"] for column in inspector.get_columns("agents")}
    indexes = {index["name"] for index in inspector.get_indexes("agents")}

    # Drop index
    if "idx_agents_marketplace_published" in indexes:
        op.drop_index('idx_agents_marketplace_published')
    
    # Drop foreign key constraint
    try:
        op.drop_constraint('fk_agents_marketplace_listing', 'agents', type_='foreignkey')
    except Exception:
        pass
    
    # Drop columns
    if "marketplace_listing_id" in existing_columns:
        op.drop_column('agents', 'marketplace_listing_id')
    if "is_marketplace_published" in existing_columns:
        op.drop_column('agents', 'is_marketplace_published')
