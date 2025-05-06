"""create token stake events raw table

Revision ID: e3ff027707a0
Revises: d8822b756c18
Create Date: 2020-03-03 19:32:40.022260

"""
from alembic import op
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision = 'e3ff027707a0'
down_revision = 'd8822b756c18'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    conn.execute(text("""
        CREATE TABLE `token_stake_events_raw` (
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
          UNIQUE KEY `uq_st_ev` (`transactionHash`, `logIndex`)
        ) ;
            """))


def downgrade():
    conn = op.get_bind()
    conn.execute(text(
        """
            drop table token_stake_events_raw
        """
    ))
