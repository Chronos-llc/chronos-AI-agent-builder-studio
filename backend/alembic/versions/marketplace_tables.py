"""Marketplace Tables Migration

Revision ID: marketplace_tables
Revises: training_models
Create Date: 2026-01-10 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'marketplace_tables'
down_revision = 'training_models'
branch_labels = None
depends_on = None

def upgrade():
    # Create marketplace_listings table
    op.create_table(
        'marketplace_listings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('agent_id', sa.Integer(), nullable=False),
        sa.Column('listing_type', sa.String(length=20), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(length=50), nullable=True),
        sa.Column('tags', postgresql.JSONB(), nullable=True),
        
        # Visibility & Moderation
        sa.Column('visibility', sa.String(length=20), server_default='PUBLIC', nullable=False),
        sa.Column('moderation_status', sa.String(length=20), server_default='PENDING', nullable=False),
        sa.Column('moderation_notes', sa.Text(), nullable=True),
        
        # Metadata
        sa.Column('author_id', sa.Integer(), nullable=False),
        sa.Column('version', sa.String(length=20), nullable=True),
        sa.Column('schema_data', postgresql.JSONB(), nullable=True),
        sa.Column('preview_images', postgresql.JSONB(), nullable=True),
        sa.Column('demo_video_url', sa.String(length=500), nullable=True),
        
        # Statistics
        sa.Column('install_count', sa.Integer(), server_default='0', nullable=False),
        sa.Column('rating_average', sa.Numeric(precision=3, scale=2), server_default='0.0', nullable=False),
        sa.Column('rating_count', sa.Integer(), server_default='0', nullable=False),
        sa.Column('view_count', sa.Integer(), server_default='0', nullable=False),
        
        # Timestamps
        sa.Column('published_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        
        sa.ForeignKeyConstraint(['agent_id'], ['agents.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['author_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create marketplace_installations table
    op.create_table(
        'marketplace_installations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('listing_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('agent_id', sa.Integer(), nullable=False),
        sa.Column('installed_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        
        sa.ForeignKeyConstraint(['listing_id'], ['marketplace_listings.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['agent_id'], ['agents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('listing_id', 'user_id', name='uq_listing_user')
    )
    
    # Create marketplace_reviews table
    op.create_table(
        'marketplace_reviews',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('listing_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('review_text', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        
        sa.CheckConstraint('rating >= 1 AND rating <= 5', name='check_rating_range'),
        sa.ForeignKeyConstraint(['listing_id'], ['marketplace_listings.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('listing_id', 'user_id', name='uq_review_listing_user')
    )
    
    # Create indexes for performance
    op.create_index('idx_marketplace_visibility', 'marketplace_listings', ['visibility', 'moderation_status'])
    op.create_index('idx_marketplace_category', 'marketplace_listings', ['category'])
    op.create_index('idx_marketplace_author', 'marketplace_listings', ['author_id'])
    op.create_index('idx_marketplace_agent', 'marketplace_listings', ['agent_id'])
    op.create_index('idx_installations_listing', 'marketplace_installations', ['listing_id'])
    op.create_index('idx_installations_user', 'marketplace_installations', ['user_id'])
    op.create_index('idx_reviews_listing', 'marketplace_reviews', ['listing_id'])
    op.create_index('idx_reviews_user', 'marketplace_reviews', ['user_id'])


def downgrade():
    # Drop indexes
    op.drop_index('idx_reviews_user')
    op.drop_index('idx_reviews_listing')
    op.drop_index('idx_installations_user')
    op.drop_index('idx_installations_listing')
    op.drop_index('idx_marketplace_agent')
    op.drop_index('idx_marketplace_author')
    op.drop_index('idx_marketplace_category')
    op.drop_index('idx_marketplace_visibility')
    
    # Drop tables
    op.drop_table('marketplace_reviews')
    op.drop_table('marketplace_installations')
    op.drop_table('marketplace_listings')
