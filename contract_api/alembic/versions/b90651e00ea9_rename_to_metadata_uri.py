"""rename to metadata_uri

Revision ID: b90651e00ea9
Revises: 4dd258579fce
Create Date: 2025-01-28 15:41:46.930616

"""
from alembic import op
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'b90651e00ea9'
down_revision = '4dd258579fce'
branch_labels = None
depends_on = None


def upgrade():
    # Rename column in the `service` table
    op.alter_column(
        'service',
        'ipfs_hash',
        new_column_name='hash_uri',
        existing_type=mysql.VARCHAR(255),
        existing_nullable=True
    )

    # Rename column in the `service_media` table
    op.alter_column(
        'service_media',
        'ipfs_url',
        new_column_name='hash_uri',
        existing_type=mysql.VARCHAR(255),
        existing_nullable=True
    )

    # Rename column in the `service_metadata` table
    op.alter_column(
        'service_metadata',
        'model_ipfs_hash',
        new_column_name='model_hash',
        existing_type=mysql.VARCHAR(255),
        existing_nullable=True
    )

    op.execute("""
        UPDATE service
        SET hash_uri = CONCAT('ipfs://', hash_uri)
        WHERE hash_uri NOT LIKE 'ipfs://%' AND hash_uri != '';
    """)

    op.execute("""
        UPDATE service_media
        SET hash_uri = CONCAT('ipfs://', hash_uri)
        WHERE hash_uri NOT LIKE 'ipfs://%' AND hash_uri != '';
    """)

    op.execute("""
        UPDATE service_metadata
        SET model_hash = CONCAT('ipfs://', model_hash)
        WHERE model_hash NOT LIKE 'ipfs://%' AND model_hash != '';
    """)


def downgrade():
    # Revert column renaming in the `service` table
    op.alter_column(
        'service',
        'hash_uri',
        new_column_name='ipfs_hash',
        existing_type=mysql.VARCHAR(255),
        existing_nullable=True
    )

    # Revert column renaming in the `service_media` table
    op.alter_column(
        'service_media',
        'hash_uri',
        new_column_name='ipfs_url',
        existing_type=mysql.VARCHAR(255),
        existing_nullable=True
    )

    # Revert column renaming in the `service_media` table
    op.alter_column(
        'service_media',
        'model_hash',
        new_column_name='model_ipfs_hash',
        existing_type=mysql.VARCHAR(255),
        existing_nullable=True
    )

    op.execute("""
        UPDATE service
        SET metadata_uri = SUBSTRING(metadata_uri, 8)
        WHERE metadata_uri LIKE 'ipfs://%';
    """)

    op.execute("""
        UPDATE service_media
        SET metadata_uri = SUBSTRING(metadata_uri, 8)
        WHERE metadata_uri LIKE 'ipfs://%';
    """)

    op.execute("""
        UPDATE service_metadata
        SET metadata_uri = SUBSTRING(metadata_uri, 8)
        WHERE metadata_uri LIKE 'ipfs://%';
    """)
