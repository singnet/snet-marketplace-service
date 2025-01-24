"""rename to metadata_uri

Revision ID: fed330af2aa5
Revises: 3312b862c6cb
Create Date: 2025-01-21 13:15:38.145316

"""
from alembic import op
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'fed330af2aa5'
down_revision = '3312b862c6cb'
branch_labels = None
depends_on = None


def upgrade():
    # Rename column in the `organization` table
    op.alter_column(
        'organization',
        'metadata_ipfs_uri',
        new_column_name='metadata_uri',
        existing_type=mysql.VARCHAR(255),
        existing_nullable=True
    )

    # Rename column in the `organization_archive` table
    op.alter_column(
        'organization_archive',
        'metadata_ipfs_uri',
        new_column_name='metadata_uri',
        existing_type=mysql.VARCHAR(255),
        existing_nullable=True
    )

    op.execute("""
        UPDATE organization
        SET metadata_uri = CONCAT('ipfs://', metadata_uri)
        WHERE metadata_uri NOT LIKE 'ipfs://%' AND metadata_uri != '';
    """)

    op.execute("""
        UPDATE organization_archive
        SET metadata_uri = CONCAT('ipfs://', metadata_uri)
        WHERE metadata_uri NOT LIKE 'ipfs://%' AND metadata_uri != '';
    """)


def downgrade():
    # Revert column renaming in the `organization` table
    op.alter_column(
        'organization',
        'metadata_uri',
        new_column_name='metadata_ipfs_uri',
        existing_type=mysql.VARCHAR(255),
        existing_nullable=True
    )

    # Revert column renaming in the `organization_archive` table
    op.alter_column(
        'organization_archive',
        'metadata_uri',
        new_column_name='metadata_ipfs_uri',
        existing_type=mysql.VARCHAR(255),
        existing_nullable=True
    )

    op.execute("""
        UPDATE organization
        SET metadata_uri = SUBSTRING(metadata_uri, 8)
        WHERE metadata_uri LIKE 'ipfs://%';
    """)

    op.execute("""
        UPDATE organization_archive
        SET metadata_uri = SUBSTRING(metadata_uri, 8)
        WHERE metadata_uri LIKE 'ipfs://%';
    """)
