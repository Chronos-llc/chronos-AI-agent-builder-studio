"""Training Models Migration

Revision ID: training_models
Revises: None
Create Date: 2026-01-04 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'training_models'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    bind = op.get_bind()
    is_postgres = bind.dialect.name == "postgresql"
    uuid_type = postgresql.UUID(as_uuid=True) if is_postgres else sa.String(length=36)
    json_type = postgresql.JSON() if is_postgres else sa.JSON()

    # Create training_sessions table
    op.create_table(
        'training_sessions',
        sa.Column('id', uuid_type, nullable=False),
        sa.Column('agent_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('session_name', sa.String(length=255), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('ended_at', sa.DateTime(), nullable=True),
        sa.Column('status', sa.Enum('active', 'completed', 'aborted', name='trainingsessionstatus'), nullable=False),
        sa.Column('configuration', json_type, nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['agent_id'], ['agents.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create training_interactions table
    op.create_table(
        'training_interactions',
        sa.Column('id', uuid_type, nullable=False),
        sa.Column('session_id', uuid_type, nullable=False),
        sa.Column('interaction_order', sa.Integer(), nullable=False),
        sa.Column('user_input', sa.Text(), nullable=False),
        sa.Column('agent_response', sa.Text(), nullable=True),
        sa.Column('response_time_ms', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('metadata', json_type, nullable=True),
        sa.ForeignKeyConstraint(['session_id'], ['training_sessions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create training_corrections table
    op.create_table(
        'training_corrections',
        sa.Column('id', uuid_type, nullable=False),
        sa.Column('interaction_id', uuid_type, nullable=False),
        sa.Column('correction_type', sa.Enum('response', 'behavior', 'knowledge', name='trainingcorrectiontype'), nullable=False),
        sa.Column('original_content', sa.Text(), nullable=True),
        sa.Column('corrected_content', sa.Text(), nullable=False),
        sa.Column('improvement_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('applied_at', sa.DateTime(), nullable=True),
        sa.Column('status', sa.Enum('pending', 'applied', 'rejected', name='trainingcorrectionstatus'), nullable=False),
        sa.ForeignKeyConstraint(['interaction_id'], ['training_interactions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for performance
    op.create_index(op.f('idx_training_sessions_agent'), 'training_sessions', ['agent_id'], unique=False)
    op.create_index(op.f('idx_training_sessions_user'), 'training_sessions', ['user_id'], unique=False)
    op.create_index(op.f('idx_training_interactions_session'), 'training_interactions', ['session_id'], unique=False)
    op.create_index(op.f('idx_training_corrections_interaction'), 'training_corrections', ['interaction_id'], unique=False)


def downgrade():
    # Drop indexes
    op.drop_index(op.f('idx_training_corrections_interaction'))
    op.drop_index(op.f('idx_training_interactions_session'))
    op.drop_index(op.f('idx_training_sessions_user'))
    op.drop_index(op.f('idx_training_sessions_agent'))
    
    # Drop tables
    op.drop_table('training_corrections')
    op.drop_table('training_interactions')
    op.drop_table('training_sessions')
