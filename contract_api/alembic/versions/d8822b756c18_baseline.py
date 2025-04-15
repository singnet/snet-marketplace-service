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
            CREATE TABLE `mpe_channel` (
              `row_id` int(11) NOT NULL AUTO_INCREMENT,
              `channel_id` int(11) NOT NULL,
              `sender` varchar(128) NOT NULL,
              `recipient` varchar(128) NOT NULL,
              `groupId` varchar(128) NOT NULL,
              `balance_in_cogs` decimal(19,8) DEFAULT NULL,
              `pending` decimal(19,8) DEFAULT NULL,
              `nonce` int(11) DEFAULT NULL,
              `expiration` bigint(20) DEFAULT NULL,
              `signer` varchar(256) NOT NULL,
              `row_created` timestamp NULL DEFAULT NULL,
              `row_updated` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
              PRIMARY KEY (`row_id`),
              UNIQUE KEY `uq_channel` (`channel_id`, `sender`, `recipient`, `groupId`)
            ) ;
            """))

    conn.execute(text("""

            CREATE TABLE `organization` (
              `row_id` int(11) NOT NULL AUTO_INCREMENT,
              `org_id` varchar(128) NOT NULL,
              `organization_name` varchar(128) DEFAULT NULL,
              `owner_address` varchar(256) DEFAULT NULL,
              `org_metadata_uri` varchar(128) DEFAULT NULL,
              `org_email` varchar(128) DEFAULT NULL,
              `org_assets_url` json DEFAULT NULL,
              `row_created` timestamp NULL DEFAULT NULL,
              `row_updated` timestamp NULL DEFAULT NULL,
              `description` varchar(256) DEFAULT NULL,
              `assets_hash` json DEFAULT NULL,
              `contacts` json DEFAULT NULL,
              PRIMARY KEY (`row_id`),
              UNIQUE KEY `uq_org` (`org_id`)
            )
        """))
    conn.execute(text("""
            CREATE TABLE `org_group` (
              `row_id` int(11) NOT NULL AUTO_INCREMENT,
              `org_id` varchar(128) NOT NULL,
              `group_id` varchar(128) DEFAULT NULL,
              `group_name` varchar(128) DEFAULT NULL,
              `payment` json DEFAULT NULL,
              `row_created` timestamp NULL DEFAULT NULL,
              `row_updated` timestamp NULL DEFAULT NULL,
              PRIMARY KEY (`row_id`),
              UNIQUE KEY `uq_org_grp` (`org_id`,`group_id`)
            ) ;
        """))
    conn.execute(text("""
            CREATE TABLE `members` (
              `row_id` int(11) NOT NULL AUTO_INCREMENT,
              `org_id` varchar(128) NOT NULL,
              `member` varchar(128) NOT NULL,
              `row_created` timestamp NULL DEFAULT NULL,
              `row_updated` timestamp NULL DEFAULT NULL,
              PRIMARY KEY (`row_id`),
              KEY `MembersFK_idx` (`org_id`),
              CONSTRAINT `MembersFK` FOREIGN KEY (`org_id`) REFERENCES `organization` (`org_id`) ON DELETE CASCADE
            ) ;
        """))

    conn.execute(text("""
            CREATE TABLE `service` (
              `row_id` int(11) NOT NULL AUTO_INCREMENT,
              `org_id` varchar(128) NOT NULL,
              `service_id` varchar(128) NOT NULL,
              `service_path` varchar(128) DEFAULT NULL,
              `ipfs_hash` varchar(128) DEFAULT NULL,
              `is_curated` tinyint(1) DEFAULT NULL,
              `service_email` varchar(128) DEFAULT NULL,
              `row_created` timestamp NULL DEFAULT NULL,
              `row_updated` timestamp NULL DEFAULT NULL,
              PRIMARY KEY (`row_id`),
              UNIQUE KEY `uq_srvc` (`org_id`,`service_id`)
            ) ;
    """))
    conn.execute(text("""
            CREATE TABLE `service_metadata` (
              `row_id` int(11) NOT NULL AUTO_INCREMENT,
              `service_row_id` int(11) NOT NULL,
              `org_id` varchar(128) NOT NULL,
              `service_id` varchar(128) NOT NULL,
              `display_name` varchar(256) DEFAULT NULL,
              `description` varchar(1024) DEFAULT NULL,
              `short_description` varchar(1024) DEFAULT NULL,
              `url` varchar(256) DEFAULT NULL,
              `json` varchar(1024) DEFAULT NULL,
              `model_ipfs_hash` varchar(256) DEFAULT NULL,
              `encoding` varchar(128) DEFAULT NULL,
              `type` varchar(128) DEFAULT NULL,
              `mpe_address` varchar(256) DEFAULT NULL,
              `assets_url` json DEFAULT NULL,
              `assets_hash` json DEFAULT NULL,
              `service_rating` json DEFAULT NULL,
              `ranking` int(4) DEFAULT '1',
              `contributors` json DEFAULT NULL,
              `row_created` timestamp NULL DEFAULT NULL,
              `row_updated` timestamp NULL DEFAULT NULL,
              PRIMARY KEY (`row_id`),
              UNIQUE KEY `uq_srvc_mdata` (`org_id`,`service_id`),
              KEY `ServiceFK_idx` (`service_row_id`),
              CONSTRAINT `ServiceMdataFK` FOREIGN KEY (`service_row_id`) REFERENCES `service` (`row_id`) ON DELETE CASCADE
            )
       """))
    conn.execute(text("""
            CREATE TABLE `service_group` (
              `row_id` int(11) NOT NULL AUTO_INCREMENT,
              `service_row_id` int(11) NOT NULL,
              `org_id` varchar(128) NOT NULL,
              `service_id` varchar(128) NOT NULL,
              `free_call_signer_address` varchar(256),
              `free_calls` int(11),
              `group_id` varchar(256) NOT NULL,
              `group_name` varchar(128) NOT NULL,
              `pricing` json DEFAULT NULL,
              `row_created` timestamp NULL DEFAULT NULL,
              `row_updated` timestamp NULL DEFAULT NULL,
              PRIMARY KEY (`row_id`),
              UNIQUE KEY `uq_srvc_grp` (`org_id`,`service_id`,`group_id`),
              KEY `ServiceFK_idx` (`service_row_id`),
              CONSTRAINT `ServiceGrpFK` FOREIGN KEY (`service_row_id`) REFERENCES `service` (`row_id`) ON DELETE CASCADE
            ) ;
       """))

    conn.execute(text("""
        CREATE TABLE `service_endpoint` (
          `row_id` int(11) NOT NULL AUTO_INCREMENT,
          `service_row_id` int(11) NOT NULL,
          `org_id` varchar(128) NOT NULL,
          `service_id` varchar(128) NOT NULL,
          `group_id` varchar(256) NOT NULL,
          `endpoint` varchar(256) DEFAULT NULL,
          `is_available` bit(1) DEFAULT NULL,
          `last_check_timestamp` timestamp NULL DEFAULT NULL,
          `next_check_timestamp` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
          `failed_status_count` int(2) DEFAULT '1',
          `row_created` timestamp NULL DEFAULT NULL,
          `row_updated` timestamp NULL DEFAULT NULL,
          PRIMARY KEY (`row_id`),
          KEY `ServiceFK_idx` (`service_row_id`),
          CONSTRAINT `ServiceEndpt` FOREIGN KEY (`service_row_id`) REFERENCES `service` (`row_id`) ON DELETE CASCADE
        );
    """))
    conn.execute(text("""
            CREATE TABLE `service_tags` (
              `row_id` int(11) NOT NULL AUTO_INCREMENT,
              `service_row_id` int(11) NOT NULL,
              `org_id` varchar(128) NOT NULL,
              `service_id` varchar(128) DEFAULT NULL,
              `tag_name` varchar(128) DEFAULT NULL,
              `row_created` timestamp NULL DEFAULT NULL,
              `row_updated` timestamp NULL DEFAULT NULL,
              PRIMARY KEY (`row_id`),
              UNIQUE KEY `uq_srvc_tag` (`org_id`, `service_id`, `tag_name`),
              KEY `ServiceFK_idx` (`service_row_id`),
              CONSTRAINT `ServiceFK` FOREIGN KEY (`service_row_id`) REFERENCES `service` (`row_id`) ON DELETE CASCADE
            ) ;
       """))
    conn.execute(text("""
            CREATE TABLE `daemon_token` (
              `row_id` int(11) NOT NULL AUTO_INCREMENT,
              `daemon_id` varchar(256) NOT NULL,
              `token` varchar(128) NOT NULL,
              `expiration` varchar(256) NOT NULL,
              `row_created` timestamp NULL DEFAULT NULL,
              `row_updated` timestamp NULL DEFAULT NULL,
              PRIMARY KEY (`row_id`),
              KEY `daemon_id_idx` (`daemon_id`),
              UNIQUE KEY `uq_daemon_id` (`daemon_id`)
            ) ;
        """))


def downgrade():
    conn = op.get_bind()
    conn.execute(text("""
                drop table mpe_channel
            """
    ))

