"""service_ media_ table_ create

Revision ID: a5b328b4edec
Revises: 698ffdd6eeba
Create Date: 2021-01-11 19:01:28.355682

"""
from alembic import op
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision = 'a5b328b4edec'
down_revision = '698ffdd6eeba'
branch_labels = None
depends_on = None


def upgrade():
   conn = op.get_bind()
   conn.execute(text("""
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
            """)
    )

def downgrade():
 conn = op.get_bind()
 conn.execute(text("DROP TABLE service_media;"))