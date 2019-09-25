"""baseline

Revision ID: d8822b756c18
Revises:
Create Date: 2019-09-18 14:33:54.629555

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = 'd8822b756c18'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    conn = op.get_bind()
    conn.execute("""
        CREATE TABLE `user_wallet` (
          `row_id` int(11) NOT NULL AUTO_INCREMENT,
          `username` varchar(128) NOT NULL,
          `address` varchar(256) NOT NULL,
          `is_default` bit(1) DEFAULT b'0',
          `row_created` timestamp NULL DEFAULT NULL,
          `row_updated` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
          PRIMARY KEY (`row_id`),
          UNIQUE KEY `uq_user` (`username`),
          UNIQUE KEY `uq_wallet` (`address`)
       );
    """)
    conn.execute("""
        CREATE TABLE `channel_transaction_history` (
          `row_id` int(11) NOT NULL AUTO_INCREMENT,
          `order_id` varchar(128) NOT NULL,
          `amount` int(11) NOT NULL,
          `currency` varchar(64) NOT NULL,
          `type` varchar(128) DEFAULT NULL,
          `address` varchar(256) DEFAULT NULL,
          `signature` varchar(256) DEFAULT NULL,
          `request_parameters` varchar(1024) DEFAULT NULL,
          `transaction_type` varchar(128) DEFAULT NULL,
          `transaction_hash` varchar(256) DEFAULT NULL,
          `status` bit(1) DEFAULT b'1',
          `row_created` timestamp NULL DEFAULT NULL,
          `row_updated` timestamp NULL DEFAULT NULL,
          PRIMARY KEY (`row_id`)
        );
       """)
    conn.execute("""
        CREATE TABLE `wallet` (
          `row_id` int(11) NOT NULL AUTO_INCREMENT,
          `address` varchar(256) NOT NULL,
          `type` varchar(128) DEFAULT NULL,
          `status` bit(1) DEFAULT b'1',
          `row_created` timestamp NULL DEFAULT NULL,
          `row_updated` timestamp NULL DEFAULT NULL,
          PRIMARY KEY (`row_id`),
          UNIQUE KEY `uq_wallet` (`address`)
       );
       """)



def downgrade():
    conn = op.get_bind()
    conn.execute("""
                drop table wallet
            """
                 )
    conn.execute("""
                drop table wallet_transaction_history
                """
    )
    conn.execute("""
                drop table user_wallet
       """
    )


