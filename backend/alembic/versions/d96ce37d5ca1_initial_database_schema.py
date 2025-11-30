"""Initial database schema

Revision ID: d96ce37d5ca1
Revises: 
Create Date: 2025-11-06 16:20:47.243970

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd96ce37d5ca1'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('first_name', sa.String(length=100), nullable=False),
        sa.Column('last_name', sa.String(length=100), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('role', sa.Enum('admin', 'adopter', 'shelter', name='userrole'), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('is_verified', sa.Boolean(), nullable=True),
        sa.Column('address_line1', sa.String(length=255), nullable=True),
        sa.Column('address_line2', sa.String(length=255), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=True),
        sa.Column('state', sa.String(length=100), nullable=True),
        sa.Column('postal_code', sa.String(length=20), nullable=True),
        sa.Column('country', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)

    # Create pets table
    op.create_table('pets',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('species', sa.Enum('dog', 'cat', 'bird', 'rabbit', 'hamster', 'fish', 'reptile', 'other', name='petspecies'), nullable=False),
        sa.Column('breed', sa.String(length=100), nullable=True),
        sa.Column('age_years', sa.Integer(), nullable=True),
        sa.Column('age_months', sa.Integer(), nullable=True),
        sa.Column('gender', sa.Enum('male', 'female', 'unknown', name='petgender'), nullable=False),
        sa.Column('size', sa.Enum('small', 'medium', 'large', 'extra_large', name='petsize'), nullable=False),
        sa.Column('weight_kg', sa.Float(), nullable=True),
        sa.Column('color', sa.String(length=100), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('medical_info', sa.Text(), nullable=True),
        sa.Column('behavioral_info', sa.Text(), nullable=True),
        sa.Column('special_needs', sa.Text(), nullable=True),
        sa.Column('adoption_fee', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('status', sa.Enum('available', 'pending', 'adopted', 'hold', 'not_available', name='petstatus'), nullable=False),
        sa.Column('shelter_id', sa.Integer(), nullable=False),
        sa.Column('microchip_id', sa.String(length=50), nullable=True),
        sa.Column('vaccination_status', sa.String(length=100), nullable=True),
        sa.Column('spayed_neutered', sa.Boolean(), nullable=True),
        sa.Column('house_trained', sa.Boolean(), nullable=True),
        sa.Column('good_with_kids', sa.Boolean(), nullable=True),
        sa.Column('good_with_pets', sa.Boolean(), nullable=True),
        sa.Column('energy_level', sa.Enum('low', 'medium', 'high', name='energylevel'), nullable=True),
        sa.Column('photos', sa.JSON(), nullable=True),
        sa.Column('videos', sa.JSON(), nullable=True),
        sa.Column('documents', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['shelter_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_pets_id'), 'pets', ['id'], unique=False)
    op.create_index(op.f('ix_pets_species'), 'pets', ['species'], unique=False)
    op.create_index(op.f('ix_pets_status'), 'pets', ['status'], unique=False)

    # Create adoption_applications table
    op.create_table('adoption_applications',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('pet_id', sa.Integer(), nullable=False),
        sa.Column('applicant_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.Enum('pending', 'under_review', 'approved', 'rejected', 'withdrawn', name='applicationstatus'), nullable=False),
        sa.Column('application_data', sa.JSON(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('reviewed_by', sa.Integer(), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['applicant_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['pet_id'], ['pets.id'], ),
        sa.ForeignKeyConstraint(['reviewed_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_adoption_applications_id'), 'adoption_applications', ['id'], unique=False)

    # Create chat_rooms table
    op.create_table('chat_rooms',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('application_id', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['application_id'], ['adoption_applications.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('application_id')
    )
    op.create_index(op.f('ix_chat_rooms_id'), 'chat_rooms', ['id'], unique=False)

    # Create messages table
    op.create_table('messages',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('chat_room_id', sa.Integer(), nullable=False),
        sa.Column('sender_id', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('message_type', sa.Enum('text', 'image', 'document', name='messagetype'), nullable=False),
        sa.Column('file_url', sa.String(length=255), nullable=True),
        sa.Column('is_read', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['chat_room_id'], ['chat_rooms.id'], ),
        sa.ForeignKeyConstraint(['sender_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_messages_id'), 'messages', ['id'], unique=False)

    # Create notifications table
    op.create_table('notifications',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('type', sa.Enum('application', 'message', 'system', 'reminder', name='notificationtype'), nullable=False),
        sa.Column('is_read', sa.Boolean(), nullable=True),
        sa.Column('action_url', sa.String(length=255), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_notifications_id'), 'notifications', ['id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop tables in reverse order to respect foreign key constraints
    op.drop_index(op.f('ix_notifications_id'), table_name='notifications')
    op.drop_table('notifications')
    op.drop_index(op.f('ix_messages_id'), table_name='messages')
    op.drop_table('messages')
    op.drop_index(op.f('ix_chat_rooms_id'), table_name='chat_rooms')
    op.drop_table('chat_rooms')
    op.drop_index(op.f('ix_adoption_applications_id'), table_name='adoption_applications')
    op.drop_table('adoption_applications')
    op.drop_index(op.f('ix_pets_status'), table_name='pets')
    op.drop_index(op.f('ix_pets_species'), table_name='pets')
    op.drop_index(op.f('ix_pets_id'), table_name='pets')
    op.drop_table('pets')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
