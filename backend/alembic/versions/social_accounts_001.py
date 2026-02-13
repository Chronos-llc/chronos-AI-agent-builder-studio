"""add social accounts table

Revision ID: social_accounts_001
Revises: admin_roles_001
Create Date: 2026-02-12
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'social_accounts_001'
down_revision = 'admin_roles_001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'social_accounts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('provider', sa.String(length=20), nullable=False),
        sa.Column('provider_user_id', sa.String(length=255), nullable=False),
        sa.Column('provider_email', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('provider', 'provider_user_id', name='uq_social_provider_user'),
    )
    op.create_index(op.f('ix_social_accounts_id'), 'social_accounts', ['id'], unique=False)
    op.create_index(op.f('ix_social_accounts_user_id'), 'social_accounts', ['user_id'], unique=False)
    op.create_index(op.f('ix_social_accounts_provider'), 'social_accounts', ['provider'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_social_accounts_provider'), table_name='social_accounts')
    op.drop_index(op.f('ix_social_accounts_user_id'), table_name='social_accounts')
    op.drop_index(op.f('ix_social_accounts_id'), table_name='social_accounts')
    op.drop_table('social_accounts')
