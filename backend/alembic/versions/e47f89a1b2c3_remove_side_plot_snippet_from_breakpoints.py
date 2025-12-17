"""remove_side_plot_snippet_from_breakpoints

Revision ID: e47f89a1b2c3
Revises: d36f54e832d2
Create Date: 2025-12-02 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e47f89a1b2c3'
down_revision: Union[str, None] = 'd36f54e832d2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Remove side_plot_snippet column from breakpoints table
    op.drop_column('breakpoints', 'side_plot_snippet')


def downgrade() -> None:
    # Add back side_plot_snippet column (nullable Text)
    op.add_column('breakpoints', sa.Column('side_plot_snippet', sa.Text(), nullable=True))

