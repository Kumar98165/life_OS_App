"""remove voice_preferences permanently

Revision ID: 3a2b1c0d9e8f
Revises: 9f8e7d6c5b4a
Create Date: 2026-11-09 12:13:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3a2b1c0d9e8f'
down_revision = '9f8e7d6c5b4a'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("DROP TABLE IF EXISTS voice_preferences CASCADE")


def downgrade():
    op.create_table(
        'voice_preferences',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('language', sa.String(length=10), nullable=False, server_default='en'),
        sa.Column('voice_name', sa.String(length=50), nullable=False, server_default='default'),
        sa.Column('speech_rate', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('speech_pitch', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('auto_play_response', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('audio_privacy_enabled', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('confirm_actions_via_voice', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
