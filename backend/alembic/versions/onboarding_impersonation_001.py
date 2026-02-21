"""split onboarding state fields

Revision ID: onboarding_impersonation_001
Revises: merge_heads_001
Create Date: 2026-02-14
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "onboarding_impersonation_001"
down_revision = "merge_heads_001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    table_names = set(inspector.get_table_names())

    if "user_profiles" not in table_names:
        return

    existing_columns = {column["name"] for column in inspector.get_columns("user_profiles")}

    if "fuzzy_onboarding_state" not in existing_columns:
        op.add_column(
            "user_profiles",
            sa.Column(
                "fuzzy_onboarding_state",
                sa.String(length=20),
                nullable=False,
                server_default="pending",
            ),
        )
    if "fuzzy_onboarding_completed_at" not in existing_columns:
        op.add_column(
            "user_profiles",
            sa.Column("fuzzy_onboarding_completed_at", sa.DateTime(timezone=True), nullable=True),
        )
    if "fuzzy_onboarding_skipped_at" not in existing_columns:
        op.add_column(
            "user_profiles",
            sa.Column("fuzzy_onboarding_skipped_at", sa.DateTime(timezone=True), nullable=True),
        )

    # Existing users that already completed onboarding should see fuzzy prompt once.
    op.execute(
        "UPDATE user_profiles "
        "SET fuzzy_onboarding_state = 'pending' "
        "WHERE onboarding_completed = 1 "
        "AND (fuzzy_onboarding_state IS NULL OR fuzzy_onboarding_state = '')"
    )
    op.execute(
        "UPDATE user_profiles "
        "SET fuzzy_onboarding_state = 'pending' "
        "WHERE fuzzy_onboarding_state IS NULL OR fuzzy_onboarding_state = ''"
    )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    table_names = set(inspector.get_table_names())
    if "user_profiles" not in table_names:
        return

    existing_columns = {column["name"] for column in inspector.get_columns("user_profiles")}
    if "fuzzy_onboarding_skipped_at" in existing_columns:
        op.drop_column("user_profiles", "fuzzy_onboarding_skipped_at")
    if "fuzzy_onboarding_completed_at" in existing_columns:
        op.drop_column("user_profiles", "fuzzy_onboarding_completed_at")
    if "fuzzy_onboarding_state" in existing_columns:
        op.drop_column("user_profiles", "fuzzy_onboarding_state")
