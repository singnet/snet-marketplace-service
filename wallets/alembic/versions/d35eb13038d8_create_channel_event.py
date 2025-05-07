"""create channel event

Revision ID: d35eb13038d8
Revises: d8822b756c18
Create Date: 2019-11-18 15:42:14.202820

"""
from alembic import op
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision = 'd35eb13038d8'
down_revision = 'd8822b756c18'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    conn.execute(text("""
            CREATE TABLE `create_channel_event` (
              `row_id` int NOT NULL AUTO_INCREMENT,
              `payload` json NOT NULL,
              `status` varchar(256) NOT NULL,
              `row_created` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
              `row_updated` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
              PRIMARY KEY (`row_id`)
           );
        """))


def downgrade():
    conn = op.get_bind()
    conn.execute(text('DROP TABLE create_channel_event'))
