"""integration submissions lifecycle

Revision ID: integration_submissions_001
Revises: social_accounts_001
Create Date: 2026-02-13
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "integration_submissions_001"
down_revision = "social_accounts_001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    table_names = set(inspector.get_table_names())
    now_expr = sa.text("now()") if bind.dialect.name == "postgresql" else sa.text("CURRENT_TIMESTAMP")

    if "integrations" in table_names:
        existing_columns = {column["name"] for column in inspector.get_columns("integrations")}
        column_defs = [
            ("status", sa.Column("status", sa.String(length=30), nullable=False, server_default="draft")),
            ("submission_notes", sa.Column("submission_notes", sa.Text(), nullable=True)),
            ("moderation_notes", sa.Column("moderation_notes", sa.Text(), nullable=True)),
            ("submitted_at", sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True)),
            ("reviewed_at", sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True)),
            ("published_at", sa.Column("published_at", sa.DateTime(timezone=True), nullable=True)),
            ("reviewed_by", sa.Column("reviewed_by", sa.Integer(), nullable=True)),
            ("visibility", sa.Column("visibility", sa.String(length=20), nullable=False, server_default="private")),
            ("app_icon_url", sa.Column("app_icon_url", sa.String(length=500), nullable=True)),
            ("app_screenshots", sa.Column("app_screenshots", sa.JSON(), nullable=False, server_default="[]")),
            ("developer_name", sa.Column("developer_name", sa.String(length=200), nullable=True)),
            ("website_url", sa.Column("website_url", sa.String(length=500), nullable=True)),
            ("support_url_or_email", sa.Column("support_url_or_email", sa.String(length=500), nullable=True)),
            ("privacy_policy_url", sa.Column("privacy_policy_url", sa.String(length=500), nullable=True)),
            ("terms_url", sa.Column("terms_url", sa.String(length=500), nullable=True)),
            ("demo_url", sa.Column("demo_url", sa.String(length=500), nullable=True)),
            ("is_workflow_node_enabled", sa.Column("is_workflow_node_enabled", sa.Boolean(), nullable=False, server_default="false")),
            ("subtitle", sa.Column("subtitle", sa.String(length=120), nullable=True)),
        ]
        for column_name, column_def in column_defs:
            if column_name not in existing_columns:
                op.add_column("integrations", column_def)

        if bind.dialect.name != "sqlite" and "users" in table_names:
            op.create_foreign_key(
                "fk_integrations_reviewed_by_users",
                "integrations",
                "users",
                ["reviewed_by"],
                ["id"],
            )

        existing_indexes = {index["name"] for index in inspector.get_indexes("integrations")}
        if "ix_integrations_status" not in existing_indexes:
            op.create_index("ix_integrations_status", "integrations", ["status"], unique=False)
        if "ix_integrations_visibility" not in existing_indexes:
            op.create_index("ix_integrations_visibility", "integrations", ["visibility"], unique=False)
        if "ix_integrations_is_workflow_node_enabled" not in existing_indexes:
            op.create_index("ix_integrations_is_workflow_node_enabled", "integrations", ["is_workflow_node_enabled"], unique=False)

        if "integration_submission_events" not in table_names:
            op.create_table(
                "integration_submission_events",
                sa.Column("id", sa.Integer(), nullable=False),
                sa.Column("integration_id", sa.Integer(), nullable=False),
                sa.Column("action", sa.String(length=40), nullable=False),
                sa.Column("actor_user_id", sa.Integer(), nullable=True),
                sa.Column("payload", sa.JSON(), nullable=False, server_default="{}"),
                sa.Column("created_at", sa.DateTime(timezone=True), server_default=now_expr, nullable=False),
                sa.Column("updated_at", sa.DateTime(timezone=True), server_default=now_expr, nullable=False),
                sa.ForeignKeyConstraint(["integration_id"], ["integrations.id"], ondelete="CASCADE"),
                sa.ForeignKeyConstraint(["actor_user_id"], ["users.id"], ondelete="SET NULL"),
                sa.PrimaryKeyConstraint("id"),
            )
            op.create_index(op.f("ix_integration_submission_events_id"), "integration_submission_events", ["id"], unique=False)
            op.create_index(op.f("ix_integration_submission_events_integration_id"), "integration_submission_events", ["integration_id"], unique=False)
            op.create_index(op.f("ix_integration_submission_events_actor_user_id"), "integration_submission_events", ["actor_user_id"], unique=False)

    if "user_plans" in table_names:
        # Backfill old pro users into the new team_developer canonical plan.
        op.execute("UPDATE user_plans SET plan_type = 'team_developer' WHERE plan_type = 'pro'")


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    table_names = set(inspector.get_table_names())

    if "user_plans" in table_names:
        op.execute("UPDATE user_plans SET plan_type = 'pro' WHERE plan_type = 'team_developer'")

    if "integrations" not in table_names:
        return

    if "integration_submission_events" in table_names:
        op.drop_index(op.f("ix_integration_submission_events_actor_user_id"), table_name="integration_submission_events")
        op.drop_index(op.f("ix_integration_submission_events_integration_id"), table_name="integration_submission_events")
        op.drop_index(op.f("ix_integration_submission_events_id"), table_name="integration_submission_events")
        op.drop_table("integration_submission_events")

    op.drop_index("ix_integrations_is_workflow_node_enabled", table_name="integrations")
    op.drop_index("ix_integrations_visibility", table_name="integrations")
    op.drop_index("ix_integrations_status", table_name="integrations")
    if bind.dialect.name != "sqlite":
        op.drop_constraint("fk_integrations_reviewed_by_users", "integrations", type_="foreignkey")
    op.drop_column("integrations", "subtitle")
    op.drop_column("integrations", "is_workflow_node_enabled")
    op.drop_column("integrations", "demo_url")
    op.drop_column("integrations", "terms_url")
    op.drop_column("integrations", "privacy_policy_url")
    op.drop_column("integrations", "support_url_or_email")
    op.drop_column("integrations", "website_url")
    op.drop_column("integrations", "developer_name")
    op.drop_column("integrations", "app_screenshots")
    op.drop_column("integrations", "app_icon_url")
    op.drop_column("integrations", "visibility")
    op.drop_column("integrations", "reviewed_by")
    op.drop_column("integrations", "published_at")
    op.drop_column("integrations", "reviewed_at")
    op.drop_column("integrations", "submitted_at")
    op.drop_column("integrations", "moderation_notes")
    op.drop_column("integrations", "submission_notes")
    op.drop_column("integrations", "status")
