
"""Safe initial migration for Expense Tracker.

Revision ID: de97fdae0c8a
Revises:
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


# Revision identifiers
revision = "de97fdae0c8a"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:

    # ==========================================
    # EXPENSES: ADD NEW COLUMNS
    # ==========================================

    op.add_column(
        "expenses",
        sa.Column("note", sa.String(255), nullable=True)
    )

    # Initially nullable to support existing records
    op.add_column(
        "expenses",
        sa.Column("payment_method", sa.String(30), nullable=True)
    )

    op.add_column(
        "expenses",
        sa.Column("created_at", sa.DateTime(), nullable=True)
    )

    op.add_column(
        "expenses",
        sa.Column("updated_at", sa.DateTime(), nullable=True)
    )

    # ==========================================
    # BACKFILL EXISTING EXPENSE RECORDS
    # ==========================================

    op.execute(
        sa.text("""
            UPDATE expenses
            SET payment_method = 'Cash'
            WHERE payment_method IS NULL
        """)
    )

    op.execute(
        sa.text("""
            UPDATE expenses
            SET created_at = CURRENT_TIMESTAMP
            WHERE created_at IS NULL
        """)
    )

    op.execute(
        sa.text("""
            UPDATE expenses
            SET updated_at = CURRENT_TIMESTAMP
            WHERE updated_at IS NULL
        """)
    )

    # ==========================================
    # MAKE NEW COLUMNS NOT NULL
    # ==========================================

    op.alter_column(
        "expenses",
        "payment_method",
        existing_type=sa.String(30),
        nullable=False
    )

    op.alter_column(
        "expenses",
        "created_at",
        existing_type=sa.DateTime(),
        nullable=False
    )

    op.alter_column(
        "expenses",
        "updated_at",
        existing_type=sa.DateTime(),
        nullable=False
    )

    # ==========================================
    # UPDATE EXISTING EXPENSE COLUMNS
    # ==========================================

    op.alter_column(
        "expenses",
        "amount",
        existing_type=mysql.FLOAT(),
        type_=sa.Numeric(15, 2),
        existing_nullable=False
    )

    op.alter_column(
        "expenses",
        "category",
        existing_type=mysql.VARCHAR(100),
        type_=sa.String(50),
        existing_nullable=False
    )

    op.alter_column(
        "expenses",
        "expense_date",
        existing_type=sa.Date(),
        nullable=False
    )

    # ==========================================
    # UPDATE SESSIONS TABLE
    # ==========================================

    # Your checks confirmed there are no NULL values.
    op.alter_column(
        "sessions",
        "created_at",
        existing_type=sa.DateTime(),
        nullable=False
    )

    op.alter_column(
        "sessions",
        "is_revoked",
        existing_type=mysql.TINYINT(display_width=1),
        nullable=False
    )


def downgrade() -> None:

    # ==========================================
    # REVERT SESSIONS
    # ==========================================

    op.alter_column(
        "sessions",
        "is_revoked",
        existing_type=mysql.TINYINT(display_width=1),
        nullable=True
    )

    op.alter_column(
        "sessions",
        "created_at",
        existing_type=sa.DateTime(),
        nullable=True
    )

    # ==========================================
    # REVERT EXPENSES
    # ==========================================

    op.alter_column(
        "expenses",
        "expense_date",
        existing_type=sa.Date(),
        nullable=True
    )

    op.alter_column(
        "expenses",
        "category",
        existing_type=sa.String(50),
        type_=mysql.VARCHAR(100),
        existing_nullable=False
    )

    op.alter_column(
        "expenses",
        "amount",
        existing_type=sa.Numeric(15, 2),
        type_=mysql.FLOAT(),
        existing_nullable=False
    )

    # Remove columns added by this migration
    op.drop_column("expenses", "updated_at")
    op.drop_column("expenses", "created_at")
    op.drop_column("expenses", "payment_method")
    op.drop_column("expenses", "note")
