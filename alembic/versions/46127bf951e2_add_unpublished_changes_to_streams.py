"""Add unpublished changes to streams

Revision ID: 46127bf951e2
Revises: f876822e12b2
Create Date: 2026-11-19 17:00:40.333483
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.

revision: str = "46127bf951e2"
down_revision: Union[str, Sequence[str], None] = "f876822e12b2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        "streams",
        sa.Column(
            "has_unpublished_changes",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )

    op.alter_column(
        "streams",
        "has_unpublished_changes",
        server_default=None,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_column(
        "streams",
        "has_unpublished_changes",
    )
