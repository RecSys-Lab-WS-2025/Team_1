"""add_base_xp_reward_to_routes

Revision ID: 2a349288b005
Revises: b02874b51238
Create Date: 2025-11-20 10:53:13.261406

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2a349288b005'
down_revision: Union[str, None] = 'b02874b51238'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add base_xp_reward column to routes table
    op.add_column('routes', sa.Column('base_xp_reward', sa.Integer(), server_default=sa.text('0'), nullable=False))


def downgrade() -> None:
    # Remove base_xp_reward column from routes table
    op.drop_column('routes', 'base_xp_reward')

