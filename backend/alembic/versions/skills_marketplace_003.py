"""Skills marketplace workflow tables and lifecycle fields.

Revision ID: skills_marketplace_003
Revises: skills_schema_alignment_002
Create Date: 2026-02-20 09:45:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "skills_marketplace_003"
down_revision = "skills_schema_alignment_002"
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
        with op.batch_alter_table("agent_skills") as batch_op:
            if not _column_exists(inspector, "agent_skills", "download_count"):
                batch_op.add_column(
                    sa.Column("download_count", sa.Integer(), nullable=False, server_default="0")
                )
            if not _column_exists(inspector, "agent_skills", "submission_status"):
                batch_op.add_column(
                    sa.Column(
                        "submission_status",
                        sa.String(length=30),
                        nullable=False,
                        server_default="published",
                    )
                )
            if not _column_exists(inspector, "agent_skills", "visibility"):
                batch_op.add_column(
                    sa.Column(
                        "visibility",
                        sa.String(length=20),
                        nullable=False,
                        server_default="public",
                    )
                )
            if not _column_exists(inspector, "agent_skills", "published_at"):
                batch_op.add_column(sa.Column("published_at", sa.DateTime(timezone=True), nullable=True))
            if not _column_exists(inspector, "agent_skills", "reviewed_at"):
                batch_op.add_column(sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True))
            if not _column_exists(inspector, "agent_skills", "reviewed_by"):
                batch_op.add_column(sa.Column("reviewed_by", sa.Integer(), nullable=True))
            if not _column_exists(inspector, "agent_skills", "review_notes"):
                batch_op.add_column(sa.Column("review_notes", sa.Text(), nullable=True))
            if not _column_exists(inspector, "agent_skills", "scan_status"):
                batch_op.add_column(
                    sa.Column(
                        "scan_status",
                        sa.String(length=20),
                        nullable=False,
                        server_default="pending",
                    )
                )
            if not _column_exists(inspector, "agent_skills", "scan_confidence"):
                batch_op.add_column(
                    sa.Column("scan_confidence", sa.Integer(), nullable=False, server_default="0")
                )
            if not _column_exists(inspector, "agent_skills", "scan_summary"):
                batch_op.add_column(sa.Column("scan_summary", sa.Text(), nullable=True))

    inspector = sa.inspect(bind)

    if not _table_exists(inspector, "skill_versions"):
        op.create_table(
            "skill_versions",
            sa.Column("skill_id", sa.Integer(), nullable=False),
            sa.Column("version", sa.String(length=50), nullable=False),
            sa.Column("file_name", sa.String(length=255), nullable=False),
            sa.Column("file_path", sa.String(length=500), nullable=False),
            sa.Column("file_sha256", sa.String(length=64), nullable=False),
            sa.Column("raw_content", sa.Text(), nullable=False),
            sa.Column("manifest_json", sa.JSON(), nullable=True),
            sa.Column("is_current", sa.Boolean(), nullable=False, server_default="1"),
            sa.Column("scan_status", sa.String(length=20), nullable=False, server_default="pending"),
            sa.Column("scan_report_json", sa.JSON(), nullable=True),
            sa.Column("created_by", sa.Integer(), nullable=True),
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["skill_id"], ["agent_skills.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("skill_id", "version", name="uq_skill_version_per_skill"),
        )
        op.create_index("ix_skill_versions_skill_id", "skill_versions", ["skill_id"])
        op.create_index("ix_skill_versions_file_sha256", "skill_versions", ["file_sha256"])
        op.create_index("ix_skill_versions_id", "skill_versions", ["id"])

    inspector = sa.inspect(bind)
    if not _table_exists(inspector, "skill_review_events"):
        op.create_table(
            "skill_review_events",
            sa.Column("skill_id", sa.Integer(), nullable=False),
            sa.Column("version_id", sa.Integer(), nullable=True),
            sa.Column("action", sa.String(length=40), nullable=False),
            sa.Column("actor_user_id", sa.Integer(), nullable=True),
            sa.Column("payload", sa.JSON(), nullable=False),
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["skill_id"], ["agent_skills.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["version_id"], ["skill_versions.id"], ondelete="SET NULL"),
            sa.ForeignKeyConstraint(["actor_user_id"], ["users.id"], ondelete="SET NULL"),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_skill_review_events_skill_id", "skill_review_events", ["skill_id"])
        op.create_index("ix_skill_review_events_version_id", "skill_review_events", ["version_id"])
        op.create_index("ix_skill_review_events_action", "skill_review_events", ["action"])
        op.create_index("ix_skill_review_events_actor_user_id", "skill_review_events", ["actor_user_id"])
        op.create_index("ix_skill_review_events_id", "skill_review_events", ["id"])

    inspector = sa.inspect(bind)
    if not _table_exists(inspector, "fuzzy_knowledge_entries"):
        op.create_table(
            "fuzzy_knowledge_entries",
            sa.Column("title", sa.String(length=255), nullable=False),
            sa.Column("content", sa.Text(), nullable=False),
            sa.Column("content_hash", sa.String(length=64), nullable=False),
            sa.Column("entry_metadata", sa.JSON(), nullable=True),
            sa.Column("installed_by", sa.Integer(), nullable=True),
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["installed_by"], ["users.id"], ondelete="SET NULL"),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_fuzzy_knowledge_entries_content_hash", "fuzzy_knowledge_entries", ["content_hash"])
        op.create_index("ix_fuzzy_knowledge_entries_id", "fuzzy_knowledge_entries", ["id"])

    inspector = sa.inspect(bind)
    if not _table_exists(inspector, "fuzzy_skill_installations"):
        op.create_table(
            "fuzzy_skill_installations",
            sa.Column("skill_id", sa.Integer(), nullable=False),
            sa.Column("version_id", sa.Integer(), nullable=True),
            sa.Column("knowledge_entry_id", sa.Integer(), nullable=False),
            sa.Column("installed_by", sa.Integer(), nullable=True),
            sa.Column("status", sa.String(length=20), nullable=False, server_default="installed"),
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["skill_id"], ["agent_skills.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["version_id"], ["skill_versions.id"], ondelete="SET NULL"),
            sa.ForeignKeyConstraint(["knowledge_entry_id"], ["fuzzy_knowledge_entries.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["installed_by"], ["users.id"], ondelete="SET NULL"),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_fuzzy_skill_installations_skill_id", "fuzzy_skill_installations", ["skill_id"])
        op.create_index("ix_fuzzy_skill_installations_version_id", "fuzzy_skill_installations", ["version_id"])
        op.create_index(
            "ix_fuzzy_skill_installations_knowledge_entry_id",
            "fuzzy_skill_installations",
            ["knowledge_entry_id"],
        )
        op.create_index(
            "ix_fuzzy_skill_installations_installed_by",
            "fuzzy_skill_installations",
            ["installed_by"],
        )
        op.create_index("ix_fuzzy_skill_installations_id", "fuzzy_skill_installations", ["id"])

    # Backfill existing skills to published defaults.
    if _table_exists(sa.inspect(bind), "agent_skills"):
        op.execute(
            sa.text(
                "UPDATE agent_skills "
                "SET submission_status = COALESCE(submission_status, 'published'), "
                "visibility = COALESCE(visibility, 'public'), "
                "scan_status = COALESCE(scan_status, 'pending'), "
                "scan_confidence = COALESCE(scan_confidence, 0)"
            )
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if _table_exists(inspector, "fuzzy_skill_installations"):
        op.drop_table("fuzzy_skill_installations")
    if _table_exists(inspector, "fuzzy_knowledge_entries"):
        op.drop_table("fuzzy_knowledge_entries")
    if _table_exists(inspector, "skill_review_events"):
        op.drop_table("skill_review_events")
    if _table_exists(inspector, "skill_versions"):
        op.drop_table("skill_versions")

    inspector = sa.inspect(bind)
    if _table_exists(inspector, "agent_skills"):
        with op.batch_alter_table("agent_skills") as batch_op:
            if _column_exists(inspector, "agent_skills", "scan_summary"):
                batch_op.drop_column("scan_summary")
            if _column_exists(inspector, "agent_skills", "scan_confidence"):
                batch_op.drop_column("scan_confidence")
            if _column_exists(inspector, "agent_skills", "scan_status"):
                batch_op.drop_column("scan_status")
            if _column_exists(inspector, "agent_skills", "review_notes"):
                batch_op.drop_column("review_notes")
            if _column_exists(inspector, "agent_skills", "reviewed_by"):
                batch_op.drop_column("reviewed_by")
            if _column_exists(inspector, "agent_skills", "reviewed_at"):
                batch_op.drop_column("reviewed_at")
            if _column_exists(inspector, "agent_skills", "published_at"):
                batch_op.drop_column("published_at")
            if _column_exists(inspector, "agent_skills", "visibility"):
                batch_op.drop_column("visibility")
            if _column_exists(inspector, "agent_skills", "submission_status"):
                batch_op.drop_column("submission_status")
            if _column_exists(inspector, "agent_skills", "download_count"):
                batch_op.drop_column("download_count")
