"""empty message

Revision ID: c86eba828bc7
Revises: 
Create Date: 2021-01-10 14:50:40.043682

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'c86eba828bc7'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('login', sa.String(), nullable=False),
        sa.Column('password', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('id'),
        sa.UniqueConstraint('login'),
        )
    op.create_table(
        'users_sign_in',
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('logged_in_by', sa.DateTime(), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('user_device_type', sa.Enum('mobile', 'pc', 'smart_tv', name='device_types_enum'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        postgresql_partition_by='list(user_device_type)'
    )

    conn = op.get_bind()
    conn.execute(sa.text(
        '''
        CREATE TABLE IF NOT EXISTS "user_sign_in_smart" PARTITION OF "users_sign_in" FOR VALUES IN ('smart_tv')
        '''
    ))
    conn.execute(sa.text(
        '''
        CREATE TABLE IF NOT EXISTS "user_sign_in_pc" PARTITION OF "users_sign_in" FOR VALUES IN ('pc')
        '''
    ))
    conn.execute(sa.text(
        '''
        CREATE TABLE IF NOT EXISTS "user_sign_in_mobile" PARTITION OF "users_sign_in" FOR VALUES IN ('mobile')
        '''
    ))



def downgrade():
    op.drop_table('user_sign_in_smart')
    op.drop_table('user_sign_in_mobile')
    op.drop_table('user_sign_in_pc')
    op.drop_table('users_sign_in')
    op.drop_table('users')
