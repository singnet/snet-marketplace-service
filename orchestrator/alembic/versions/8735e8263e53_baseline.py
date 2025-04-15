"""baseline

Revision ID: 8735e8263e53
Revises:
Create Date: 2019-09-18 14:37:42.662065

"""
from sqlalchemy import text
from alembic import op

# revision identifiers, used by Alembic.
revision = "8735e8263e53"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    conn.execute(text("""
         CREATE TABLE `transaction_history` (
            `row_id` int NOT NULL AUTO_INCREMENT,
            `username` varchar(128) NOT NULL,
            `order_id` varchar(128) NOT NULL,
            `order_type` varchar(64) NOT NULL,
            `status` varchar(64) NOT NULL,
            `payment_id` varchar(128) NULL DEFAULT NULL,
            `payment_type` varchar(64) NULL DEFAULT NULL,
            `payment_method` varchar(255) NULL DEFAULT NULL,
            `raw_payment_data` json NOT NULL,
            `transaction_hash` varchar(255) NULL DEFAULT NULL,
            `row_created` timestamp NULL DEFAULT NULL,
            `row_updated` timestamp NULL DEFAULT NULL,
            PRIMARY KEY (`row_id`));
            """))


def downgrade():
    conn = op.get_bind()
    conn.execute(text("""
            drop table transaction_history;
            """))
