"""consume_balance

Revision ID: 698ffdd6eeba
Revises: d8822b756c18
Create Date: 2019-11-14 13:17:05.359609

"""
from alembic import op
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision = '698ffdd6eeba'
down_revision = 'd8822b756c18'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    conn.execute(text("ALTER TABLE `mpe_channel` ADD `consumed_balance` DECIMAL NULL DEFAULT 0;"))


def downgrade():
    conn = op.get_bind()
    conn.execute(text("ALTER TABLE `mpe_channel` DROP COLUMN `consumed_balance`;"))
