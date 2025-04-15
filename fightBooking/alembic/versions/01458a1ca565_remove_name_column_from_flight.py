"""remove name column from flight

Revision ID: 01458a1ca565
Revises:
Create Date: 2025-03-15 22:29:09.371199

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "01458a1ca565"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Lệnh xóa cột 'name' trong bảng 'flight'
    op.drop_column("flight", "name")


def downgrade() -> None:
    # Nếu muốn rollback, thêm lại cột 'name'
    op.add_column("flight", sa.Column("name", sa.String(255), nullable=False))
