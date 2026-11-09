"""add complete productivity extensions tables

Revision ID: 5c6d7e8f9a0b
Revises: 3a2b1c0d9e8f
Create Date: 2026-11-09 12:25:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5c6d7e8f9a0b'
down_revision = '3a2b1c0d9e8f'
branch_labels = None
depends_on = None


def upgrade():
    # 1. Note Folders
    op.create_table(
        'note_folders',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('color_hex', sa.String(length=10), nullable=False, server_default='#6C63FF'),
        sa.Column('icon', sa.String(length=50), nullable=False, server_default='folder-outline'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'name', name='uq_note_folder_user_name')
    )
    with op.batch_alter_table('note_folders', schema=None) as batch_op:
        batch_op.create_index('ix_note_folders_user_id', ['user_id'], unique=False)

    # 2. Add folder_id to notes
    with op.batch_alter_table('notes', schema=None) as batch_op:
        batch_op.add_column(sa.Column('folder_id', sa.String(length=36), nullable=True))
        batch_op.create_foreign_key('fk_notes_folder_id', 'note_folders', ['folder_id'], ['id'], ondelete='SET NULL')
        batch_op.create_index('ix_notes_folder_id', ['folder_id'], unique=False)

    # 3. Note Attachments
    op.create_table(
        'note_attachments',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('note_id', sa.String(length=36), nullable=False),
        sa.Column('file_name', sa.String(length=255), nullable=False),
        sa.Column('file_type', sa.String(length=50), nullable=False),
        sa.Column('file_size_bytes', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('file_url', sa.String(length=1000), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['note_id'], ['notes.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('note_attachments', schema=None) as batch_op:
        batch_op.create_index('ix_note_attachments_note_id', ['note_id'], unique=False)

    # 4. Contacts
    op.create_table(
        'contacts',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=120), nullable=False),
        sa.Column('relationship_type', sa.String(length=50), nullable=False, server_default='friend'),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('phone', sa.String(length=50), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('company', sa.String(length=100), nullable=True),
        sa.Column('job_title', sa.String(length=100), nullable=True),
        sa.Column('birthday', sa.Date(), nullable=True),
        sa.Column('anniversary', sa.Date(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('is_favorite', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('contacts', schema=None) as batch_op:
        batch_op.create_index('ix_contacts_user_id', ['user_id'], unique=False)
        batch_op.create_index('ix_contacts_name', ['name'], unique=False)

    # 5. Contact Interactions
    op.create_table(
        'contact_interactions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('contact_id', sa.String(length=36), nullable=False),
        sa.Column('interaction_type', sa.String(length=50), nullable=False, server_default='call'),
        sa.Column('summary', sa.String(length=255), nullable=False),
        sa.Column('details', sa.Text(), nullable=True),
        sa.Column('interaction_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('follow_up_date', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['contact_id'], ['contacts.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('contact_interactions', schema=None) as batch_op:
        batch_op.create_index('ix_contact_interactions_contact_id', ['contact_id'], unique=False)

    # 6. Subscriptions
    op.create_table(
        'subscriptions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=120), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False, server_default='entertainment'),
        sa.Column('amount', sa.Numeric(12, 2), nullable=False),
        sa.Column('currency', sa.String(length=10), nullable=False, server_default='USD'),
        sa.Column('billing_cycle', sa.String(length=20), nullable=False, server_default='monthly'),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='active'),
        sa.Column('renewal_date', sa.Date(), nullable=False),
        sa.Column('payment_method', sa.String(length=50), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('auto_renew', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('subscriptions', schema=None) as batch_op:
        batch_op.create_index('ix_subscriptions_user_id', ['user_id'], unique=False)
        batch_op.create_index('ix_subscriptions_renewal_date', ['renewal_date'], unique=False)

    # 7. Learning Goals
    op.create_table(
        'learning_goals',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('title', sa.String(length=150), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False, server_default='technology'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('target_hours', sa.Integer(), nullable=False, server_default='50'),
        sa.Column('current_hours', sa.Numeric(8, 2), nullable=False, server_default='0.0'),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='in_progress'),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('target_completion_date', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('learning_goals', schema=None) as batch_op:
        batch_op.create_index('ix_learning_goals_user_id', ['user_id'], unique=False)

    # 8. Study Sessions
    op.create_table(
        'study_sessions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('goal_id', sa.String(length=36), nullable=False),
        sa.Column('duration_minutes', sa.Integer(), nullable=False),
        sa.Column('topics_covered', sa.String(length=255), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('session_date', sa.Date(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['goal_id'], ['learning_goals.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('study_sessions', schema=None) as batch_op:
        batch_op.create_index('ix_study_sessions_goal_id', ['goal_id'], unique=False)

    # 9. Trips
    op.create_table(
        'trips',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('destination', sa.String(length=150), nullable=False),
        sa.Column('title', sa.String(length=150), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('budget', sa.Numeric(12, 2), nullable=False, server_default='0.0'),
        sa.Column('currency', sa.String(length=10), nullable=False, server_default='USD'),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='planned'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('trips', schema=None) as batch_op:
        batch_op.create_index('ix_trips_user_id', ['user_id'], unique=False)
        batch_op.create_index('ix_trips_start_date', ['start_date'], unique=False)

    # 10. Trip Itinerary Items
    op.create_table(
        'trip_itinerary_items',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('trip_id', sa.String(length=36), nullable=False),
        sa.Column('activity_date', sa.Date(), nullable=False),
        sa.Column('activity_time', sa.String(length=10), nullable=True),
        sa.Column('title', sa.String(length=150), nullable=False),
        sa.Column('location', sa.String(length=200), nullable=True),
        sa.Column('booking_reference', sa.String(length=100), nullable=True),
        sa.Column('estimated_cost', sa.Numeric(10, 2), nullable=False, server_default='0.0'),
        sa.Column('is_completed', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['trip_id'], ['trips.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('trip_itinerary_items', schema=None) as batch_op:
        batch_op.create_index('ix_trip_itinerary_items_trip_id', ['trip_id'], unique=False)

    # 11. Trip Packing Items
    op.create_table(
        'trip_packing_items',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('trip_id', sa.String(length=36), nullable=False),
        sa.Column('item_name', sa.String(length=100), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False, server_default='essentials'),
        sa.Column('is_packed', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('quantity', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['trip_id'], ['trips.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('trip_packing_items', schema=None) as batch_op:
        batch_op.create_index('ix_trip_packing_items_trip_id', ['trip_id'], unique=False)

    # 12. Workouts
    op.create_table(
        'workouts',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('workout_type', sa.String(length=50), nullable=False, server_default='strength'),
        sa.Column('title', sa.String(length=120), nullable=False),
        sa.Column('duration_minutes', sa.Integer(), nullable=False),
        sa.Column('calories_burned', sa.Integer(), nullable=True),
        sa.Column('distance_km', sa.Numeric(6, 2), nullable=True),
        sa.Column('intensity', sa.String(length=20), nullable=False, server_default='medium'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('workout_date', sa.Date(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('workouts', schema=None) as batch_op:
        batch_op.create_index('ix_workouts_user_id', ['user_id'], unique=False)
        batch_op.create_index('ix_workouts_workout_date', ['workout_date'], unique=False)

    # 13. Personal Assets
    op.create_table(
        'personal_assets',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=150), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False, server_default='electronics'),
        sa.Column('purchase_date', sa.Date(), nullable=True),
        sa.Column('purchase_price', sa.Numeric(12, 2), nullable=True),
        sa.Column('currency', sa.String(length=10), nullable=False, server_default='USD'),
        sa.Column('serial_number', sa.String(length=100), nullable=True),
        sa.Column('warranty_expiry', sa.Date(), nullable=True),
        sa.Column('location', sa.String(length=100), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='active'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('personal_assets', schema=None) as batch_op:
        batch_op.create_index('ix_personal_assets_user_id', ['user_id'], unique=False)
        batch_op.create_index('ix_personal_assets_warranty_expiry', ['warranty_expiry'], unique=False)

    # 14. Asset Maintenance Records
    op.create_table(
        'asset_maintenance_records',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('asset_id', sa.String(length=36), nullable=False),
        sa.Column('service_date', sa.Date(), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=False),
        sa.Column('cost', sa.Numeric(10, 2), nullable=False, server_default='0.0'),
        sa.Column('service_provider', sa.String(length=100), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['asset_id'], ['personal_assets.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('asset_maintenance_records', schema=None) as batch_op:
        batch_op.create_index('ix_asset_maintenance_records_asset_id', ['asset_id'], unique=False)

    # 15. Bills
    op.create_table(
        'bills',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('title', sa.String(length=120), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False, server_default='utility'),
        sa.Column('amount', sa.Numeric(12, 2), nullable=False),
        sa.Column('currency', sa.String(length=10), nullable=False, server_default='USD'),
        sa.Column('due_date', sa.Date(), nullable=False),
        sa.Column('is_recurring', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('frequency', sa.String(length=20), nullable=False, server_default='monthly'),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='unpaid'),
        sa.Column('auto_pay', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('bills', schema=None) as batch_op:
        batch_op.create_index('ix_bills_user_id', ['user_id'], unique=False)
        batch_op.create_index('ix_bills_due_date', ['due_date'], unique=False)

    # 16. Bill Payments
    op.create_table(
        'bill_payments',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('bill_id', sa.String(length=36), nullable=False),
        sa.Column('amount_paid', sa.Numeric(12, 2), nullable=False),
        sa.Column('payment_date', sa.Date(), nullable=False),
        sa.Column('payment_method', sa.String(length=50), nullable=False, server_default='bank_transfer'),
        sa.Column('reference_number', sa.String(length=100), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['bill_id'], ['bills.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('bill_payments', schema=None) as batch_op:
        batch_op.create_index('ix_bill_payments_bill_id', ['bill_id'], unique=False)


def downgrade():
    op.drop_table('bill_payments')
    op.drop_table('bills')
    op.drop_table('asset_maintenance_records')
    op.drop_table('personal_assets')
    op.drop_table('workouts')
    op.drop_table('trip_packing_items')
    op.drop_table('trip_itinerary_items')
    op.drop_table('trips')
    op.drop_table('study_sessions')
    op.drop_table('learning_goals')
    op.drop_table('subscriptions')
    op.drop_table('contact_interactions')
    op.drop_table('contacts')
    op.drop_table('note_attachments')
    with op.batch_alter_table('notes', schema=None) as batch_op:
        batch_op.drop_constraint('fk_notes_folder_id', type_='foreignkey')
        batch_op.drop_index('ix_notes_folder_id')
        batch_op.drop_column('folder_id')
    op.drop_table('note_folders')

