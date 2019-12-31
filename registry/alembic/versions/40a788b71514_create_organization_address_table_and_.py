"""create organization address table and duns no will be part of organization table

Revision ID: 40a788b71514
Revises: e70a6807544e
Create Date: 2019-12-31 12:11:59.361336

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '40a788b71514'
down_revision = 'e70a6807544e'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('organization_address',
                    sa.Column('row_id', sa.Integer(), autoincrement=True, nullable=False),
                    sa.Column('org_row_id', sa.Integer(), nullable=False),
                    sa.Column('address_type', sa.VARCHAR(length=64), nullable=False),
                    sa.Column('street_address', sa.VARCHAR(length=256), nullable=False),
                    sa.Column('city', sa.VARCHAR(length=64), nullable=False),
                    sa.Column('pincode', sa.VARCHAR(length=10), nullable=False),
                    sa.Column('state', sa.VARCHAR(length=64), nullable=False),
                    sa.Column('country', sa.VARCHAR(length=64), nullable=False),
                    sa.Column('created_on', mysql.TIMESTAMP(), nullable=True),
                    sa.Column('updated_on', mysql.TIMESTAMP(), nullable=True),
                    sa.ForeignKeyConstraint(['org_row_id'], ['organization.row_id'], onupdate='CASCADE',
                                            ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint('row_id')
                    )
    op.add_column('organization',
                  sa.Column('duns_no', sa.VARCHAR(length=20), nullable=True))


def downgrade():
    op.drop_table('organization_address')
    op.drop_column('organization', 'duns_no')