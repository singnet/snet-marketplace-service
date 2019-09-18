"""baseline

Revision ID: 8735e8263e53
Revises:
Create Date: 2019-09-18 14:37:42.662065

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8735e8263e53'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    conn.execute("""

        CREATE TABLE `purchase_history` (
        `row_id` int(11) NOT NULL AUTO_INCREMENT,
        `username` varchar(128) NOT NULL,
        `raw_payment_data` json NOT NULL,
        `type` varchar(64) NOT NULL,
        `order_id` varchar(128) NULL DEFAULT NULL,
        `payment_id` varchar(128) NULL DEFAULT NULL,
        `payment_trasaction_id` varchar(256) NULL DEFAULT NULL,
        `transaction_hash` varchar(256) NULL DEFAULT NULL,
        `status` varchar(64) NOT NULL,
        `row_created` timestamp NULL DEFAULT NULL,
        `row_updated` timestamp NULL DEFAULT NULL,
        PRIMARY KEY (`row_id`)
);

        """)


def downgrade():
    conn = op.get_bind()
    conn.execute("""

           
            drop table purchase_history;

            """)
