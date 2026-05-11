"""schema review: constraints, indexes, redeem link, mission timestamps

Revision ID: c3f8a1b2d4e6
Revises: a0b1c2d3e4f5
Create Date: 2026-05-10

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c3f8a1b2d4e6"
down_revision: Union[str, Sequence[str], None] = "a0b1c2d3e4f5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


_TS_TABLES = (
    "businesses",
    "users",
    "missions",
    "redeem_tokens",
    "portfolio_items",
    "ratings",
    "transactions",
)


def upgrade() -> None:
    op.execute(
        sa.text(
            """
            DELETE FROM redeem_tokens AS a
                USING redeem_tokens AS b
            WHERE a.id > b.id AND a.token_hash = b.token_hash
            """
        )
    )
    op.create_unique_constraint(
        "uq_redeem_tokens_token_hash", "redeem_tokens", ["token_hash"]
    )

    for table in _TS_TABLES:
        op.execute(
            sa.text(
                f"UPDATE {table} SET updated_at = created_at WHERE updated_at IS NULL"
            )
        )
        op.execute(
            sa.text(f"ALTER TABLE {table} ALTER COLUMN updated_at SET DEFAULT now()")
        )

    op.add_column(
        "transactions",
        sa.Column("from_business_id", sa.UUID(), nullable=True),
    )
    op.create_foreign_key(
        "fk_transactions_from_business_id_businesses",
        "transactions",
        "businesses",
        ["from_business_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.execute(sa.text("UPDATE ratings SET score = 1 WHERE score < 1"))
    op.execute(sa.text("UPDATE ratings SET score = 5 WHERE score > 5"))
    op.create_check_constraint(
        "ck_rating_score",
        "ratings",
        "score >= 1 AND score <= 5",
    )

    op.create_check_constraint(
        "ck_user_provider_no_business",
        "users",
        "(role::text <> 'PROVIDER' OR business_id IS NULL)",
    )

    op.create_index(
        op.f("ix_missions_status"), "missions", ["status"], unique=False
    )
    op.create_index(
        op.f("ix_missions_business_id"),
        "missions",
        ["business_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_transactions_to_user_id"),
        "transactions",
        ["to_user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_transactions_business_id"),
        "transactions",
        ["business_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_redeem_tokens_status"),
        "redeem_tokens",
        ["status"],
        unique=False,
    )
    op.create_index(
        op.f("ix_redeem_tokens_provider_id"),
        "redeem_tokens",
        ["provider_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_redeem_tokens_business_id"),
        "redeem_tokens",
        ["business_id"],
        unique=False,
    )

    op.add_column(
        "redeem_tokens",
        sa.Column("transaction_id", sa.UUID(), nullable=True),
    )
    op.add_column(
        "redeem_tokens",
        sa.Column("redeemed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_redeem_tokens_transaction_id_transactions",
        "redeem_tokens",
        "transactions",
        ["transaction_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.add_column(
        "missions",
        sa.Column("accepted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "missions",
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "missions",
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "missions",
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("missions", "cancelled_at")
    op.drop_column("missions", "approved_at")
    op.drop_column("missions", "completed_at")
    op.drop_column("missions", "accepted_at")

    op.drop_constraint(
        "fk_redeem_tokens_transaction_id_transactions",
        "redeem_tokens",
        type_="foreignkey",
    )
    op.drop_column("redeem_tokens", "redeemed_at")
    op.drop_column("redeem_tokens", "transaction_id")

    op.drop_index(op.f("ix_redeem_tokens_business_id"), table_name="redeem_tokens")
    op.drop_index(op.f("ix_redeem_tokens_provider_id"), table_name="redeem_tokens")
    op.drop_index(op.f("ix_redeem_tokens_status"), table_name="redeem_tokens")
    op.drop_index(op.f("ix_transactions_business_id"), table_name="transactions")
    op.drop_index(op.f("ix_transactions_to_user_id"), table_name="transactions")
    op.drop_index(op.f("ix_missions_business_id"), table_name="missions")
    op.drop_index(op.f("ix_missions_status"), table_name="missions")

    op.drop_constraint("ck_user_provider_no_business", "users", type_="check")
    op.drop_constraint("ck_rating_score", "ratings", type_="check")

    op.drop_constraint(
        "fk_transactions_from_business_id_businesses",
        "transactions",
        type_="foreignkey",
    )
    op.drop_column("transactions", "from_business_id")

    for table in _TS_TABLES:
        op.execute(
            sa.text(f"ALTER TABLE {table} ALTER COLUMN updated_at DROP DEFAULT")
        )

    op.drop_constraint("uq_redeem_tokens_token_hash", "redeem_tokens", type_="unique")
