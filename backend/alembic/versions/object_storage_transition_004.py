"""Object storage transition columns for file/image domains.

Revision ID: object_storage_transition_004
Revises: skills_marketplace_003
Create Date: 2026-02-20 12:15:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "object_storage_transition_004"
down_revision = "skills_marketplace_003"
branch_labels = None
depends_on = None


def _table_exists(inspector: sa.Inspector, table_name: str) -> bool:
    return table_name in inspector.get_table_names()


def _column_exists(inspector: sa.Inspector, table_name: str, column_name: str) -> bool:
    if not _table_exists(inspector, table_name):
        return False
    return any(column["name"] == column_name for column in inspector.get_columns(table_name))


def _index_exists(inspector: sa.Inspector, table_name: str, index_name: str) -> bool:
    if not _table_exists(inspector, table_name):
        return False
    return any(index.get("name") == index_name for index in inspector.get_indexes(table_name))


def _add_object_columns(table_name: str) -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if not _table_exists(inspector, table_name):
        return

    with op.batch_alter_table(table_name) as batch_op:
        if not _column_exists(inspector, table_name, "object_key"):
            batch_op.add_column(sa.Column("object_key", sa.String(length=1024), nullable=True))
        if not _column_exists(inspector, table_name, "object_size"):
            batch_op.add_column(sa.Column("object_size", sa.Integer(), nullable=True))
        if not _column_exists(inspector, table_name, "object_content_type"):
            batch_op.add_column(sa.Column("object_content_type", sa.String(length=255), nullable=True))
        if not _column_exists(inspector, table_name, "object_etag"):
            batch_op.add_column(sa.Column("object_etag", sa.String(length=128), nullable=True))
        if not _column_exists(inspector, table_name, "storage_provider"):
            batch_op.add_column(sa.Column("storage_provider", sa.String(length=32), nullable=True))
        if not _column_exists(inspector, table_name, "storage_bucket"):
            batch_op.add_column(sa.Column("storage_bucket", sa.String(length=128), nullable=True))

    inspector = sa.inspect(bind)
    index_name = f"ix_{table_name}_object_key"
    if _column_exists(inspector, table_name, "object_key") and not _index_exists(
        inspector, table_name, index_name
    ):
        op.create_index(index_name, table_name, ["object_key"], unique=False)


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    _add_object_columns("skill_versions")
    _add_object_columns("knowledge_files")
    _add_object_columns("playwright_tool_executions")
    _add_object_columns("playwright_artifacts")

    # Legacy transition: allow null raw_content to avoid persisting full file payloads.
    inspector = sa.inspect(bind)
    if _table_exists(inspector, "skill_versions") and _column_exists(
        inspector, "skill_versions", "raw_content"
    ):
        try:
            with op.batch_alter_table("skill_versions") as batch_op:
                batch_op.alter_column(
                    "raw_content",
                    existing_type=sa.Text(),
                    nullable=True,
                )
        except Exception:
            # SQLite/legacy compatibility: keep column as-is when alteration is unsupported.
            pass


def _drop_object_columns(table_name: str) -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if not _table_exists(inspector, table_name):
        return

    index_name = f"ix_{table_name}_object_key"
    if _index_exists(inspector, table_name, index_name):
        op.drop_index(index_name, table_name=table_name)

    inspector = sa.inspect(bind)
    with op.batch_alter_table(table_name) as batch_op:
        for column_name in [
            "storage_bucket",
            "storage_provider",
            "object_etag",
            "object_content_type",
            "object_size",
            "object_key",
        ]:
            if _column_exists(inspector, table_name, column_name):
                batch_op.drop_column(column_name)


def downgrade() -> None:
    _drop_object_columns("playwright_artifacts")
    _drop_object_columns("playwright_tool_executions")
    _drop_object_columns("knowledge_files")
    _drop_object_columns("skill_versions")
