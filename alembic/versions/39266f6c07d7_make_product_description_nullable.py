"""make product description nullable

Revision ID: 39266f6c07d7
Revises: 720238967b38
Create Date: 2025-11-25 22:36:23.014795

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '39266f6c07d7'
down_revision: Union[str, Sequence[str], None] = '720238967b38'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
