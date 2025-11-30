"""add_environment_photos_to_adoption_applications

Revision ID: ccec3edb08fa
Revises: fa50cd5b4b06
Create Date: 2025-11-13 12:09:34.102270

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ccec3edb08fa'
down_revision: Union[str, Sequence[str], None] = 'fa50cd5b4b06'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add environment_photos column to adoption_applications table
    op.add_column(
        'adoption_applications',
        sa.Column('environment_photos', sa.JSON(), nullable=True)
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Remove environment_photos column from adoption_applications table
    op.drop_column('adoption_applications', 'environment_photos')
