-- common database schema across all networks
-- -----------------------------------------
-- Contract Level

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
-- -----------------------------------------
CREATE TABLE `organization` (
  `row_id` int(11) NOT NULL AUTO_INCREMENT,
  `org_id` varchar(128) NOT NULL,
  `organization_name` varchar(128) DEFAULT NULL,
  `owner_address` varchar(256) DEFAULT NULL,
  `org_metadata_uri` varchar(128) DEFAULT NULL,
  `org_email` varchar(128) DEFAULT NULL,
  `row_created` timestamp NULL DEFAULT NULL,
  `row_updated` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`row_id`),
  UNIQUE KEY `uq_org` (`org_id`)
) ;
-- -----------------------------------------
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
-- -----------------------------------------
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
-- -----------------------------------------
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
-- -----------------------------------------
CREATE TABLE `service_metadata` (
  `row_id` int(11) NOT NULL AUTO_INCREMENT,
  `service_row_id` int(11) NOT NULL,
  `org_id` varchar(128) NOT NULL,
  `service_id` varchar(128) NOT NULL,
  `display_name` varchar(256) DEFAULT NULL,
  `description` varchar(1024) DEFAULT NULL,
  `url` varchar(256) DEFAULT NULL,
  `json` varchar(1024) DEFAULT NULL,
  `model_ipfs_hash` varchar(256) DEFAULT NULL,
  `encoding` varchar(128) DEFAULT NULL,
  `type` varchar(128) DEFAULT NULL,
  `mpe_address` varchar(256) DEFAULT NULL,
  `assets_url` json DEFAULT NULL,
  `assets_hash` json DEFAULT NULL,
  `service_rating` json DEFAULT NULL,
  `ranking` int(4) DEFAULT 1,
  `contributors` varchar(128) DEFAULT NULL,
  `row_created` timestamp NULL DEFAULT NULL,
  `row_updated` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`row_id`),
  UNIQUE KEY `uq_srvc_mdata` (`org_id`,`service_id`),
  KEY `ServiceFK_idx` (`service_row_id`),
  CONSTRAINT `ServiceMdataFK` FOREIGN KEY (`service_row_id`) REFERENCES `service` (`row_id`) ON DELETE CASCADE
) ;
-- -----------------------------------------
CREATE TABLE `service_group` (
  `row_id` int(11) NOT NULL AUTO_INCREMENT,
  `service_row_id` int(11) NOT NULL,
  `org_id` varchar(128) NOT NULL,
  `service_id` varchar(128) NOT NULL,
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
-- -----------------------------------------
CREATE TABLE `service_endpoint` (
  `row_id` int(11) NOT NULL AUTO_INCREMENT,
  `service_row_id` int(11) NOT NULL,
  `org_id` varchar(128) NOT NULL,
  `service_id` varchar(128) NOT NULL,
  `group_id` varchar(256) NOT NULL,
  `endpoint` varchar(256) DEFAULT NULL,
  `is_available` bit(1) DEFAULT b'1',
  `last_check_timestamp` timestamp NULL DEFAULT NULL,
  `row_created` timestamp NULL DEFAULT NULL,
  `row_updated` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`row_id`),
  KEY `ServiceFK_idx` (`service_row_id`),
  CONSTRAINT `ServiceEndpt` FOREIGN KEY (`service_row_id`) REFERENCES `service` (`row_id`) ON DELETE CASCADE
) ;
-- -----------------------------------------
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
-- -----------------------------------------
-- User Level
CREATE TABLE `user` (
  `row_id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(128) NOT NULL,
  `account_id` varchar(128) NOT NULL,
  `name` varchar(128) NOT NULL,
  `email` varchar(128) NOT NULL,
  `email_verified` bit(1) DEFAULT b'0',
  `email_alerts` bit(1) DEFAULT b'0',
  `status` bit(1) DEFAULT b'0',
  `request_id` varchar(128) NOT NULL,
  `request_time_epoch` varchar(128) NOT NULL,
  `is_terms_accepted` bit(1) DEFAULT b'0',
  `row_created` timestamp NULL DEFAULT NULL,
  `row_updated` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`row_id`),
  UNIQUE KEY `uq_usr` (`username`),
  UNIQUE KEY `uq_usr_email` (`email`)
) ;
-- -----------------------------------------
 CREATE TABLE `user_service_vote` (
  `row_id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(128) NOT NULL,
  `org_id` varchar(128) NOT NULL,
  `service_id` varchar(128) NOT NULL,
  `rating` float(2,1) DEFAULT NULL,
  `row_created` timestamp DEFAULT NULL,
  `row_updated` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`row_id`),
  UNIQUE KEY `unique_vote` (`username`,`org_id`,`service_id`)
) ;
-- -----------------------------------------
CREATE TABLE `user_service_feedback` (
  `row_id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(128) NOT NULL,
  `org_id` varchar(128) NOT NULL,
  `service_id` varchar(128) NOT NULL,
  `comment` varchar(1024) DEFAULT NULL,
  `row_created` timestamp NULL DEFAULT NULL,
  `row_updated` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`row_id`)
);
-- -----------------------------------------
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
-- -----------------------------------------
CREATE TABLE `service_status_stats` (
       `row_id` int(11) NOT NULL AUTO_INCREMENT,
       `org_id` varchar(128) NOT NULL,
       `service_id` varchar(128) NOT NULL,
       `previous_state` varchar(128) NOT NULL,
       `current_state` varchar(128) NOT NULL,
       `row_created` timestamp NULL DEFAULT NULL,
       `row_updated` timestamp NULL DEFAULT NULL,
       PRIMARY KEY (`row_id`)
     ) ;
-----------------------------------------------
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
) ENGINE=InnoDB AUTO_INCREMENT=162 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;