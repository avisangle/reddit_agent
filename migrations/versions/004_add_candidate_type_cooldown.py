"""Add candidate_type to replied_items for separate cooldowns.

Revision ID: 004_add_candidate_type_cooldown
Revises: 003_add_performance_tracking
Create Date: 2026-01-15

Adds candidate_type column to replied_items table to enable separate cooldown
periods for inbox replies (6h) vs rising content (24h). Part of Phase A: Inbox
Priority System.
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '004_add_candidate_type_cooldown'
down_revision = '003_add_performance_tracking'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add candidate_type column to replied_items."""

    # Add candidate_type column (nullable to support existing rows)
    op.add_column(
        'replied_items',
        sa.Column('candidate_type', sa.String(20), nullable=True)
    )

    # Create index for efficient filtering by candidate type
    op.create_index(
        'ix_replied_items_candidate_type',
        'replied_items',
        ['candidate_type']
    )


def downgrade() -> None:
    """Remove candidate_type column from replied_items."""

    # Drop index and column
    op.drop_index('ix_replied_items_candidate_type', table_name='replied_items')
    op.drop_column('replied_items', 'candidate_type')
