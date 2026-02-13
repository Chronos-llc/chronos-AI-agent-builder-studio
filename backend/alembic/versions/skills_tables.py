"""Skills Tables Migration

Revision ID: skills_tables
Revises: marketplace_tables
Create Date: 2026-01-10 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'skills_tables'
down_revision = 'marketplace_tables'
branch_labels = None
depends_on = None

def upgrade():
    bind = op.get_bind()
    now_expr = sa.text("NOW()") if bind.dialect.name == "postgresql" else sa.text("CURRENT_TIMESTAMP")

    # Create agent_skills table
    op.create_table(
        'agent_skills',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False, unique=True),
        sa.Column('display_name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(length=50), nullable=True),
        sa.Column('icon', sa.String(length=50), nullable=True),
        
        # File Information
        sa.Column('file_path', sa.String(length=500), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('content_preview', sa.Text(), nullable=True),
        
        # Metadata
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('is_premium', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('install_count', sa.Integer(), server_default='0', nullable=False),
        
        # Admin Management
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=now_expr, nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=now_expr, nullable=False),
        
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create agent_skill_installations table
    op.create_table(
        'agent_skill_installations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('agent_id', sa.Integer(), nullable=False),
        sa.Column('skill_id', sa.Integer(), nullable=False),
        sa.Column('knowledge_file_id', sa.Integer(), nullable=True),
        sa.Column('installed_at', sa.DateTime(timezone=True), server_default=now_expr, nullable=False),
        
        sa.ForeignKeyConstraint(['agent_id'], ['agents.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['skill_id'], ['agent_skills.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['knowledge_file_id'], ['knowledge_files.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('agent_id', 'skill_id', name='uq_agent_skill')
    )
    
    # Create indexes for performance
    op.create_index('idx_skills_name', 'agent_skills', ['name'])
    op.create_index('idx_skills_category', 'agent_skills', ['category'])
    op.create_index('idx_skills_active', 'agent_skills', ['is_active'])
    op.create_index('idx_skill_installations_agent', 'agent_skill_installations', ['agent_id'])
    op.create_index('idx_skill_installations_skill', 'agent_skill_installations', ['skill_id'])


def downgrade():
    # Drop indexes
    op.drop_index('idx_skill_installations_skill')
    op.drop_index('idx_skill_installations_agent')
    op.drop_index('idx_skills_active')
    op.drop_index('idx_skills_category')
    op.drop_index('idx_skills_name')
    
    # Drop tables
    op.drop_table('agent_skill_installations')
    op.drop_table('agent_skills')
