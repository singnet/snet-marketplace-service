"""offchain_service_config_table_added

Revision ID: 4dd258579fce
Revises: 6947016cfc24
Create Date: 2021-07-16 16:29:39.966227

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '4dd258579fce'
down_revision = '6947016cfc24'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('offchain_service_config',
    sa.Column('row_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('org_id', sa.VARCHAR(length=128), nullable=False),
    sa.Column('service_id', sa.VARCHAR(length=128), nullable=False),
    sa.Column('parameter_name', sa.VARCHAR(length=128), nullable=False),
    sa.Column('parameter_value', sa.VARCHAR(length=512), nullable=False),
    sa.Column('created_on', mysql.TIMESTAMP(), nullable=False),
    sa.Column('updated_on', mysql.TIMESTAMP(), nullable=False),
    sa.PrimaryKeyConstraint('row_id'),
    sa.UniqueConstraint('org_id', 'service_id', 'parameter_name', name='uq_off')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('offchain_service_config')
    # ### end Alembic commands ###
