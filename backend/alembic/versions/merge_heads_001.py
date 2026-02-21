"""Merge parallel alembic heads.

Revision ID: merge_heads_001
Revises: add_agent_type_field, integration_submissions_001, playwright_models_001
Create Date: 2026-02-13
"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "merge_heads_001"
down_revision = ("add_agent_type_field", "integration_submissions_001", "playwright_models_001")
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass

