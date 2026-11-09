"""add focus mode and advanced calendar fields

Revision ID: 8e9f0a1b2c3d
Revises: 7d8e9f0a1b2c
Create Date: 2026-11-09 13:25:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8e9f0a1b2c3d'
down_revision = '7d8e9f0a1b2c'
branch_labels = None
depends_on = None


def upgrade():
    # 1. Update planner_blocks with recurrence, reminder, timezone
    with op.batch_alter_table('planner_blocks', schema=None) as batch_op:
        batch_op.add_column(sa.Column('recurrence_rule', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('reminder_minutes_before', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('timezone', sa.String(length=50), nullable=True, server_default='UTC'))

    # 2. Create focus_goals table
    op.create_table(
        'focus_goals',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('daily_target_minutes', sa.Integer(), nullable=False, server_default='120'),
        sa.Column('weekly_target_minutes', sa.Integer(), nullable=False, server_default='600'),
        sa.Column('preferred_technique', sa.String(length=30), nullable=False, server_default='25/5'),
        sa.Column('custom_work_minutes', sa.Integer(), nullable=False, server_default='25'),
        sa.Column('custom_break_minutes', sa.Integer(), nullable=False, server_default='5'),
        sa.Column('custom_long_break_minutes', sa.Integer(), nullable=False, server_default='15'),
        sa.Column('long_break_interval', sa.Integer(), nullable=False, server_default='4'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    with op.batch_alter_table('focus_goals', schema=None) as batch_op:
        batch_op.create_index('ix_focus_goals_user_id', ['user_id'], unique=True)

    # 3. Create focus_sessions table
    op.create_table(
        'focus_sessions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('task_id', sa.String(length=36), nullable=True),
        sa.Column('planner_block_id', sa.String(length=36), nullable=True),
        sa.Column('title', sa.String(length=255), nullable=False, server_default='Focus Session'),
        sa.Column('session_type', sa.String(length=30), nullable=False, server_default='work'),
        sa.Column('target_duration_minutes', sa.Integer(), nullable=False, server_default='25'),
        sa.Column('actual_duration_seconds', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='active'),
        sa.Column('start_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('paused_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['planner_block_id'], ['planner_blocks.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('focus_sessions', schema=None) as batch_op:
        batch_op.create_index('ix_focus_sessions_user_id', ['user_id'], unique=False)
        batch_op.create_index('ix_focus_sessions_task_id', ['task_id'], unique=False)
        batch_op.create_index('ix_focus_sessions_planner_block_id', ['planner_block_id'], unique=False)
        batch_op.create_index('ix_focus_sessions_start_time', ['start_time'], unique=False)
        batch_op.create_index('ix_focus_sessions_status', ['status'], unique=False)

    # 4. Create focus_distractions table
    op.create_table(
        'focus_distractions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('focus_session_id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('distraction_type', sa.String(length=50), nullable=False, server_default='internal'),
        sa.Column('description', sa.String(length=255), nullable=False),
        sa.Column('logged_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['focus_session_id'], ['focus_sessions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('focus_distractions', schema=None) as batch_op:
        batch_op.create_index('ix_focus_distractions_focus_session_id', ['focus_session_id'], unique=False)
        batch_op.create_index('ix_focus_distractions_user_id', ['user_id'], unique=False)


def downgrade():
    op.drop_table('focus_distractions')
    op.drop_table('focus_sessions')
    op.drop_table('focus_goals')
    with op.batch_alter_table('planner_blocks', schema=None) as batch_op:
        batch_op.drop_column('timezone')
        batch_op.drop_column('reminder_minutes_before')
        batch_op.drop_column('recurrence_rule')

