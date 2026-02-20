"""Startup schema alignment for legacy skills tables.

This keeps local/dev databases compatible with the current SQLAlchemy skills
models when older tables already exist without newer columns.
"""

from __future__ import annotations

import logging

import sqlalchemy as sa

from app.core.database import engine

logger = logging.getLogger(__name__)


def _column_exists(inspector: sa.Inspector, table_name: str, column_name: str) -> bool:
    return any(column["name"] == column_name for column in inspector.get_columns(table_name))


def _table_exists(inspector: sa.Inspector, table_name: str) -> bool:
    return table_name in inspector.get_table_names()


def _add_column_if_missing(
    connection: sa.Connection,
    inspector: sa.Inspector,
    table_name: str,
    column_name: str,
    column_type_sql: str,
) -> None:
    if not _table_exists(inspector, table_name):
        return
    if _column_exists(inspector, table_name, column_name):
        return

    preparer = connection.dialect.identifier_preparer
    quoted_table = preparer.quote(table_name)
    quoted_column = preparer.quote(column_name)

    connection.execute(
        sa.text(
            f"ALTER TABLE {quoted_table} "
            f"ADD COLUMN {quoted_column} {column_type_sql}"
        )
    )
    logger.info("Aligned schema: added %s.%s", table_name, column_name)


def _align_skills_schema(connection: sa.Connection) -> None:
    inspector = sa.inspect(connection)
    dialect_name = connection.dialect.name
    bool_default_true = "1" if dialect_name == "sqlite" else "TRUE"
    timestamp_type = "DATETIME" if dialect_name == "sqlite" else "TIMESTAMP WITH TIME ZONE"
    now_default = "CURRENT_TIMESTAMP" if dialect_name == "sqlite" else "NOW()"

    _add_column_if_missing(connection, inspector, "agent_skills", "version", "VARCHAR(20)")
    _add_column_if_missing(connection, inspector, "agent_skills", "parameters", "JSON")
    _add_column_if_missing(connection, inspector, "agent_skills", "tags", "JSON")
    _add_column_if_missing(connection, inspector, "agent_skills", "download_count", "INTEGER NOT NULL DEFAULT 0")
    _add_column_if_missing(
        connection,
        inspector,
        "agent_skills",
        "submission_status",
        "VARCHAR(30) NOT NULL DEFAULT 'published'",
    )
    _add_column_if_missing(
        connection,
        inspector,
        "agent_skills",
        "visibility",
        "VARCHAR(20) NOT NULL DEFAULT 'public'",
    )
    _add_column_if_missing(connection, inspector, "agent_skills", "published_at", f"{timestamp_type} NULL")
    _add_column_if_missing(connection, inspector, "agent_skills", "reviewed_at", f"{timestamp_type} NULL")
    _add_column_if_missing(connection, inspector, "agent_skills", "reviewed_by", "INTEGER NULL")
    _add_column_if_missing(connection, inspector, "agent_skills", "review_notes", "TEXT NULL")
    _add_column_if_missing(
        connection,
        inspector,
        "agent_skills",
        "scan_status",
        "VARCHAR(20) NOT NULL DEFAULT 'pending'",
    )
    _add_column_if_missing(
        connection,
        inspector,
        "agent_skills",
        "scan_confidence",
        "INTEGER NOT NULL DEFAULT 0",
    )
    _add_column_if_missing(connection, inspector, "agent_skills", "scan_summary", "TEXT NULL")

    _add_column_if_missing(
        connection,
        inspector,
        "agent_skill_installations",
        "configuration",
        "JSON",
    )
    _add_column_if_missing(
        connection,
        inspector,
        "agent_skill_installations",
        "is_enabled",
        f"BOOLEAN NOT NULL DEFAULT {bool_default_true}",
    )
    _add_column_if_missing(
        connection,
        inspector,
        "agent_skill_installations",
        "created_at",
        f"{timestamp_type} NOT NULL DEFAULT {now_default}",
    )
    _add_column_if_missing(
        connection,
        inspector,
        "agent_skill_installations",
        "updated_at",
        f"{timestamp_type} NOT NULL DEFAULT {now_default}",
    )

    # Object-storage transition columns
    _add_column_if_missing(connection, inspector, "skill_versions", "object_key", "VARCHAR(1024)")
    _add_column_if_missing(connection, inspector, "skill_versions", "object_size", "INTEGER")
    _add_column_if_missing(
        connection,
        inspector,
        "skill_versions",
        "object_content_type",
        "VARCHAR(255)",
    )
    _add_column_if_missing(connection, inspector, "skill_versions", "object_etag", "VARCHAR(128)")
    _add_column_if_missing(connection, inspector, "skill_versions", "storage_provider", "VARCHAR(32)")
    _add_column_if_missing(connection, inspector, "skill_versions", "storage_bucket", "VARCHAR(128)")

    _add_column_if_missing(connection, inspector, "knowledge_files", "object_key", "VARCHAR(1024)")
    _add_column_if_missing(connection, inspector, "knowledge_files", "object_size", "INTEGER")
    _add_column_if_missing(
        connection,
        inspector,
        "knowledge_files",
        "object_content_type",
        "VARCHAR(255)",
    )
    _add_column_if_missing(connection, inspector, "knowledge_files", "object_etag", "VARCHAR(128)")
    _add_column_if_missing(connection, inspector, "knowledge_files", "storage_provider", "VARCHAR(32)")
    _add_column_if_missing(connection, inspector, "knowledge_files", "storage_bucket", "VARCHAR(128)")

    _add_column_if_missing(connection, inspector, "playwright_tool_executions", "object_key", "VARCHAR(1024)")
    _add_column_if_missing(connection, inspector, "playwright_tool_executions", "object_size", "INTEGER")
    _add_column_if_missing(
        connection,
        inspector,
        "playwright_tool_executions",
        "object_content_type",
        "VARCHAR(255)",
    )
    _add_column_if_missing(connection, inspector, "playwright_tool_executions", "object_etag", "VARCHAR(128)")
    _add_column_if_missing(
        connection,
        inspector,
        "playwright_tool_executions",
        "storage_provider",
        "VARCHAR(32)",
    )
    _add_column_if_missing(
        connection,
        inspector,
        "playwright_tool_executions",
        "storage_bucket",
        "VARCHAR(128)",
    )

    _add_column_if_missing(connection, inspector, "playwright_artifacts", "object_key", "VARCHAR(1024)")
    _add_column_if_missing(connection, inspector, "playwright_artifacts", "object_size", "INTEGER")
    _add_column_if_missing(
        connection,
        inspector,
        "playwright_artifacts",
        "object_content_type",
        "VARCHAR(255)",
    )
    _add_column_if_missing(connection, inspector, "playwright_artifacts", "object_etag", "VARCHAR(128)")
    _add_column_if_missing(connection, inspector, "playwright_artifacts", "storage_provider", "VARCHAR(32)")
    _add_column_if_missing(connection, inspector, "playwright_artifacts", "storage_bucket", "VARCHAR(128)")


async def ensure_skills_schema_alignment() -> None:
    async with engine.begin() as connection:
        await connection.run_sync(_align_skills_schema)
