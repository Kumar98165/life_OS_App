"""add_goal_priority_and_milestone_description

Revision ID: e3bb8a0112fa
Revises: daaa4c2c151c
Create Date: 2026-11-07 22:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e3bb8a0112fa'
down_revision = 'daaa4c2c151c'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('goals', schema=None) as batch_op:
        batch_op.add_column(sa.Column('priority', sa.String(length=20), server_default='medium', nullable=False))
        batch_op.create_index('ix_goals_user_priority', ['user_id', 'priority'], unique=False)

    with op.batch_alter_table('goal_milestones', schema=None) as batch_op:
        batch_op.add_column(sa.Column('description', sa.Text(), nullable=True))


def downgrade():
    with op.batch_alter_table('goal_milestones', schema=None) as batch_op:
        batch_op.drop_column('description')

    with op.batch_alter_table('goals', schema=None) as batch_op:
        batch_op.drop_index('ix_goals_user_priority')
        batch_op.drop_column('priority')

