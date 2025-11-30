"""add home visit and decision fields

Revision ID: f4e8c9d3a2b1
Revises: ccec3edb08fa
Create Date: 2025-11-13 13:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'f4e8c9d3a2b1'
down_revision = 'ccec3edb08fa'
branch_labels = None
depends_on = None


def upgrade():
    # Add home visit and decision fields to adoption_applications
    op.add_column('adoption_applications', sa.Column('home_visit_date', sa.Date(), nullable=True))
    op.add_column('adoption_applications', sa.Column('home_visit_notes', sa.Text(), nullable=True))
    op.add_column('adoption_applications', sa.Column('home_visit_document', sa.String(500), nullable=True))
    op.add_column('adoption_applications', sa.Column('final_decision_notes', sa.Text(), nullable=True))


def downgrade():
    # Remove the added columns
    op.drop_column('adoption_applications', 'final_decision_notes')
    op.drop_column('adoption_applications', 'home_visit_document')
    op.drop_column('adoption_applications', 'home_visit_notes')
    op.drop_column('adoption_applications', 'home_visit_date')
