"""Align skills schema with current SQLAlchemy models.

Revision ID: skills_schema_alignment_002
Revises: onboarding_impersonation_001
Create Date: 2026-02-14 09:20:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "skills_schema_alignment_002"
down_revision = "onboarding_impersonation_001"
branch_labels = None
depends_on = None


def _table_exists(inspector: sa.Inspector, table_name: str) -> bool:
    return table_name in inspector.get_table_names()


def _column_exists(inspector: sa.Inspector, table_name: str, column_name: str) -> bool:
    return any(column["name"] == column_name for column in inspector.get_columns(table_name))


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if _table_exists(inspector, "agent_skills"):
        add_version = not _column_exists(inspector, "agent_skills", "version")
        add_parameters = not _column_exists(inspector, "agent_skills", "parameters")
        add_tags = not _column_exists(inspector, "agent_skills", "tags")

        if add_version or add_parameters or add_tags:
            with op.batch_alter_table("agent_skills") as batch_op:
                if add_version:
                    batch_op.add_column(sa.Column("version", sa.String(length=20), nullable=True))
                if add_parameters:
                    batch_op.add_column(sa.Column("parameters", sa.JSON(), nullable=True))
                if add_tags:
                    batch_op.add_column(sa.Column("tags", sa.JSON(), nullable=True))

    if _table_exists(inspector, "agent_skill_installations"):
        add_configuration = not _column_exists(inspector, "agent_skill_installations", "configuration")
        add_is_enabled = not _column_exists(inspector, "agent_skill_installations", "is_enabled")
        default_true = sa.text("1") if bind.dialect.name == "sqlite" else sa.text("true")

        if add_configuration or add_is_enabled:
            with op.batch_alter_table("agent_skill_installations") as batch_op:
                if add_configuration:
                    batch_op.add_column(sa.Column("configuration", sa.JSON(), nullable=True))
                if add_is_enabled:
                    batch_op.add_column(
                        sa.Column(
                            "is_enabled",
                            sa.Boolean(),
                            nullable=False,
                            server_default=default_true,
                        )
                    )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if _table_exists(inspector, "agent_skill_installations"):
        drop_configuration = _column_exists(inspector, "agent_skill_installations", "configuration")
        drop_is_enabled = _column_exists(inspector, "agent_skill_installations", "is_enabled")
        if drop_configuration or drop_is_enabled:
            with op.batch_alter_table("agent_skill_installations") as batch_op:
                if drop_is_enabled:
                    batch_op.drop_column("is_enabled")
                if drop_configuration:
                    batch_op.drop_column("configuration")

    if _table_exists(inspector, "agent_skills"):
        drop_tags = _column_exists(inspector, "agent_skills", "tags")
        drop_parameters = _column_exists(inspector, "agent_skills", "parameters")
        drop_version = _column_exists(inspector, "agent_skills", "version")
        if drop_tags or drop_parameters or drop_version:
            with op.batch_alter_table("agent_skills") as batch_op:
                if drop_tags:
                    batch_op.drop_column("tags")
                if drop_parameters:
                    batch_op.drop_column("parameters")
                if drop_version:
                    batch_op.drop_column("version")
