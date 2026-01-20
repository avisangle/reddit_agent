"""Add approve_url and reject_url columns to draft_queue.

Revision ID: 006
Revises: 005_add_admin_tables
Create Date: 2025-01-20

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '006_add_approval_urls'
down_revision = '005_add_admin_tables'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('draft_queue', sa.Column('approve_url', sa.String(500), nullable=True))
    op.add_column('draft_queue', sa.Column('reject_url', sa.String(500), nullable=True))


def downgrade() -> None:
    op.drop_column('draft_queue', 'approve_url')
    op.drop_column('draft_queue', 'reject_url')
