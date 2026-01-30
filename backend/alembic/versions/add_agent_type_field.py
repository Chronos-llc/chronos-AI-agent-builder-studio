"""Add Agent Type Field to Agents Table

Revision ID: add_agent_type_field
Revises: add_marketplace_fields_to_agents
Create Date: 2026-01-30 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_agent_type_field'
down_revision = 'add_marketplace_fields_to_agents'
branch_labels = None
depends_on = None

def upgrade():
    # Add agent_type column with default value
    op.add_column('agents', sa.Column('agent_type', sa.Enum('text', 'voice', name='agenttype'), server_default='text', nullable=True))
    
    # Create index for efficient filtering
    op.create_index('idx_agents_agent_type', 'agents', ['agent_type'])
    
    # Migrate existing data: set agent_type = 'voice' where voice_configuration exists and voice_enabled is true
    connection = op.get_bind()
    
    # Get all agents with voice configurations that are enabled
    result = connection.execute(sa.text("""
        SELECT a.id FROM agents a
        JOIN voice_configurations vc ON a.id = vc.agent_id
        WHERE vc.voice_enabled = true
    """))
    
    voice_agent_ids = [row[0] for row in result]
    
    if voice_agent_ids:
        # Update these agents to have agent_type = 'voice'
        connection.execute(sa.text("""
            UPDATE agents
            SET agent_type = 'voice'
            WHERE id IN :agent_ids
        """), {'agent_ids': tuple(voice_agent_ids)})
    
    # Set default for remaining agents
    connection.execute(sa.text("""
        UPDATE agents
        SET agent_type = 'text'
        WHERE agent_type IS NULL
    """))
    
    # Make column non-nullable
    op.alter_column('agents', 'agent_type', nullable=False)


def downgrade():
    # Drop index
    op.drop_index('idx_agents_agent_type')
    
    # Drop column
    op.drop_column('agents', 'agent_type')
