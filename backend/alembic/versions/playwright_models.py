"""
Playwright Models Migration

Revision ID: playwright_models_001
Revises: 
Create Date: 2025-12-31 02:11:55.777000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'playwright_models_001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Create Playwright-specific database models"""
    
    # Create playwright_browser_sessions table
    op.create_table('playwright_browser_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.String(length=255), nullable=False),
        sa.Column('user_id', sa.String(length=255), nullable=False),
        sa.Column('browser_type', sa.String(length=50), nullable=False),
        sa.Column('viewport_width', sa.Integer(), nullable=True),
        sa.Column('viewport_height', sa.Integer(), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('headless', sa.Boolean(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('current_url', sa.String(length=2000), nullable=True),
        sa.Column('cookies', sa.JSON(), nullable=True),
        sa.Column('local_storage', sa.JSON(), nullable=True),
        sa.Column('session_storage', sa.JSON(), nullable=True),
        sa.Column('memory_usage_mb', sa.Float(), nullable=True),
        sa.Column('cpu_usage_percent', sa.Float(), nullable=True),
        sa.Column('network_requests', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('last_activity', sa.DateTime(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_playwright_browser_sessions_id'), 'playwright_browser_sessions', ['id'], unique=False)
    op.create_index(op.f('ix_playwright_browser_sessions_session_id'), 'playwright_browser_sessions', ['session_id'], unique=True)
    op.create_index(op.f('ix_playwright_browser_sessions_user_id'), 'playwright_browser_sessions', ['user_id'], unique=False)

    # Create playwright_automation_tasks table
    op.create_table('playwright_automation_tasks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('task_id', sa.String(length=255), nullable=False),
        sa.Column('session_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(length=255), nullable=False),
        sa.Column('target_url', sa.String(length=2000), nullable=False),
        sa.Column('actions', sa.JSON(), nullable=False),
        sa.Column('selectors', sa.JSON(), nullable=True),
        sa.Column('viewport_config', sa.JSON(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('duration_ms', sa.Float(), nullable=True),
        sa.Column('success', sa.Boolean(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('final_url', sa.String(length=2000), nullable=True),
        sa.Column('captured_data', sa.JSON(), nullable=True),
        sa.Column('screenshot_taken', sa.Boolean(), nullable=True),
        sa.Column('pdf_generated', sa.Boolean(), nullable=True),
        sa.Column('video_recorded', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['session_id'], ['playwright_browser_sessions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_playwright_automation_tasks_id'), 'playwright_automation_tasks', ['id'], unique=False)
    op.create_index(op.f('ix_playwright_automation_tasks_task_id'), 'playwright_automation_tasks', ['task_id'], unique=True)
    op.create_index(op.f('ix_playwright_automation_tasks_session_id'), 'playwright_automation_tasks', ['session_id'], unique=False)
    op.create_index(op.f('ix_playwright_automation_tasks_user_id'), 'playwright_automation_tasks', ['user_id'], unique=False)

    # Create playwright_artifacts table
    op.create_table('playwright_artifacts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('artifact_id', sa.String(length=255), nullable=False),
        sa.Column('task_id', sa.Integer(), nullable=True),
        sa.Column('session_id', sa.Integer(), nullable=False),
        sa.Column('artifact_type', sa.String(length=50), nullable=False),
        sa.Column('file_name', sa.String(length=255), nullable=False),
        sa.Column('file_path', sa.String(length=1000), nullable=False),
        sa.Column('file_size_bytes', sa.Integer(), nullable=True),
        sa.Column('mime_type', sa.String(length=100), nullable=False),
        sa.Column('storage_type', sa.String(length=50), nullable=True),
        sa.Column('encryption_key', sa.String(length=255), nullable=True),
        sa.Column('checksum', sa.String(length=64), nullable=True),
        sa.Column('width', sa.Integer(), nullable=True),
        sa.Column('height', sa.Integer(), nullable=True),
        sa.Column('duration_ms', sa.Integer(), nullable=True),
        sa.Column('page_url', sa.String(length=2000), nullable=True),
        sa.Column('capture_timestamp', sa.DateTime(), nullable=True),
        sa.Column('is_public', sa.Boolean(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('download_count', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['session_id'], ['playwright_browser_sessions.id'], ),
        sa.ForeignKeyConstraint(['task_id'], ['playwright_automation_tasks.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_playwright_artifacts_id'), 'playwright_artifacts', ['id'], unique=False)
    op.create_index(op.f('ix_playwright_artifacts_artifact_id'), 'playwright_artifacts', ['artifact_id'], unique=True)
    op.create_index(op.f('ix_playwright_artifacts_session_id'), 'playwright_artifacts', ['session_id'], unique=False)
    op.create_index(op.f('ix_playwright_artifacts_task_id'), 'playwright_artifacts', ['task_id'], unique=False)

    # Create playwright_browser_pools table
    op.create_table('playwright_browser_pools',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('pool_id', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('browser_type', sa.String(length=50), nullable=False),
        sa.Column('max_instances', sa.Integer(), nullable=True),
        sa.Column('min_instances', sa.Integer(), nullable=True),
        sa.Column('instance_timeout_minutes', sa.Integer(), nullable=True),
        sa.Column('max_memory_mb', sa.Integer(), nullable=True),
        sa.Column('max_cpu_percent', sa.Integer(), nullable=True),
        sa.Column('max_concurrent_tasks', sa.Integer(), nullable=True),
        sa.Column('idle_timeout_minutes', sa.Integer(), nullable=True),
        sa.Column('health_check_interval_seconds', sa.Integer(), nullable=True),
        sa.Column('auto_scaling_enabled', sa.Boolean(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('current_instances', sa.Integer(), nullable=True),
        sa.Column('total_tasks_executed', sa.Integer(), nullable=True),
        sa.Column('total_tasks_failed', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_playwright_browser_pools_id'), 'playwright_browser_pools', ['id'], unique=False)
    op.create_index(op.f('ix_playwright_browser_pools_pool_id'), 'playwright_browser_pools', ['pool_id'], unique=True)

    # Create playwright_browser_pool_instances table
    op.create_table('playwright_browser_pool_instances',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('instance_id', sa.String(length=255), nullable=False),
        sa.Column('pool_id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.String(length=255), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('pid', sa.Integer(), nullable=True),
        sa.Column('port', sa.Integer(), nullable=True),
        sa.Column('memory_usage_mb', sa.Float(), nullable=True),
        sa.Column('cpu_usage_percent', sa.Float(), nullable=True),
        sa.Column('last_activity', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('last_used', sa.DateTime(), nullable=True),
        sa.Column('termination_reason', sa.String(length=255), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['pool_id'], ['playwright_browser_pools.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_playwright_browser_pool_instances_id'), 'playwright_browser_pool_instances', ['id'], unique=False)
    op.create_index(op.f('ix_playwright_browser_pool_instances_instance_id'), 'playwright_browser_pool_instances', ['instance_id'], unique=True)
    op.create_index(op.f('ix_playwright_browser_pool_instances_pool_id'), 'playwright_browser_pool_instances', ['pool_id'], unique=False)

    # Create playwright_security_rules table
    op.create_table('playwright_security_rules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('rule_id', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('rule_type', sa.String(length=50), nullable=False),
        sa.Column('pattern', sa.String(length=1000), nullable=False),
        sa.Column('is_regex', sa.Boolean(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('priority', sa.Integer(), nullable=True),
        sa.Column('action', sa.String(length=50), nullable=True),
        sa.Column('created_by', sa.String(length=255), nullable=True),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_playwright_security_rules_id'), 'playwright_security_rules', ['id'], unique=False)
    op.create_index(op.f('ix_playwright_security_rules_rule_id'), 'playwright_security_rules', ['rule_id'], unique=True)

    # Update existing mcp_operation_logs table to include Playwright operation types
    op.execute("""
        ALTER TYPE operationtype ADD VALUE IF NOT EXISTS 'playwright_automation';
        ALTER TYPE operationtype ADD VALUE IF NOT EXISTS 'playwright_session_management';
        ALTER TYPE operationtype ADD VALUE IF NOT EXISTS 'playwright_pool_management';
    """)

    # Add Playwright-specific indexes for performance
    op.create_index('ix_playwright_artifacts_created_at', 'playwright_artifacts', ['created_at'], unique=False)
    op.create_index('ix_playwright_automation_tasks_status', 'playwright_automation_tasks', ['status'], unique=False)
    op.create_index('ix_playwright_automation_tasks_created_at', 'playwright_automation_tasks', ['created_at'], unique=False)
    op.create_index('ix_playwright_browser_sessions_status', 'playwright_browser_sessions', ['status'], unique=False)
    op.create_index('ix_playwright_browser_sessions_created_at', 'playwright_browser_sessions', ['created_at'], unique=False)


def downgrade():
    """Drop Playwright-specific database models"""
    
    # Drop indexes first
    op.drop_index('ix_playwright_browser_sessions_created_at', table_name='playwright_browser_sessions')
    op.drop_index('ix_playwright_browser_sessions_status', table_name='playwright_browser_sessions')
    op.drop_index('ix_playwright_automation_tasks_created_at', table_name='playwright_automation_tasks')
    op.drop_index('ix_playwright_automation_tasks_status', table_name='playwright_automation_tasks')
    op.drop_index('ix_playwright_artifacts_created_at', table_name='playwright_artifacts')

    # Drop tables
    op.drop_table('playwright_security_rules')
    op.drop_table('playwright_browser_pool_instances')
    op.drop_table('playwright_browser_pools')
    op.drop_table('playwright_artifacts')
    op.drop_table('playwright_automation_tasks')
    op.drop_table('playwright_browser_sessions')
