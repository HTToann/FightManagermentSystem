"""Add model FlightSeat and remove a field Status at model Seat

Revision ID: 23f6797ac2c7
Revises: 8968628f8285
Create Date: 2025-04-06 20:06:14.371922

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '23f6797ac2c7'
down_revision: Union[str, None] = '8968628f8285'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('flight_seat',
    sa.Column('flight_id', sa.Integer(), nullable=False),
    sa.Column('seat_id', sa.Integer(), nullable=False),
    sa.Column('status', sa.Enum('AVAILABLE', 'BOOKED', name='statusseat'), nullable=False),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.ForeignKeyConstraint(['flight_id'], ['flight.id'], ),
    sa.ForeignKeyConstraint(['seat_id'], ['seat.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_column('seat', 'status')
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('seat', sa.Column('status', mysql.ENUM('AVAILABLE', 'BOOKED'), nullable=False))
    op.drop_table('flight_seat')
    # ### end Alembic commands ###
