"""create trulioo_transaction_history table

Revision ID: f72d9e8fbd5b
Revises: 8735e8263e53
Create Date: 2019-12-12 17:08:25.579811

"""
from alembic import op
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision = 'f72d9e8fbd5b'
down_revision = '8735e8263e53'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    conn.execute(text("""
         CREATE TABLE `trulioo_transaction_history` (
            `row_id` int NOT NULL AUTO_INCREMENT,
            `transaction_id` varchar(128) NOT NULL,
            `transaction_record_id` varchar(128) NOT NULL,
            `country_code` varchar(2) NOT NULL,
            `product_name` varchar(64) NOT NULL,
            `uploaded_date` varchar(64) NOT NULL,
            `record_status` varchar(64) NOT NULL,
            `row_created` timestamp NULL DEFAULT NULL,
            `row_updated` timestamp NULL DEFAULT NULL,
            PRIMARY KEY (`row_id`),
            UNIQUE KEY `uq_trxn_id` (`transaction_id`),
            UNIQUE KEY `uq_trxn_rec_id` (`transaction_record_id`)
        );
    """))


def downgrade():
    conn = op.get_bind()
    conn.execute(text("""
            drop table trulioo_transaction_history;
            """))
