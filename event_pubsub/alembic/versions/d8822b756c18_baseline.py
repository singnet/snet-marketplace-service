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
        CREATE TABLE `registry_events_raw` (
          `row_id` int(11) NOT NULL AUTO_INCREMENT,
          `block_no` int(11) NOT NULL,
          `event` varchar(256) NOT NULL,
          `json_str` text,
          `processed` bit(1) DEFAULT NULL,
          `transactionHash` varchar(256) DEFAULT NULL,
          `logIndex` varchar(256) DEFAULT NULL,
          `error_code` int(11) DEFAULT NULL,
          `error_msg` varchar(256) DEFAULT NULL,
          `row_updated` timestamp NULL DEFAULT NULL,
          `row_created` timestamp NULL DEFAULT NULL,
          PRIMARY KEY (`row_id`),
          KEY `blk_no_idx` (`block_no`),
          UNIQUE KEY `uq_rg_ev` (`block_no`,`transactionHash`)
        );
      """))

    conn.execute(text("""
        CREATE TABLE `mpe_events_raw` (
          `row_id` int(11) NOT NULL AUTO_INCREMENT,
          `block_no` int(11) NOT NULL,
          `event` varchar(256) NOT NULL,
          `json_str` text,
          `processed` bit(1) DEFAULT NULL,
          `transactionHash` varchar(256) DEFAULT NULL,
          `logIndex` varchar(256) DEFAULT NULL,
          `error_code` int(11) DEFAULT NULL,
          `error_msg` varchar(256) DEFAULT NULL,
          `row_updated` timestamp NULL DEFAULT NULL,
          `row_created` timestamp NULL DEFAULT NULL,
          PRIMARY KEY (`row_id`),
          KEY `blk_no_idx` (`block_no`),
          UNIQUE KEY `uq_mpe_ev` (`block_no`,`transactionHash`)
        ) ;
        """))
    conn.execute(text("""
        CREATE TABLE `rfai_events_raw` (
          `row_id` int(11) NOT NULL AUTO_INCREMENT,
          `block_no` int(11) NOT NULL,
          `event` varchar(256) NOT NULL,
          `json_str` text,
          `processed` bit(1) DEFAULT NULL,
          `transactionHash` varchar(256) DEFAULT NULL,
          `logIndex` varchar(256) DEFAULT NULL,
          `error_code` int(11) DEFAULT NULL,
          `error_msg` varchar(256) DEFAULT NULL,
          `row_updated` timestamp NULL DEFAULT NULL,
          `row_created` timestamp NULL DEFAULT NULL,
          PRIMARY KEY (`row_id`),
          KEY `blk_no_idx` (`block_no`),
          UNIQUE KEY `uq_rf_ev` (`block_no`,`transactionHash`)
        )
        """))

    conn.execute(text("""
        CREATE TABLE `event_blocknumber_marker` (
          `row_id` int(11) NOT NULL AUTO_INCREMENT,
          `event_type` varchar(128) NOT NULL,
          `last_block_number` int(11) not null,
          `row_created` timestamp NULL DEFAULT NULL,
          `row_updated` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
          PRIMARY KEY (`row_id`)
        )

        """))


def downgrade():
    conn = op.get_bind()
    conn.execute(text("""
                drop table registry_events_raw
            """))
    conn.execute(text("""
                drop table mpe_events_raw
                """
                 ))
    conn.execute(text("""
                drop table user_wallet
       """
    ))
