from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

SCHEMA = "notifications"


def upgrade() -> None:
    op.create_table(
        "notification_settings",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("push_enabled", sa.Boolean(), nullable=False),
        sa.Column("email_enabled", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("user_id", name=op.f("pk_notification_settings")),
        schema=SCHEMA,
    )
    op.create_table(
        "device_tokens",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("platform", sa.Text(), nullable=False),
        sa.Column("token", sa.Text(), nullable=False),
        sa.CheckConstraint("platform = 'android'", name=op.f("ck_device_tokens_android_platform")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_device_tokens")),
        sa.UniqueConstraint("token", name=op.f("uq_device_tokens_token")),
        schema=SCHEMA,
    )
    op.create_index(op.f("ix_device_tokens_user_id"), "device_tokens", ["user_id"], schema=SCHEMA)


def downgrade() -> None:
    op.drop_table("device_tokens", schema=SCHEMA)
    op.drop_table("notification_settings", schema=SCHEMA)
