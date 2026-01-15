"""Add performance tracking tables and columns.

Revision ID: 003_add_performance_tracking
Revises: 002_add_approval_token
Create Date: 2026-01-14

Adds performance_history table to track draft outcomes and engagement metrics.
Extends draft_queue with comment_id, published_at, and engagement_checked fields.
Enables historical learning system (Phase 2 & 3 of quality scoring).
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '003_add_performance_tracking'
down_revision = '002_add_approval_token'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add performance_history table and extend draft_queue."""

    # Create performance_history table
    op.create_table(
        'performance_history',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('draft_id', sa.String(50), nullable=False),
        sa.Column('subreddit', sa.String(50), nullable=False),
        sa.Column('candidate_type', sa.String(20), nullable=False),
        sa.Column('quality_score', sa.Float(), nullable=True),
        sa.Column('outcome', sa.String(20), nullable=False),
        sa.Column('engagement_score', sa.Float(), nullable=True),
        sa.Column('upvotes_24h', sa.Integer(), nullable=True),
        sa.Column('replies_24h', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('outcome_at', sa.DateTime(), nullable=True)
    )

    # Create indexes on performance_history
    op.create_index(
        'ix_performance_history_draft_id',
        'performance_history',
        ['draft_id']
    )
    op.create_index(
        'ix_performance_history_subreddit',
        'performance_history',
        ['subreddit']
    )
    op.create_index(
        'ix_performance_history_created_at',
        'performance_history',
        ['created_at']
    )
    # Composite index for aggregation queries (subreddit performance over time)
    op.create_index(
        'ix_performance_history_subreddit_created',
        'performance_history',
        ['subreddit', 'created_at']
    )

    # Extend draft_queue table with new columns
    op.add_column(
        'draft_queue',
        sa.Column('comment_id', sa.String(50), nullable=True)
    )
    op.add_column(
        'draft_queue',
        sa.Column('published_at', sa.DateTime(), nullable=True)
    )
    op.add_column(
        'draft_queue',
        sa.Column('engagement_checked', sa.Boolean(), nullable=False, server_default='0')
    )
    op.add_column(
        'draft_queue',
        sa.Column('candidate_type', sa.String(20), nullable=True)
    )
    op.add_column(
        'draft_queue',
        sa.Column('quality_score', sa.Float(), nullable=True)
    )

    # Create index for engagement check queries
    op.create_index(
        'ix_draft_queue_engagement_check',
        'draft_queue',
        ['status', 'engagement_checked', 'published_at']
    )


def downgrade() -> None:
    """Remove performance tracking tables and columns."""

    # Drop draft_queue index and columns
    op.drop_index('ix_draft_queue_engagement_check', table_name='draft_queue')
    op.drop_column('draft_queue', 'quality_score')
    op.drop_column('draft_queue', 'candidate_type')
    op.drop_column('draft_queue', 'engagement_checked')
    op.drop_column('draft_queue', 'published_at')
    op.drop_column('draft_queue', 'comment_id')

    # Drop performance_history indexes and table
    op.drop_index('ix_performance_history_subreddit_created', table_name='performance_history')
    op.drop_index('ix_performance_history_created_at', table_name='performance_history')
    op.drop_index('ix_performance_history_subreddit', table_name='performance_history')
    op.drop_index('ix_performance_history_draft_id', table_name='performance_history')
    op.drop_table('performance_history')
