"""Add unit and unit_quantity to products (manual)

Revision ID: b80460af1269
Revises: c64ee8e59f68
Create Date: 2026-10-10 17:08:14.442519

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b80460af1269'
down_revision = 'c64ee8e59f68'
branch_labels = None
depends_on = None


def upgrade():
    # Columns were added manually to work around SQLite limitations
    # Migration is for documentation only
    pass


def downgrade():
    # Manual removal would be required
    pass
