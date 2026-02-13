"""Add Marketplace Categories and Tags Tables

Revision ID: add_marketplace_categories_and_tags
Revises: add_marketplace_fields_to_agents
Create Date: 2026-01-10 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_marketplace_categories_and_tags'
down_revision = 'add_marketplace_fields_to_agents'
branch_labels = None
depends_on = None

def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    now_expr = sa.text("NOW()") if bind.dialect.name == "postgresql" else sa.text("CURRENT_TIMESTAMP")

    # Create marketplace_categories table
    op.create_table(
        'marketplace_categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('display_name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('icon', sa.String(length=100), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('sort_order', sa.Integer(), server_default='0', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=now_expr, nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=now_expr, nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name', name='uq_category_name')
    )
    
    # Create marketplace_tags table
    op.create_table(
        'marketplace_tags',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('display_name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('usage_count', sa.Integer(), server_default='0', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=now_expr, nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=now_expr, nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name', name='uq_tag_name')
    )
    
    # Create marketplace_listing_tags association table
    op.create_table(
        'marketplace_listing_tags',
        sa.Column('listing_id', sa.Integer(), nullable=False),
        sa.Column('tag_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=now_expr, nullable=False),
        sa.ForeignKeyConstraint(['listing_id'], ['marketplace_listings.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tag_id'], ['marketplace_tags.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('listing_id', 'tag_id')
    )
    
    # Add category_id column to marketplace_listings table
    if "marketplace_listings" in inspector.get_table_names():
        existing_columns = {column["name"] for column in inspector.get_columns("marketplace_listings")}
        if "category_id" not in existing_columns:
            op.add_column('marketplace_listings', sa.Column('category_id', sa.Integer(), nullable=True))
    
    # Add foreign key constraint for category_id
    if bind.dialect.name != "sqlite":
        op.create_foreign_key(
            'fk_marketplace_listings_category',
            'marketplace_listings',
            'marketplace_categories',
            ['category_id'],
            ['id'],
            ondelete='SET NULL'
        )
    
    # Create indexes for performance
    op.create_index('idx_categories_name', 'marketplace_categories', ['name'])
    op.create_index('idx_tags_name', 'marketplace_tags', ['name'])
    op.create_index('idx_listing_tags_listing', 'marketplace_listing_tags', ['listing_id'])
    op.create_index('idx_listing_tags_tag', 'marketplace_listing_tags', ['tag_id'])
    op.create_index('idx_listings_category', 'marketplace_listings', ['category_id'])


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    # Drop indexes
    op.drop_index('idx_listings_category')
    op.drop_index('idx_listing_tags_tag')
    op.drop_index('idx_listing_tags_listing')
    op.drop_index('idx_tags_name')
    op.drop_index('idx_categories_name')
    
    # Drop foreign key constraint
    if bind.dialect.name != "sqlite":
        op.drop_constraint('fk_marketplace_listings_category', 'marketplace_listings', type_='foreignkey')
    
    # Drop category_id column
    if "marketplace_listings" in inspector.get_table_names():
        existing_columns = {column["name"] for column in inspector.get_columns("marketplace_listings")}
        if "category_id" in existing_columns:
            op.drop_column('marketplace_listings', 'category_id')
    
    # Drop tables
    op.drop_table('marketplace_listing_tags')
    op.drop_table('marketplace_tags')
    op.drop_table('marketplace_categories')
