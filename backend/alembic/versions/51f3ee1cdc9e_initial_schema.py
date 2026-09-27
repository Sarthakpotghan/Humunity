"""initial schema

Revision ID: 51f3ee1cdc9e
Revises: 
Create Date: 2026-09-23 15:38:37.784940

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '51f3ee1cdc9e'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('role', sa.Enum('DONOR', 'NGO', 'VOLUNTEER', 'ADMIN', name='userrole'), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('lat', sa.Float(), nullable=True),
        sa.Column('lng', sa.Float(), nullable=True),
        sa.Column('verified', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
    )
    op.create_index('ix_users_lat_lng', 'users', ['lat', 'lng'])
    op.create_index('ix_users_email', 'users', ['email'])

    op.create_table(
        'ngo_profiles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('reg_number', sa.String(length=100), nullable=False),
        sa.Column('reg_doc_url', sa.String(length=500), nullable=True),
        sa.Column('focus_areas', sa.JSON(), nullable=True),
        sa.Column('reliability_score', sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id'),
    )

    op.create_table(
        'donations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('donor_id', sa.Integer(), nullable=False),
        sa.Column('category', sa.Enum('CLOTHES', 'STATIONERY', name='itemcategory'), nullable=False),
        sa.Column('item_type', sa.String(length=100), nullable=False),
        sa.Column('size', sa.String(length=50), nullable=True),
        sa.Column('age_group', sa.String(length=50), nullable=True),
        sa.Column('gender', sa.String(length=20), nullable=True),
        sa.Column('season', sa.String(length=50), nullable=True),
        sa.Column('condition', sa.Enum('NEW', 'GOOD', 'FAIR', name='itemcondition'), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('lat', sa.Float(), nullable=True),
        sa.Column('lng', sa.Float(), nullable=True),
        sa.Column('available_from', sa.DateTime(), nullable=True),
        sa.Column('available_to', sa.DateTime(), nullable=True),
        sa.Column('status', sa.Enum('LISTED', 'MATCHED', 'ACCEPTED', 'PICKUP_SCHEDULED', 'IN_TRANSIT', 'DELIVERED', 'CONFIRMED', 'REJECTED', 'EXPIRED', name='donationstatus'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['donor_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_donations_category_status', 'donations', ['category', 'status'])

    op.create_table(
        'donation_photos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('donation_id', sa.Integer(), nullable=False),
        sa.Column('url', sa.String(length=500), nullable=False),
        sa.ForeignKeyConstraint(['donation_id'], ['donations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'requests',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ngo_id', sa.Integer(), nullable=False),
        sa.Column('category', sa.Enum('CLOTHES', 'STATIONERY', name='itemcategory'), nullable=False),
        sa.Column('item_type', sa.String(length=100), nullable=False),
        sa.Column('size', sa.String(length=50), nullable=True),
        sa.Column('age_group', sa.String(length=50), nullable=True),
        sa.Column('gender', sa.String(length=20), nullable=True),
        sa.Column('season', sa.String(length=50), nullable=True),
        sa.Column('quantity_needed', sa.Integer(), nullable=False),
        sa.Column('urgency', sa.Integer(), nullable=False),
        sa.Column('beneficiary_group', sa.String(length=100), nullable=True),
        sa.Column('deadline', sa.DateTime(), nullable=True),
        sa.Column('status', sa.Enum('ACTIVE', 'FULFILLED', 'CLOSED', 'EXPIRED', name='requeststatus'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['ngo_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_requests_category_status_deadline', 'requests', ['category', 'status', 'deadline'])

    op.create_table(
        'matches',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('donation_id', sa.Integer(), nullable=False),
        sa.Column('request_id', sa.Integer(), nullable=False),
        sa.Column('score', sa.Float(), nullable=False),
        sa.Column('score_breakdown', sa.JSON(), nullable=True),
        sa.Column('status', sa.Enum('PENDING', 'ACCEPTED', 'REJECTED', 'EXPIRED', name='matchstatus'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['donation_id'], ['donations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['request_id'], ['requests.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'deliveries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('match_id', sa.Integer(), nullable=False),
        sa.Column('mode', sa.Enum('DROPOFF', 'PICKUP', name='deliverymode'), nullable=False),
        sa.Column('volunteer_id', sa.Integer(), nullable=True),
        sa.Column('scheduled_at', sa.DateTime(), nullable=True),
        sa.Column('delivered_at', sa.DateTime(), nullable=True),
        sa.Column('status', sa.Enum('SCHEDULED', 'IN_TRANSIT', 'DELIVERED', 'CONFIRMED', 'CANCELLED', name='deliverystatus'), nullable=False),
        sa.ForeignKeyConstraint(['match_id'], ['matches.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['volunteer_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('match_id'),
    )

    op.create_table(
        'delivery_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('delivery_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.Enum('SCHEDULED', 'IN_TRANSIT', 'DELIVERED', 'CONFIRMED', 'CANCELLED', name='deliverystatus'), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['delivery_id'], ['deliveries.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'notifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('is_read', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'feedback',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('match_id', sa.Integer(), nullable=False),
        sa.Column('giver_id', sa.Integer(), nullable=False),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('comments', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['giver_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['match_id'], ['matches.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('match_id'),
    )


def downgrade() -> None:
    op.drop_table('feedback')
    op.drop_table('notifications')
    op.drop_table('delivery_events')
    op.drop_table('deliveries')
    op.drop_table('matches')
    op.drop_index('ix_requests_category_status_deadline', table_name='requests')
    op.drop_table('requests')
    op.drop_table('donation_photos')
    op.drop_index('ix_donations_category_status', table_name='donations')
    op.drop_table('donations')
    op.drop_table('ngo_profiles')
    op.drop_index('ix_users_lat_lng', table_name='users')
    op.drop_index('ix_users_email', table_name='users')
    op.drop_table('users')
    op.execute('DROP TYPE IF EXISTS userrole')
    op.execute('DROP TYPE IF EXISTS itemcategory')
    op.execute('DROP TYPE IF EXISTS itemcondition')
    op.execute('DROP TYPE IF EXISTS donationstatus')
    op.execute('DROP TYPE IF EXISTS requeststatus')
    op.execute('DROP TYPE IF EXISTS matchstatus')
    op.execute('DROP TYPE IF EXISTS deliverymode')
    op.execute('DROP TYPE IF EXISTS deliverystatus')