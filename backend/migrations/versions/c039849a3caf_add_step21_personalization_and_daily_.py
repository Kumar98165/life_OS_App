"""add_step21_personalization_and_daily_routine_tables

Revision ID: c039849a3caf
Revises: 468418e6382d
Create Date: 2026-11-09 00:58:29.203525

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'c039849a3caf'
down_revision = '468418e6382d'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('daily_routines',
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('wake_time', sa.String(length=10), nullable=False, server_default='07:00'),
        sa.Column('sleep_time', sa.String(length=10), nullable=False, server_default='23:00'),
        sa.Column('work_start', sa.String(length=10), nullable=False, server_default='09:00'),
        sa.Column('work_end', sa.String(length=10), nullable=False, server_default='17:00'),
        sa.Column('work_days', sa.JSON(), nullable=False),
        sa.Column('focus_block_duration_minutes', sa.Integer(), nullable=False, server_default='50'),
        sa.Column('break_duration_minutes', sa.Integer(), nullable=False, server_default='10'),
        sa.Column('lunch_start', sa.String(length=10), nullable=False, server_default='12:30'),
        sa.Column('lunch_duration_minutes', sa.Integer(), nullable=False, server_default='60'),
        sa.Column('morning_routine_enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('evening_routine_enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('preferred_planning_time', sa.String(length=10), nullable=False, server_default='08:30'),
        sa.Column('routine_reminders_enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('daily_routines', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_daily_routines_created_at'), ['created_at'], unique=False)
        batch_op.create_index(batch_op.f('ix_daily_routines_user_id'), ['user_id'], unique=True)

    op.create_table('user_personalizations',
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('preferred_name', sa.String(length=100), nullable=True),
        sa.Column('preferred_language', sa.String(length=20), nullable=False, server_default='en'),
        sa.Column('timezone', sa.String(length=50), nullable=False, server_default='UTC'),
        sa.Column('date_format', sa.String(length=20), nullable=False, server_default='YYYY-MM-DD'),
        sa.Column('time_format', sa.String(length=10), nullable=False, server_default='24h'),
        sa.Column('week_start_day', sa.String(length=10), nullable=False, server_default='monday'),
        sa.Column('productivity_style', sa.String(length=30), nullable=False, server_default='structured'),
        sa.Column('task_priority_strategy', sa.String(length=30), nullable=False, server_default='eisenhower'),
        sa.Column('ai_response_style', sa.String(length=30), nullable=False, server_default='concise'),
        sa.Column('ai_response_length', sa.String(length=20), nullable=False, server_default='medium'),
        sa.Column('dashboard_widgets', sa.JSON(), nullable=False),
        sa.Column('dashboard_density', sa.String(length=20), nullable=False, server_default='comfortable'),
        sa.Column('personalization_enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('user_personalizations', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_user_personalizations_created_at'), ['created_at'], unique=False)
        batch_op.create_index(batch_op.f('ix_user_personalizations_user_id'), ['user_id'], unique=True)


def downgrade():
    with op.batch_alter_table('user_personalizations', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_user_personalizations_user_id'))
        batch_op.drop_index(batch_op.f('ix_user_personalizations_created_at'))

    op.drop_table('user_personalizations')

    with op.batch_alter_table('daily_routines', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_daily_routines_user_id'))
        batch_op.drop_index(batch_op.f('ix_daily_routines_created_at'))

    op.drop_table('daily_routines')
