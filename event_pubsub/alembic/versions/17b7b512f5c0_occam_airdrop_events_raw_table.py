"""occam_airdrop_events_raw_table

Revision ID: 17b7b512f5c0
Revises: ab2543ca5262
Create Date: 2021-12-23 19:52:46.192866

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '17b7b512f5c0'
down_revision = 'ab2543ca5262'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('occam_airdrop_events_raw',
    sa.Column('row_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('block_no', sa.Integer(), nullable=False),
    sa.Column('uncle_block_no', sa.Integer(), nullable=True),
    sa.Column('event', sa.VARCHAR(length=256), nullable=False),
    sa.Column('json_str', sa.VARCHAR(length=256), nullable=True),
    sa.Column('processed', mysql.BIT(), nullable=True),
    sa.Column('transactionHash', sa.VARCHAR(length=256), nullable=True),
    sa.Column('logIndex', sa.VARCHAR(length=256), nullable=True),
    sa.Column('error_code', sa.Integer(), nullable=True),
    sa.Column('error_msg', sa.VARCHAR(length=256), nullable=True),
    sa.Column('row_updated', mysql.TIMESTAMP(), nullable=True),
    sa.Column('row_created', mysql.TIMESTAMP(), nullable=True),
    sa.PrimaryKeyConstraint('row_id'),
    sa.UniqueConstraint('transactionHash', 'logIndex', name='uq_oaer')
    )
    op.create_index('blk_no_idx', 'occam_airdrop_events_raw', ['block_no'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('blk_no_idx', table_name='occam_airdrop_events_raw')
    op.drop_table('occam_airdrop_events_raw')
    # ### end Alembic commands ###
