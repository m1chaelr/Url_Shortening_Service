"""create shortened urls table

Revision ID: bc59cc27de17
Revises: 
Create Date: 2026-06-12 14:11:49.125800

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bc59cc27de17'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "shortened_urls",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("original_url", sa.String(), nullable=False),
        sa.Column("short_code", sa.String(), nullable=False),
        sa.Column("access_count", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_shortened_urls_id"), "shortened_urls", ["id"], unique=False)
    op.create_index(op.f("ix_shortened_urls_short_code"), "shortened_urls", ["short_code"], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_shortened_urls_short_code"), table_name="shortened_urls")
    op.drop_index(op.f("ix_shortened_urls_id"), table_name="shortened_urls")
    op.drop_table("shortened_urls")
