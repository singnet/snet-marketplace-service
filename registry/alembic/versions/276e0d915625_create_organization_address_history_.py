"""create organization address history table

Revision ID: 276e0d915625
Revises: 0a1eced60e7d
Create Date: 2019-12-30 11:48:19.723884

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '276e0d915625'
down_revision = '0a1eced60e7d'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('organization_address_history',
                    sa.Column('row_id', sa.Integer(), nullable=False),
                    sa.Column('org_row_id', sa.Integer(), nullable=False),
                    sa.Column('headquater_address', mysql.JSON(), nullable=False),
                    sa.Column('mailing_address', mysql.JSON(), nullable=False),
                    sa.Column('created_on', mysql.TIMESTAMP(), nullable=True),
                    sa.Column('updated_on', mysql.TIMESTAMP(), nullable=True),
                    sa.ForeignKeyConstraint(['org_row_id'], ['organization_history.row_id'], onupdate='CASCADE',
                                            ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint('row_id')
                    )


def downgrade():
    op.drop_table('organization_address_history')
