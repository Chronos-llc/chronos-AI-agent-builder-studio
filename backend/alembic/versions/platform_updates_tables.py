"""Platform Updates Tables Migration

Revision ID: platform_updates_tables
Revises: skills_tables
Create Date: 2026-01-10 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'platform_updates_tables'
down_revision = 'skills_tables'
branch_labels = None
depends_on = None

def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "platform_updates" in inspector.get_table_names():
        return

    is_postgres = bind.dialect.name == "postgresql"
    json_type = postgresql.JSONB() if is_postgres else sa.JSON()
    now_expr = sa.text("NOW()") if is_postgres else sa.text("CURRENT_TIMESTAMP")

    # Create platform_updates table
    op.create_table(
        'platform_updates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('update_type', sa.String(length=20), nullable=False),
        sa.Column('priority', sa.String(length=20), server_default='NORMAL', nullable=False),
        
        # Media
        sa.Column('media_type', sa.String(length=20), nullable=True),
        sa.Column('media_urls', json_type, nullable=True),
        sa.Column('thumbnail_url', sa.String(length=500), nullable=True),
        
        # Visibility
        sa.Column('is_published', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('target_audience', sa.String(length=20), server_default='ALL', nullable=False),
        
        # Tracking
        sa.Column('view_count', sa.Integer(), server_default='0', nullable=False),
        
        # Timestamps
        sa.Column('published_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=now_expr, nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=now_expr, nullable=False),
        
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create user_update_views table
    op.create_table(
        'user_update_views',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('update_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('viewed_at', sa.DateTime(timezone=True), server_default=now_expr, nullable=False),
        
        sa.ForeignKeyConstraint(['update_id'], ['platform_updates.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('update_id', 'user_id', name='uq_update_user_view')
    )
    
    # Create indexes for performance
    op.create_index('idx_updates_published', 'platform_updates', ['is_published'])
    op.create_index('idx_updates_type', 'platform_updates', ['update_type'])
    op.create_index('idx_updates_published_at', 'platform_updates', ['published_at'])
    op.create_index('idx_update_views_update', 'user_update_views', ['update_id'])
    op.create_index('idx_update_views_user', 'user_update_views', ['user_id'])


def downgrade():
    # Drop indexes
    op.drop_index('idx_update_views_user')
    op.drop_index('idx_update_views_update')
    op.drop_index('idx_updates_published_at')
    op.drop_index('idx_updates_type')
    op.drop_index('idx_updates_published')
    
    # Drop tables
    op.drop_table('user_update_views')
    op.drop_table('platform_updates')
