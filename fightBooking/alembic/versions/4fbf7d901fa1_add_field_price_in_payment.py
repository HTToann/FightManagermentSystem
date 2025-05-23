"""Add field price in Payment

Revision ID: 4fbf7d901fa1
Revises: f21be7bc98b2
Create Date: 2025-04-02 21:25:18.478874

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4fbf7d901fa1'
down_revision: Union[str, None] = 'f21be7bc98b2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('payment', sa.Column('price', sa.Float(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('payment', 'price')
    # ### end Alembic commands ###
