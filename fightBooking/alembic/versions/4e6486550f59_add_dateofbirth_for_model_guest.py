"""Add dateOfBirth for model Guest

Revision ID: 4e6486550f59
Revises: 9c68370b5967
Create Date: 2025-04-03 09:36:09.945477

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4e6486550f59'
down_revision: Union[str, None] = '9c68370b5967'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('guest', sa.Column('date_of_birth', sa.DateTime(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('guest', 'date_of_birth')
    # ### end Alembic commands ###
