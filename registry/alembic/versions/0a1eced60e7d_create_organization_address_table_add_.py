"""create organization address table, add audit columns and add duns attribute in organization table

Revision ID: 0a1eced60e7d
Revises: e70a6807544e
Create Date: 2019-12-27 14:49:21.280864

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '0a1eced60e7d'
down_revision = 'e70a6807544e'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('organization_address',
                    sa.Column('row_id', sa.Integer(), autoincrement=True, nullable=False),
                    sa.Column('organization_row_id', sa.Integer(), nullable=False),
                    sa.Column('headquater_address', mysql.JSON(), nullable=False),
                    sa.Column('mailing_address', mysql.JSON(), nullable=False),
                    sa.Column('created_on', mysql.TIMESTAMP(), nullable=True),
                    sa.Column('updated_on', mysql.TIMESTAMP(), nullable=True),
                    sa.PrimaryKeyConstraint('row_id')
                    )
    op.add_column('organization',
                  sa.Column('duns_no', sa.VARCHAR(length=20), nullable=True))
    op.add_column('organization',
                  sa.Column('created_on', mysql.TIMESTAMP(), nullable=True))
    op.add_column('organization',
                  sa.Column('updated_on', mysql.TIMESTAMP(), nullable=True))

    op.add_column('org_member',
                  sa.Column('created_on', mysql.TIMESTAMP(), nullable=True))
    op.add_column('org_member',
                  sa.Column('updated_on', mysql.TIMESTAMP(), nullable=True))

    op.add_column('group',
                  sa.Column('created_on', mysql.TIMESTAMP(), nullable=True))
    op.add_column('group',
                  sa.Column('updated_on', mysql.TIMESTAMP(), nullable=True))

    op.add_column('organization_history',
                  sa.Column('created_on', mysql.TIMESTAMP(), nullable=True))
    op.add_column('organization_history',
                  sa.Column('updated_on', mysql.TIMESTAMP(), nullable=True))


def downgrade():
    op.drop_table('organization_address')
    op.drop_column('organization', 'duns_no')
    op.drop_column('organization', 'created_on')
    op.drop_column('organization', 'updated_on')

    op.drop_column('organization_history', 'created_on')
    op.drop_column('organization_history', 'updated_on')

    op.drop_column('group', 'created_on')
    op.drop_column('group', 'updated_on')

    op.drop_column('org_member', 'created_on')
    op.drop_column('org_member', 'updated_on')
