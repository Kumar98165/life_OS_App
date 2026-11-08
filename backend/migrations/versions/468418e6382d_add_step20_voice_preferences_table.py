"""add_step20_voice_preferences_table

Revision ID: 468418e6382d
Revises: a10de13e7227
Create Date: 2026-11-08 13:13:35.783352

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '468418e6382d'
down_revision = 'a10de13e7227'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('voice_preferences',
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('language', sa.String(length=20), nullable=False, server_default='en'),
        sa.Column('voice_name', sa.String(length=100), nullable=False, server_default='default'),
        sa.Column('speech_rate', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('speech_pitch', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('auto_play_response', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('audio_privacy_enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('confirm_actions_via_voice', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('voice_preferences', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_voice_preferences_created_at'), ['created_at'], unique=False)
        batch_op.create_index(batch_op.f('ix_voice_preferences_user_id'), ['user_id'], unique=True)


def downgrade():
    with op.batch_alter_table('voice_preferences', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_voice_preferences_user_id'))
        batch_op.drop_index(batch_op.f('ix_voice_preferences_created_at'))

    op.drop_table('voice_preferences')
