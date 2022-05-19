"""empty message

Revision ID: c3f9b4723f8e
Revises: be9592410209
Create Date: 2022-05-17 17:11:02.773759

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'c3f9b4723f8e'
down_revision = 'be9592410209'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('achievements',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('description', sa.String(), nullable=False),
    sa.Column('stages', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('achievement_progress',
    sa.Column('user', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('achievement', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('progress', sa.Integer(), nullable=False),
    sa.Column('completed_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['achievement'], ['achievements.id'], ),
    sa.ForeignKeyConstraint(['user'], ['users.id'], ),
    sa.PrimaryKeyConstraint('user', 'achievement')
    )
    op.create_table('admin',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.ForeignKeyConstraint(['id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('friend_invites',
    sa.Column('invitee', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('code', sa.Integer(), nullable=False),
    sa.Column('expires_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['invitee'], ['users.id'], ),
    sa.PrimaryKeyConstraint('invitee')
    )
    op.create_table('friends',
    sa.Column('invitee', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('invited', postgresql.UUID(as_uuid=True), nullable=False),
    sa.CheckConstraint('invitee <> invited'),
    sa.ForeignKeyConstraint(['invited'], ['users.id'], ),
    sa.ForeignKeyConstraint(['invitee'], ['users.id'], ),
    sa.PrimaryKeyConstraint('invitee', 'invited')
    )
    op.create_table('user_lang',
    sa.Column('user', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('language', sa.Enum('catalan', 'spanish', 'english', name='lang'), nullable=False),
    sa.ForeignKeyConstraint(['user'], ['users.id'], ),
    sa.PrimaryKeyConstraint('user', 'language')
    )
    op.create_table('likes',
    sa.Column('event_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.ForeignKeyConstraint(['event_id'], ['events.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('event_id', 'user_id')
    )
    op.create_table('participant',
    sa.Column('event_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.ForeignKeyConstraint(['event_id'], ['events.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('event_id', 'user_id')
    )
    op.add_column('email_verification', sa.Column('expires_at', sa.DateTime(), nullable=True))
    op.add_column('events', sa.Column('date_creation', sa.DateTime(), nullable=False))
    op.add_column('events', sa.Column('event_image_uri', sa.String(), nullable=True))
    op.create_foreign_key(None, 'events', 'users', ['user_creator'], ['id'])
    op.drop_column('users', 'profile_img_uri')
    op.drop_column('users', 'mini_profile_img_uri')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('mini_profile_img_uri', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('users', sa.Column('profile_img_uri', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'events', type_='foreignkey')
    op.drop_column('events', 'event_image_uri')
    op.drop_column('events', 'date_creation')
    op.drop_column('email_verification', 'expires_at')
    op.drop_table('participant')
    op.drop_table('likes')
    op.drop_table('user_lang')
    op.drop_table('friends')
    op.drop_table('friend_invites')
    op.drop_table('admin')
    op.drop_table('achievement_progress')
    op.drop_table('achievements')
    # ### end Alembic commands ###
