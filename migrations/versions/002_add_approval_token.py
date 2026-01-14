"""Add approval_token_hash column to draft_queue table.

Revision ID: 002_add_approval_token
Revises: 
Create Date: 2026-01-13

Stores SHA-256 hash of approval tokens for secure URL-based approval flow.
Tokens are hashed at rest to prevent abuse if database is compromised.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002_add_approval_token'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add approval_token_hash column."""
    op.add_column(
        'draft_queue',
        sa.Column('approval_token_hash', sa.String(), nullable=True)
    )
    op.create_index(
        'ix_draft_queue_approval_token_hash',
        'draft_queue',
        ['approval_token_hash']
    )


def downgrade() -> None:
    """Remove approval_token_hash column."""
    op.drop_index('ix_draft_queue_approval_token_hash', table_name='draft_queue')
    op.drop_column('draft_queue', 'approval_token_hash')
