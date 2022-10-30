"""empty message

Revision ID: 3ce7ebcaeaf9
Revises: 
Create Date: 2022-10-30 18:43:05.322517

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3ce7ebcaeaf9'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('location',
    sa.Column('id', sa.Integer(), nullable=False, auto_increment=True),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('city', sa.String(length=64), nullable=True),
    sa.Column('state', sa.String(length=64), nullable=True),
    sa.Column('zip', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_location_city'), 'location', ['city'], unique=False)
    op.create_index(op.f('ix_location_name'), 'location', ['name'], unique=False)
    op.create_index(op.f('ix_location_state'), 'location', ['state'], unique=False)
    op.create_table('tech',
    sa.Column('id', sa.Integer(), nullable=False, auto_increment=True),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tech_id'), 'tech', ['id'], unique=False)
    op.create_index(op.f('ix_tech_name'), 'tech', ['name'], unique=False)
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False, auto_increment=True),
    sa.Column('username', sa.String(length=64), nullable=True),
    sa.Column('password_hash', sa.String(length=64), nullable=True),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('guest', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('space',
    sa.Column('id', sa.Integer(), nullable=False, auto_increment=True),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('sizeCap', sa.Integer(), nullable=True),
    sa.Column('hourlyRate', sa.Integer(), nullable=True),
    sa.Column('location', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['location'], ['location.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_space_hourlyRate'), 'space', ['hourlyRate'], unique=False)
    op.create_index(op.f('ix_space_location'), 'space', ['location'], unique=False)
    op.create_index(op.f('ix_space_name'), 'space', ['name'], unique=False)
    op.create_index(op.f('ix_space_sizeCap'), 'space', ['sizeCap'], unique=False)
    op.create_table('meeting_history',
    sa.Column('id', sa.Integer(), nullable=False, auto_increment=True),
    sa.Column('uid', sa.Integer(), nullable=True),
    sa.Column('spid', sa.Integer(), nullable=True),
    sa.Column('date', sa.Date(), nullable=True),
    sa.Column('startTime', sa.Time(), nullable=True),
    sa.Column('endTime', sa.Time(), nullable=True),
    sa.ForeignKeyConstraint(['spid'], ['space.id'], ),
    sa.ForeignKeyConstraint(['uid'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_meeting_history_spid'), 'meeting_history', ['spid'], unique=False)
    op.create_index(op.f('ix_meeting_history_uid'), 'meeting_history', ['uid'], unique=False)
    op.create_table('reviews',
    sa.Column('id', sa.Integer(), nullable=False, auto_increment=True),
    sa.Column('uid', sa.Integer(), nullable=True),
    sa.Column('spid', sa.Integer(), nullable=True),
    sa.Column('score', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['spid'], ['space.id'], ),
    sa.ForeignKeyConstraint(['uid'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('tech_to_space',
    sa.Column('id', sa.Integer(), nullable=False, auto_increment=True),
    sa.Column('tid', sa.Integer(), nullable=True),
    sa.Column('spid', sa.Integer(), nullable=True),
    sa.Column('count', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['spid'], ['space.id'], ),
    sa.ForeignKeyConstraint(['tid'], ['tech.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tech_to_space_id'), 'tech_to_space', ['id'], unique=False)
    op.create_table('upcoming_meeting',
    sa.Column('id', sa.Integer(), nullable=False, auto_increment=True),
    sa.Column('uid', sa.Integer(), nullable=True),
    sa.Column('spid', sa.Integer(), nullable=True),
    sa.Column('date', sa.Date(), nullable=True),
    sa.Column('startTime', sa.Time(), nullable=True),
    sa.Column('endTime', sa.Time(), nullable=True),
    sa.ForeignKeyConstraint(['spid'], ['space.id'], ),
    sa.ForeignKeyConstraint(['uid'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_upcoming_meeting_spid'), 'upcoming_meeting', ['spid'], unique=False)
    op.create_index(op.f('ix_upcoming_meeting_uid'), 'upcoming_meeting', ['uid'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_upcoming_meeting_uid'), table_name='upcoming_meeting')
    op.drop_index(op.f('ix_upcoming_meeting_spid'), table_name='upcoming_meeting')
    op.drop_table('upcoming_meeting')
    op.drop_index(op.f('ix_tech_to_space_id'), table_name='tech_to_space')
    op.drop_table('tech_to_space')
    op.drop_table('reviews')
    op.drop_index(op.f('ix_meeting_history_uid'), table_name='meeting_history')
    op.drop_index(op.f('ix_meeting_history_spid'), table_name='meeting_history')
    op.drop_table('meeting_history')
    op.drop_index(op.f('ix_space_sizeCap'), table_name='space')
    op.drop_index(op.f('ix_space_name'), table_name='space')
    op.drop_index(op.f('ix_space_location'), table_name='space')
    op.drop_index(op.f('ix_space_hourlyRate'), table_name='space')
    op.drop_table('space')
    op.drop_table('user')
    op.drop_index(op.f('ix_tech_name'), table_name='tech')
    op.drop_index(op.f('ix_tech_id'), table_name='tech')
    op.drop_table('tech')
    op.drop_index(op.f('ix_location_state'), table_name='location')
    op.drop_index(op.f('ix_location_name'), table_name='location')
    op.drop_index(op.f('ix_location_city'), table_name='location')
    op.drop_table('location')
    # ### end Alembic commands ###
