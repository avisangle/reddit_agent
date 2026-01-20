"""Add admin tables for authentication and audit logging.

Revision ID: 005_add_admin_tables
Revises: 004_add_candidate_type_cooldown
Create Date: 2026-01-15

Creates AdminAuditLog and LoginAttempt tables for Phase 1: Admin Backend.
Enables password-protected admin UI with session-based authentication and
comprehensive audit logging of all admin actions.
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '005_add_admin_tables'
down_revision = '004_add_candidate_type_cooldown'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create admin_audit_log and login_attempts tables."""

    # Create admin_audit_log table
    op.create_table(
        'admin_audit_log',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('ip_address', sa.String(50), nullable=False),
        sa.Column('user_agent', sa.String(500), nullable=True),
        sa.Column('details', sa.Text(), nullable=True),
        sa.Column('success', sa.Boolean(), nullable=False, default=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for admin_audit_log
    op.create_index('ix_admin_audit_log_timestamp', 'admin_audit_log', ['timestamp'])
    op.create_index('ix_admin_audit_log_action', 'admin_audit_log', ['action'])
    op.create_index('ix_admin_audit_log_ip_address', 'admin_audit_log', ['ip_address'])

    # Create login_attempts table
    op.create_table(
        'login_attempts',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('ip_address', sa.String(50), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('success', sa.Boolean(), nullable=False, default=False),
        sa.Column('user_agent', sa.String(500), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for login_attempts (for rate limiting queries)
    op.create_index('ix_login_attempts_ip_address', 'login_attempts', ['ip_address'])
    op.create_index('ix_login_attempts_timestamp', 'login_attempts', ['timestamp'])


def downgrade() -> None:
    """Drop admin_audit_log and login_attempts tables."""

    # Drop login_attempts table and indexes
    op.drop_index('ix_login_attempts_timestamp', table_name='login_attempts')
    op.drop_index('ix_login_attempts_ip_address', table_name='login_attempts')
    op.drop_table('login_attempts')

    # Drop admin_audit_log table and indexes
    op.drop_index('ix_admin_audit_log_ip_address', table_name='admin_audit_log')
    op.drop_index('ix_admin_audit_log_action', table_name='admin_audit_log')
    op.drop_index('ix_admin_audit_log_timestamp', table_name='admin_audit_log')
    op.drop_table('admin_audit_log')
