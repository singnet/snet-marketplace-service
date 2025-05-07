"""baseline

Revision ID: d8822b756c18
Revises:
Create Date: 2019-09-18 14:33:54.629555

"""
from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = 'd8822b756c18'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    conn.execute(text("""
        CREATE TABLE `user_wallet` (
          `row_id` int NOT NULL AUTO_INCREMENT,
          `username` varchar(128) NOT NULL,
          `address` varchar(256) NOT NULL,
          `is_default` bit(1) DEFAULT b'0',
          `row_created` timestamp NULL DEFAULT NULL,
          `row_updated` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
          PRIMARY KEY (`row_id`),
          UNIQUE KEY `uq_wallet` (`username`, `address`)
       );
    """))
    conn.execute(text("""
        CREATE TABLE `channel_transaction_history` (
          `row_id` int NOT NULL AUTO_INCREMENT,
          `order_id` varchar(128) NOT NULL,
          `amount` int NOT NULL,
          `currency` varchar(64) NOT NULL,
          `type` varchar(128) DEFAULT NULL,
          `address` varchar(255) DEFAULT NULL,
          `recipient` varchar(255) DEFAULT NULL,
          `signature` varchar(255) DEFAULT NULL,
          `org_id` varchar(255) DEFAULT NULL,
          `group_id` varchar(255) DEFAULT NULL,
          `request_parameters` varchar(1024) DEFAULT NULL,
          `transaction_hash` varchar(255) DEFAULT NULL,
          `status` VARCHAR(255),
          `row_created` timestamp NULL DEFAULT NULL,
          `row_updated` timestamp NULL DEFAULT NULL,
          PRIMARY KEY (`row_id`)
        );
       """))
    conn.execute(text("""
        CREATE TABLE `wallet` (
          `row_id` int NOT NULL AUTO_INCREMENT,
          `address` varchar(256) NOT NULL,
          `type` varchar(128) DEFAULT NULL,
          `status` bit(1) DEFAULT b'1',
          `row_created` timestamp NULL DEFAULT NULL,
          `row_updated` timestamp NULL DEFAULT NULL,
          PRIMARY KEY (`row_id`),
          UNIQUE KEY `uq_wallet` (`address`)
       );
       """))


def downgrade():
    conn = op.get_bind()
    conn.execute(text("DROP TABLE wallet"))
    conn.execute(text("DROP TABLE channel_transaction_history"))
    conn.execute(text("DROP TABLE user_wallet"))


