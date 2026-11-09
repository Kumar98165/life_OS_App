"""add_step7_ai_dataset_management_tables_and_columns

Revision ID: b7e3d1a89f24
Revises: c039849a3caf
Create Date: 2026-11-09 06:50:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b7e3d1a89f24'
down_revision = 'c039849a3caf'
branch_labels = None
depends_on = None


def upgrade():
    # 1. Create ai_dataset_versions table
    op.create_table(
        'ai_dataset_versions',
        sa.Column('version_name', sa.String(length=50), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('sample_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('dataset_type', sa.String(length=20), nullable=False, server_default='sft'),
        sa.Column('manifest_hash', sa.String(length=64), nullable=False),
        sa.Column('included_categories', sa.JSON(), nullable=True),
        sa.Column('validation_summary', sa.JSON(), nullable=True),
        sa.Column('is_exported', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('exported_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', sa.String(length=36), nullable=True),
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('ai_dataset_versions', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_ai_dataset_versions_created_at'), ['created_at'], unique=False)
        batch_op.create_index(batch_op.f('ix_ai_dataset_versions_version_name'), ['version_name'], unique=True)

    # 2. Add columns to ai_training_samples
    with op.batch_alter_table('ai_training_samples', schema=None) as batch_op:
        batch_op.add_column(sa.Column('category', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('sanitization_status', sa.String(length=20), nullable=False, server_default='pending'))
        batch_op.add_column(sa.Column('validation_status', sa.String(length=20), nullable=False, server_default='pending'))
        batch_op.add_column(sa.Column('validation_notes', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('dataset_version_id', sa.String(length=36), nullable=True))
        batch_op.create_foreign_key(
            'fk_ai_training_samples_dataset_version_id',
            'ai_dataset_versions',
            ['dataset_version_id'],
            ['id'],
            ondelete='SET NULL'
        )
        batch_op.create_index(
            'ix_ai_training_samples_val_san',
            ['validation_status', 'sanitization_status'],
            unique=False
        )
        batch_op.create_index(
            batch_op.f('ix_ai_training_samples_dataset_version_id'),
            ['dataset_version_id'],
            unique=False
        )


def downgrade():
    with op.batch_alter_table('ai_training_samples', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_ai_training_samples_dataset_version_id'))
        batch_op.drop_index('ix_ai_training_samples_val_san')
        batch_op.drop_constraint('fk_ai_training_samples_dataset_version_id', type_='foreignkey')
        batch_op.drop_column('dataset_version_id')
        batch_op.drop_column('validation_notes')
        batch_op.drop_column('validation_status')
        batch_op.drop_column('sanitization_status')
        batch_op.drop_column('category')

    with op.batch_alter_table('ai_dataset_versions', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_ai_dataset_versions_version_name'))
        batch_op.drop_index(batch_op.f('ix_ai_dataset_versions_created_at'))

    op.drop_table('ai_dataset_versions')
