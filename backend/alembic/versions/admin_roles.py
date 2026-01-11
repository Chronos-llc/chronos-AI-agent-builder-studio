"""admin roles and permissions

Revision ID: admin_roles_001
Revises: add_marketplace_categories_and_tags
Create Date: 2026-01-10 21:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'admin_roles_001'
down_revision = 'add_marketplace_categories_and_tags'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create admin_roles table
    op.create_table(
        'admin_roles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.Enum('SUPER_ADMIN', 'ADMIN', 'MODERATOR', 'SUPPORT', name='adminroleenum'), nullable=False),
        sa.Column('display_name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_admin_roles_id'), 'admin_roles', ['id'], unique=False)
    op.create_index(op.f('ix_admin_roles_name'), 'admin_roles', ['name'], unique=True)
    
    # Create admin_permissions table
    op.create_table(
        'admin_permissions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.Enum(
            'MANAGE_USERS', 'VIEW_USERS', 'BAN_USERS',
            'MANAGE_AGENTS', 'VIEW_AGENTS', 'DELETE_AGENTS',
            'MANAGE_MARKETPLACE', 'APPROVE_LISTINGS', 'REJECT_LISTINGS', 'FEATURE_LISTINGS',
            'MANAGE_SUPPORT', 'VIEW_SUPPORT_TICKETS', 'RESPOND_TO_TICKETS',
            'MANAGE_SYSTEM', 'VIEW_ANALYTICS', 'MANAGE_SETTINGS',
            'VIEW_AUDIT_LOGS',
            name='permissionenum'
        ), nullable=False),
        sa.Column('display_name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('resource', sa.String(length=50), nullable=False),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_admin_permissions_id'), 'admin_permissions', ['id'], unique=False)
    op.create_index(op.f('ix_admin_permissions_name'), 'admin_permissions', ['name'], unique=True)
    
    # Create admin_role_permissions association table
    op.create_table(
        'admin_role_permissions',
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.Column('permission_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['permission_id'], ['admin_permissions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['role_id'], ['admin_roles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('role_id', 'permission_id')
    )
    
    # Create admin_users table
    op.create_table(
        'admin_users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role_id', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['role_id'], ['admin_roles.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index(op.f('ix_admin_users_id'), 'admin_users', ['id'], unique=False)
    op.create_index(op.f('ix_admin_users_user_id'), 'admin_users', ['user_id'], unique=True)
    
    # Create admin_audit_logs table
    op.create_table(
        'admin_audit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('admin_user_id', sa.Integer(), nullable=True),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('resource_type', sa.String(length=50), nullable=False),
        sa.Column('resource_id', sa.Integer(), nullable=True),
        sa.Column('details', sa.Text(), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=255), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True, server_default='success'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['admin_user_id'], ['admin_users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_admin_audit_logs_id'), 'admin_audit_logs', ['id'], unique=False)
    op.create_index(op.f('ix_admin_audit_logs_action'), 'admin_audit_logs', ['action'], unique=False)
    op.create_index(op.f('ix_admin_audit_logs_resource_type'), 'admin_audit_logs', ['resource_type'], unique=False)
    
    # Insert default roles
    op.execute("""
        INSERT INTO admin_roles (name, display_name, description, is_active)
        VALUES 
            ('SUPER_ADMIN', 'Super Administrator', 'Full system access with all permissions', true),
            ('ADMIN', 'Administrator', 'Manage users, agents, and marketplace', true),
            ('MODERATOR', 'Moderator', 'Review and approve marketplace listings', true),
            ('SUPPORT', 'Support Agent', 'Access support tickets and user data', true)
    """)
    
    # Insert default permissions
    op.execute("""
        INSERT INTO admin_permissions (name, display_name, description, resource, action)
        VALUES 
            -- User management
            ('MANAGE_USERS', 'Manage Users', 'Full user management capabilities', 'users', 'manage'),
            ('VIEW_USERS', 'View Users', 'View user information', 'users', 'view'),
            ('BAN_USERS', 'Ban Users', 'Ban or suspend users', 'users', 'ban'),
            
            -- Agent management
            ('MANAGE_AGENTS', 'Manage Agents', 'Full agent management capabilities', 'agents', 'manage'),
            ('VIEW_AGENTS', 'View Agents', 'View agent information', 'agents', 'view'),
            ('DELETE_AGENTS', 'Delete Agents', 'Delete agents', 'agents', 'delete'),
            
            -- Marketplace management
            ('MANAGE_MARKETPLACE', 'Manage Marketplace', 'Full marketplace management', 'marketplace', 'manage'),
            ('APPROVE_LISTINGS', 'Approve Listings', 'Approve marketplace listings', 'marketplace', 'approve'),
            ('REJECT_LISTINGS', 'Reject Listings', 'Reject marketplace listings', 'marketplace', 'reject'),
            ('FEATURE_LISTINGS', 'Feature Listings', 'Feature marketplace listings', 'marketplace', 'feature'),
            
            -- Support management
            ('MANAGE_SUPPORT', 'Manage Support', 'Full support system management', 'support', 'manage'),
            ('VIEW_SUPPORT_TICKETS', 'View Support Tickets', 'View support tickets', 'support', 'view'),
            ('RESPOND_TO_TICKETS', 'Respond to Tickets', 'Respond to support tickets', 'support', 'respond'),
            
            -- System management
            ('MANAGE_SYSTEM', 'Manage System', 'Full system management', 'system', 'manage'),
            ('VIEW_ANALYTICS', 'View Analytics', 'View system analytics', 'system', 'view'),
            ('MANAGE_SETTINGS', 'Manage Settings', 'Manage system settings', 'system', 'manage'),
            
            -- Audit logs
            ('VIEW_AUDIT_LOGS', 'View Audit Logs', 'View admin audit logs', 'audit', 'view')
    """)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index(op.f('ix_admin_audit_logs_resource_type'), table_name='admin_audit_logs')
    op.drop_index(op.f('ix_admin_audit_logs_action'), table_name='admin_audit_logs')
    op.drop_index(op.f('ix_admin_audit_logs_id'), table_name='admin_audit_logs')
    op.drop_table('admin_audit_logs')
    
    op.drop_index(op.f('ix_admin_users_user_id'), table_name='admin_users')
    op.drop_index(op.f('ix_admin_users_id'), table_name='admin_users')
    op.drop_table('admin_users')
    
    op.drop_table('admin_role_permissions')
    
    op.drop_index(op.f('ix_admin_permissions_name'), table_name='admin_permissions')
    op.drop_index(op.f('ix_admin_permissions_id'), table_name='admin_permissions')
    op.drop_table('admin_permissions')
    
    op.drop_index(op.f('ix_admin_roles_name'), table_name='admin_roles')
    op.drop_index(op.f('ix_admin_roles_id'), table_name='admin_roles')
    op.drop_table('admin_roles')
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS permissionenum')
    op.execute('DROP TYPE IF EXISTS adminroleenum')
