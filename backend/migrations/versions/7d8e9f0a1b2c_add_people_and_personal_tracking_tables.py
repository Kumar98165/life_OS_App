"""add people and personal tracking modules tables

Revision ID: 7d8e9f0a1b2c
Revises: 5c6d7e8f9a0b
Create Date: 2026-11-09 12:51:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7d8e9f0a1b2c'
down_revision = '5c6d7e8f9a0b'
branch_labels = None
depends_on = None


def upgrade():
    # 1. Assigned Tasks
    op.create_table(
        'assigned_tasks',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('contact_id', sa.String(length=36), nullable=True),
        sa.Column('person_name', sa.String(length=120), nullable=False),
        sa.Column('person_contact', sa.String(length=100), nullable=True),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('assignment_date', sa.Date(), nullable=False),
        sa.Column('expected_completion_date', sa.Date(), nullable=True),
        sa.Column('actual_completion_date', sa.Date(), nullable=True),
        sa.Column('priority', sa.String(length=20), nullable=False, server_default='medium'),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='assigned'),
        sa.Column('attachment_url', sa.String(length=1000), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['contact_id'], ['contacts.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('assigned_tasks', schema=None) as batch_op:
        batch_op.create_index('ix_assigned_tasks_user_id', ['user_id'], unique=False)
        batch_op.create_index('ix_assigned_tasks_contact_id', ['contact_id'], unique=False)
        batch_op.create_index('ix_assigned_tasks_person_name', ['person_name'], unique=False)
        batch_op.create_index('ix_assigned_tasks_status', ['status'], unique=False)
        batch_op.create_index('ix_assigned_tasks_expected_completion_date', ['expected_completion_date'], unique=False)

    # 2. Task Follow-ups
    op.create_table(
        'task_follow_ups',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('task_id', sa.String(length=36), nullable=False),
        sa.Column('note', sa.Text(), nullable=False),
        sa.Column('follow_up_date', sa.Date(), nullable=False),
        sa.Column('reminder_date', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['task_id'], ['assigned_tasks.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('task_follow_ups', schema=None) as batch_op:
        batch_op.create_index('ix_task_follow_ups_task_id', ['task_id'], unique=False)

    # 3. Money Transactions
    op.create_table(
        'money_transactions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('contact_id', sa.String(length=36), nullable=True),
        sa.Column('person_name', sa.String(length=120), nullable=False),
        sa.Column('person_contact', sa.String(length=100), nullable=True),
        sa.Column('transaction_type', sa.String(length=20), nullable=False),
        sa.Column('amount', sa.Numeric(12, 2), nullable=False),
        sa.Column('amount_repaid', sa.Numeric(12, 2), nullable=False, server_default='0.0'),
        sa.Column('currency', sa.String(length=10), nullable=False, server_default='INR'),
        sa.Column('transaction_date', sa.Date(), nullable=False),
        sa.Column('expected_return_date', sa.Date(), nullable=True),
        sa.Column('payment_method', sa.String(length=50), nullable=False, server_default='UPI'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('proof_url', sa.String(length=1000), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='pending'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['contact_id'], ['contacts.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('money_transactions', schema=None) as batch_op:
        batch_op.create_index('ix_money_transactions_user_id', ['user_id'], unique=False)
        batch_op.create_index('ix_money_transactions_contact_id', ['contact_id'], unique=False)
        batch_op.create_index('ix_money_transactions_person_name', ['person_name'], unique=False)
        batch_op.create_index('ix_money_transactions_type', ['transaction_type'], unique=False)
        batch_op.create_index('ix_money_transactions_status', ['status'], unique=False)
        batch_op.create_index('ix_money_transactions_expected_return_date', ['expected_return_date'], unique=False)

    # 4. Money Repayments
    op.create_table(
        'money_repayments',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('transaction_id', sa.String(length=36), nullable=False),
        sa.Column('amount', sa.Numeric(12, 2), nullable=False),
        sa.Column('payment_date', sa.Date(), nullable=False),
        sa.Column('payment_method', sa.String(length=50), nullable=False, server_default='UPI'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('proof_url', sa.String(length=1000), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['transaction_id'], ['money_transactions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('money_repayments', schema=None) as batch_op:
        batch_op.create_index('ix_money_repayments_transaction_id', ['transaction_id'], unique=False)

    # 5. Personal Items
    op.create_table(
        'personal_items',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=150), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False, server_default='other'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('initial_condition', sa.String(length=50), nullable=False, server_default='good'),
        sa.Column('photo_url', sa.String(length=1000), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='available'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('personal_items', schema=None) as batch_op:
        batch_op.create_index('ix_personal_items_user_id', ['user_id'], unique=False)
        batch_op.create_index('ix_personal_items_name', ['name'], unique=False)
        batch_op.create_index('ix_personal_items_status', ['status'], unique=False)

    # 6. Item Lending Records
    op.create_table(
        'item_lending_records',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('item_id', sa.String(length=36), nullable=False),
        sa.Column('contact_id', sa.String(length=36), nullable=True),
        sa.Column('person_name', sa.String(length=120), nullable=False),
        sa.Column('person_contact', sa.String(length=100), nullable=True),
        sa.Column('given_date', sa.Date(), nullable=False),
        sa.Column('expected_return_date', sa.Date(), nullable=True),
        sa.Column('actual_return_date', sa.Date(), nullable=True),
        sa.Column('condition_on_return', sa.String(length=50), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['item_id'], ['personal_items.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['contact_id'], ['contacts.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('item_lending_records', schema=None) as batch_op:
        batch_op.create_index('ix_item_lending_records_item_id', ['item_id'], unique=False)
        batch_op.create_index('ix_item_lending_records_contact_id', ['contact_id'], unique=False)
        batch_op.create_index('ix_item_lending_records_person_name', ['person_name'], unique=False)
        batch_op.create_index('ix_item_lending_records_expected_return_date', ['expected_return_date'], unique=False)

    # 7. Person Activities
    op.create_table(
        'person_activities',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('contact_id', sa.String(length=36), nullable=True),
        sa.Column('person_name', sa.String(length=120), nullable=False),
        sa.Column('activity_type', sa.String(length=50), nullable=False),
        sa.Column('summary', sa.String(length=255), nullable=False),
        sa.Column('details', sa.Text(), nullable=True),
        sa.Column('amount', sa.Numeric(12, 2), nullable=True),
        sa.Column('reference_id', sa.String(length=36), nullable=True),
        sa.Column('activity_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['contact_id'], ['contacts.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('person_activities', schema=None) as batch_op:
        batch_op.create_index('ix_person_activities_user_id', ['user_id'], unique=False)
        batch_op.create_index('ix_person_activities_contact_id', ['contact_id'], unique=False)
        batch_op.create_index('ix_person_activities_person_name', ['person_name'], unique=False)
        batch_op.create_index('ix_person_activities_activity_type', ['activity_type'], unique=False)
        batch_op.create_index('ix_person_activities_activity_date', ['activity_date'], unique=False)


def downgrade():
    op.drop_table('person_activities')
    op.drop_table('item_lending_records')
    op.drop_table('personal_items')
    op.drop_table('money_repayments')
    op.drop_table('money_transactions')
    op.drop_table('task_follow_ups')
    op.drop_table('assigned_tasks')
