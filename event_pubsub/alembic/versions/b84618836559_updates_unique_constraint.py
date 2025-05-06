"""updates_unique_constraint

Revision ID: b84618836559
Revises: e3ff027707a0
Create Date: 2020-05-05 15:53:22.105650

"""
from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = 'b84618836559'
down_revision = 'e3ff027707a0'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    conn.execute(text("""
        ALTER TABLE token_stake_events_raw
        DROP INDEX uq_st_ev;
    """))
    conn.execute(text("""
        ALTER TABLE registry_events_raw
        DROP INDEX uq_rg_ev;
    """))
    conn.execute(text("""
        ALTER TABLE mpe_events_raw
        DROP INDEX uq_mpe_ev;
    """))
    conn.execute(text("""
        ALTER TABLE rfai_events_raw
        DROP INDEX uq_rf_ev;
    """))
    conn.execute(text("""
        ALTER TABLE token_stake_events_raw
        ADD CONSTRAINT uq_st_ev UNIQUE (`transactionHash`);
    """))
    conn.execute(text("""
        ALTER TABLE registry_events_raw
        ADD CONSTRAINT uq_rg_ev UNIQUE (`transactionHash`);
    """))
    conn.execute(text("""
        ALTER TABLE mpe_events_raw
        ADD CONSTRAINT uq_mpe_ev UNIQUE (`transactionHash`);
    """))
    conn.execute(text("""
        ALTER TABLE rfai_events_raw
        ADD CONSTRAINT uq_rf_ev UNIQUE (`transactionHash`);
    """))
    conn.execute(text("""
        ALTER TABLE token_stake_events_raw
        ADD COLUMN uncle_block_no INT DEFAULT NULL AFTER block_no;
    """))
    conn.execute(text("""
        ALTER TABLE registry_events_raw
        ADD COLUMN uncle_block_no INT DEFAULT NULL AFTER block_no;
    """))
    conn.execute(text("""
        ALTER TABLE mpe_events_raw
        ADD COLUMN uncle_block_no INT DEFAULT NULL AFTER block_no;
    """))
    conn.execute(text("""
        ALTER TABLE rfai_events_raw
        ADD COLUMN uncle_block_no INT DEFAULT NULL AFTER block_no;
    """))


def downgrade():
    conn = op.get_bind()
    conn.execute(text("""
        ALTER TABLE token_stake_events_raw
        DROP INDEX uq_st_ev;
    """))
    conn.execute(text("""
        ALTER TABLE registry_events_raw
        DROP INDEX uq_rg_ev;
    """))
    conn.execute(text("""
        ALTER TABLE mpe_events_raw
        DROP INDEX uq_mpe_ev;
    """))
    conn.execute(text("""
        ALTER TABLE rfai_events_raw
        DROP INDEX uq_rf_ev;
    """))
    conn.execute(text("""
        ALTER TABLE token_stake_events_raw
        ADD CONSTRAINT uq_st_ev UNIQUE (`block_no`,`transactionHash`);
    """))
    conn.execute(text("""
        ALTER TABLE registry_events_raw
        ADD CONSTRAINT uq_rg_ev UNIQUE (`block_no`,`transactionHash`);
    """))
    conn.execute(text("""
        ALTER TABLE mpe_events_raw
        ADD CONSTRAINT uq_mpe_ev UNIQUE (`block_no`,`transactionHash`);
    """))
    conn.execute(text("""
        ALTER TABLE rfai_events_raw
        ADD CONSTRAINT uq_rf_ev UNIQUE (`block_no`,`transactionHash`);
    """))
    conn.execute(text("""
        ALTER TABLE token_stake_events_raw
        DROP COLUMN uncle_block_no;
    """))
    conn.execute(text("""
        ALTER TABLE registry_events_raw
        DROP COLUMN uncle_block_no;
    """))
    conn.execute(text("""
        ALTER TABLE mpe_events_raw
        DROP COLUMN uncle_block_no;
    """))
    conn.execute(text("""
        ALTER TABLE rfai_events_raw
        DROP COLUMN uncle_block_no;
    """))