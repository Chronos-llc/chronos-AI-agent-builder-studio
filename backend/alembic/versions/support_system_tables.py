"""Support System Tables Migration

Revision ID: support_system_tables
Revises: platform_updates_tables
Create Date: 2026-01-10 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'support_system_tables'
down_revision = 'platform_updates_tables'
branch_labels = None
depends_on = None

def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "support_messages" in inspector.get_table_names():
        return

    now_expr = sa.text("NOW()") if bind.dialect.name == "postgresql" else sa.text("CURRENT_TIMESTAMP")

    # Create support_messages table
    op.create_table(
        'support_messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('subject', sa.String(length=200), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('status', sa.String(length=20), server_default='OPEN', nullable=False),
        sa.Column('priority', sa.String(length=20), server_default='NORMAL', nullable=False),
        sa.Column('assigned_to', sa.Integer(), nullable=True),
        sa.Column('category', sa.String(length=50), nullable=True),
        
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=now_expr, nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=now_expr, nullable=False),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['assigned_to'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create support_message_replies table
    op.create_table(
        'support_message_replies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('message_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('is_admin', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('reply_text', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=now_expr, nullable=False),
        
        sa.ForeignKeyConstraint(['message_id'], ['support_messages.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for performance
    op.create_index('idx_support_messages_user', 'support_messages', ['user_id'])
    op.create_index('idx_support_messages_status', 'support_messages', ['status'])
    op.create_index('idx_support_messages_assigned', 'support_messages', ['assigned_to'])
    op.create_index('idx_support_messages_category', 'support_messages', ['category'])
    op.create_index('idx_support_replies_message', 'support_message_replies', ['message_id'])
    op.create_index('idx_support_replies_user', 'support_message_replies', ['user_id'])


def downgrade():
    # Drop indexes
    op.drop_index('idx_support_replies_user')
    op.drop_index('idx_support_replies_message')
    op.drop_index('idx_support_messages_category')
    op.drop_index('idx_support_messages_assigned')
    op.drop_index('idx_support_messages_status')
    op.drop_index('idx_support_messages_user')
    
    # Drop tables
    op.drop_table('support_message_replies')
    op.drop_table('support_messages')
