"""service media table

Revision ID: 9c30245d4716
Revises: 698ffdd6eeba
Create Date: 2021-01-11 16:29:32.234495

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9c30245d4716'
down_revision = '698ffdd6eeba'
branch_labels = None
depends_on = None


def upgrade():
   conn = op.get_bind()
   conn.execute("""
            CREATE TABLE `service_media` (
            `row_id` int NOT NULL AUTO_INCREMENT,
            `org_id` varchar(100) NOT NULL,
            `service_id` varchar(100) NOT NULL,
            `url` varchar(512) DEFAULT NULL,
            `order` int DEFAULT NULL,
            `file_type` varchar(100) DEFAULT NULL,
            `asset_type` varchar(100) DEFAULT NULL,
            `alt_text` varchar(100) DEFAULT NULL,
            `created_on` timestamp NULL DEFAULT NULL,
            `updated_on` timestamp NULL DEFAULT NULL,
            `ipfs_url` varchar(512) DEFAULT NULL,
            `service_row_id` int DEFAULT NULL,
            PRIMARY KEY (`row_id`),
            KEY `ServiceMedisFK` (`service_row_id`),
            CONSTRAINT `ServiceMedisFK` FOREIGN KEY (`service_row_id`) REFERENCES `service` (`row_id`) ON DELETE CASCADE
            );
            """
    )

def downgrade():
 conn = op.get_bind()
 conn.execute("DROP TABLE service_media;")
