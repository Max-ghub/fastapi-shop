"""init

Revision ID: ec90f06d423d
Revises:
Create Date: 2025-11-21 08:40:40.705210

"""

from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = 'ec90f06d423d'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
