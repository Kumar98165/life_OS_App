"""remove ai tables permanently

Revision ID: 9f8e7d6c5b4a
Revises: 3f5aa89ed9bf
Create Date: 2026-11-09 10:15:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9f8e7d6c5b4a'
down_revision = '3f5aa89ed9bf'
branch_labels = None
depends_on = None


def upgrade():
    # Drop all 12 confirmed AI-only tables safely
    tables = [
        'ai_model_rollback_logs',
        'ai_model_versions',
        'ai_evaluation_metrics',
        'ai_evaluation_runs',
        'ai_training_jobs',
        'ai_training_samples',
        'ai_dataset_versions',
        'ai_feedback',
        'ai_memories',
        'ai_messages',
        'ai_prompt_versions',
        'ai_conversations'
    ]
    for table_name in tables:
        op.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE;")


def downgrade():
    # Irreversible permanent removal: data backed up in backend/backups/
    pass
