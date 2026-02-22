"""Usage metering, add-ons, workspace seats, and user balance tables.

Revision ID: usage_metering_addons_balance_005
Revises: object_storage_transition_004
Create Date: 2026-02-22 10:00:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "usage_metering_addons_balance_005"
down_revision = "object_storage_transition_004"
branch_labels = None
depends_on = None


def _table_exists(inspector: sa.Inspector, table_name: str) -> bool:
    return table_name in inspector.get_table_names()


def _index_exists(inspector: sa.Inspector, table_name: str, index_name: str) -> bool:
    if not _table_exists(inspector, table_name):
        return False
    return any(index.get("name") == index_name for index in inspector.get_indexes(table_name))


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not _table_exists(inspector, "workspace_members"):
        op.create_table(
            "workspace_members",
            sa.Column("owner_user_id", sa.Integer(), nullable=False),
            sa.Column("member_user_id", sa.Integer(), nullable=False),
            sa.Column("role", sa.String(length=50), nullable=False, server_default="member"),
            sa.Column("status", sa.String(length=20), nullable=False, server_default="active"),
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["member_user_id"], ["users.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["owner_user_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("owner_user_id", "member_user_id", name="uq_workspace_member_owner_member"),
        )
        op.create_index("ix_workspace_members_owner_user_id", "workspace_members", ["owner_user_id"], unique=False)
        op.create_index("ix_workspace_members_member_user_id", "workspace_members", ["member_user_id"], unique=False)
        op.create_index("ix_workspace_members_status", "workspace_members", ["status"], unique=False)

    if not _table_exists(inspector, "user_addon_allocations"):
        resource_enum = sa.Enum(
            "AI_SPEND",
            "FILE_STORAGE",
            "VECTOR_DB_STORAGE",
            "TABLE_ROWS",
            "COLLABORATORS",
            "AGENTS",
            name="resourcetype",
        )
        op.create_table(
            "user_addon_allocations",
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("resource_type", resource_enum, nullable=False),
            sa.Column("units", sa.Integer(), nullable=False, server_default="1"),
            sa.Column("unit_price_usd", sa.Float(), nullable=False, server_default="0"),
            sa.Column("currency", sa.String(length=3), nullable=False, server_default="USD"),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
            sa.Column("effective_from", sa.DateTime(timezone=True), nullable=False),
            sa.Column("effective_to", sa.DateTime(timezone=True), nullable=True),
            sa.Column("additional_metadata", sa.JSON(), nullable=True),
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_user_addon_allocations_user_id", "user_addon_allocations", ["user_id"], unique=False)
        op.create_index("ix_user_addon_allocations_resource_type", "user_addon_allocations", ["resource_type"], unique=False)
        op.create_index("ix_user_addon_allocations_is_active", "user_addon_allocations", ["is_active"], unique=False)

    if not _table_exists(inspector, "ai_spend_events"):
        op.create_table(
            "ai_spend_events",
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("agent_id", sa.Integer(), nullable=True),
            sa.Column("provider", sa.String(length=100), nullable=True),
            sa.Column("model", sa.String(length=150), nullable=True),
            sa.Column("cost_amount", sa.Float(), nullable=False),
            sa.Column("currency", sa.String(length=3), nullable=False, server_default="USD"),
            sa.Column("tokens", sa.Integer(), nullable=True),
            sa.Column("source", sa.String(length=100), nullable=True),
            sa.Column("additional_metadata", sa.JSON(), nullable=True),
            sa.Column("event_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["agent_id"], ["agents.id"], ondelete="SET NULL"),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_ai_spend_events_user_id", "ai_spend_events", ["user_id"], unique=False)
        op.create_index("ix_ai_spend_events_agent_id", "ai_spend_events", ["agent_id"], unique=False)
        op.create_index("ix_ai_spend_events_event_at", "ai_spend_events", ["event_at"], unique=False)

    if not _table_exists(inspector, "user_balance_accounts"):
        op.create_table(
            "user_balance_accounts",
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("currency", sa.String(length=3), nullable=False),
            sa.Column("balance", sa.Numeric(precision=16, scale=4), nullable=False, server_default="0"),
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("user_id", "currency", name="uq_user_balance_account_currency"),
        )
        op.create_index("ix_user_balance_accounts_user_id", "user_balance_accounts", ["user_id"], unique=False)
        op.create_index("ix_user_balance_accounts_currency", "user_balance_accounts", ["currency"], unique=False)

    if not _table_exists(inspector, "user_balance_transactions"):
        op.create_table(
            "user_balance_transactions",
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("currency", sa.String(length=3), nullable=False),
            sa.Column("amount_delta", sa.Numeric(precision=16, scale=4), nullable=False),
            sa.Column("reason", sa.String(length=255), nullable=False),
            sa.Column("admin_user_id", sa.Integer(), nullable=True),
            sa.Column("additional_metadata", sa.JSON(), nullable=True),
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["admin_user_id"], ["users.id"], ondelete="SET NULL"),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_user_balance_transactions_user_id", "user_balance_transactions", ["user_id"], unique=False)
        op.create_index("ix_user_balance_transactions_currency", "user_balance_transactions", ["currency"], unique=False)
        op.create_index("ix_user_balance_transactions_admin_user_id", "user_balance_transactions", ["admin_user_id"], unique=False)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if _table_exists(inspector, "user_balance_transactions"):
        op.drop_table("user_balance_transactions")

    inspector = sa.inspect(bind)
    if _table_exists(inspector, "user_balance_accounts"):
        op.drop_table("user_balance_accounts")

    inspector = sa.inspect(bind)
    if _table_exists(inspector, "ai_spend_events"):
        op.drop_table("ai_spend_events")

    inspector = sa.inspect(bind)
    if _table_exists(inspector, "user_addon_allocations"):
        op.drop_table("user_addon_allocations")

    inspector = sa.inspect(bind)
    if _table_exists(inspector, "workspace_members"):
        op.drop_table("workspace_members")

