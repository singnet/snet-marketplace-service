-- common database schema across all networks

CREATE TABLE `registry_events_raw` (
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
  KEY `blk_no_idx` (`block_no`)
) ;

CREATE TABLE `mpe_events_raw` (
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
  KEY `blk_no_idx` (`block_no`)
) ;

CREATE TABLE `rfai_events_raw` (
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
  KEY `blk_no_idx` (`block_no`)
) ;



-- run after create_table.sql is processed
-- this script need to be processed before snet-event-consumer is run for the first time
-- field block_no Integer, replace starting block_no with start block no of the contract
INSERT INTO registry_events_raw (block_no, event, json_str, processed, transactionHash, logIndex, error_code, error_msg)
VALUES ( 0, "start", "", 1, "", -1, 0, "");

INSERT INTO mpe_events_raw (block_no, event, json_str, processed, transactionHash, logIndex, error_code, error_msg)
VALUES ( 0, "start", "", 1, "", -1, 0, "");

INSERT INTO rfai_events_raw (block_no, event, json_str, processed, transactionHash, logIndex, error_code, error_msg)
VALUES ( 0, "start", "", 1, "", -1, 0, "");















-- seed script for running unittest
-- -----------------------------------------
-- user : unittest_root
-- pwd  : unittest_pwd
-- host : 127.0.0.1
-- port : 3306
-- -----------------------------------------
CREATE DATABASE unittestdb;
GRANT ALL PRIVILEGES ON *.* to 'unittest_root'@'%' IDENTIFIED BY 'unittest_pwd' WITH GRANT OPTION;
USE unittestdb;

CREATE TABLE `organization` (
  `row_id` int(11) NOT NULL AUTO_INCREMENT,
  `org_id` varchar(256) NOT NULL,
  `organization_name` varchar(128) DEFAULT NULL,
  `owner_address` varchar(256) DEFAULT NULL,
  `row_created` timestamp NULL DEFAULT NULL,
  `row_updated` timestamp NULL DEFAULT NULL,
  `org_metadata_uri` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`row_id`),
  UNIQUE KEY `uq_org` (`org_id`)
) ;
INSERT INTO `organization` (`row_id`,`org_id`,`organization_name`,`owner_address`,`row_created`,`row_updated`) VALUES (2,'test-snet','test-snet','0xFF2a327ed1Ca40CE93F116C5d6646b56991c0ddE','2019-01-17 04:43:27','2019-01-17 04:43:44');



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
)




CREATE TABLE `service` (
  `row_id` int(11) NOT NULL AUTO_INCREMENT,
  `org_id` varchar(256) NOT NULL,
  `service_id` varchar(256) NOT NULL,
  `service_path` varchar(128) DEFAULT NULL,
  `ipfs_hash` varchar(256) DEFAULT NULL,
  `is_curated` tinyint(1) DEFAULT NULL,
  `row_created` timestamp NULL DEFAULT NULL,
  `row_updated` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`row_id`),
  UNIQUE KEY `uq_srvc` (`org_id`,`service_id`)
) ;
INSERT INTO `service` (`row_id`,`org_id`,`service_id`,`service_path`,`ipfs_hash`,`is_curated`,`row_created`,`row_updated`) VALUES (149,'test-snet','tests',NULL,'QmdcPZXYfYeiN5FcZDwy5rRSDKk19EoKEvGN6gjgB5FMzX',1,'2019-01-17 04:43:48','2019-01-17 04:43:48');

CREATE TABLE `service_metadata` (
  `row_id` int(11) NOT NULL AUTO_INCREMENT,
  `service_row_id` int(11) NOT NULL,
  `org_id` varchar(256) NOT NULL,
  `service_id` varchar(256) NOT NULL,
  `price_model` varchar(128) DEFAULT NULL,
  `price_in_cogs` decimal(19,8) DEFAULT NULL,
  `display_name` varchar(256) DEFAULT NULL,
  `description` varchar(1024) DEFAULT NULL,
  `url` varchar(256) DEFAULT NULL,
  `json` varchar(1024) DEFAULT NULL,
  `model_ipfs_hash` varchar(256) DEFAULT NULL,
  `encoding` varchar(128) DEFAULT NULL,
  `type` varchar(128) DEFAULT NULL,
  `mpe_address` varchar(256) DEFAULT NULL,
  `row_created` timestamp NULL DEFAULT NULL,
  `row_updated` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`row_id`),
  UNIQUE KEY `uq_srvc_mdata` (`org_id`,`service_id`),
  KEY `ServiceFK_idx` (`service_row_id`),
  CONSTRAINT `ServiceMdataFK` FOREIGN KEY (`service_row_id`) REFERENCES `service` (`row_id`) ON DELETE CASCADE
) ;
INSERT INTO `service_metadata` (`row_id`,`service_row_id`,`org_id`,`service_id`,`price_model`,`price_in_cogs`,`display_name`,`description`,`url`,`json`,`model_ipfs_hash`,`encoding`,`type`,`mpe_address`,`row_created`,`row_updated`) VALUES (146,149,'test-snet','tests','fixed_price',10000000.00000000,'Example1','','','','QmcxeRNsmm3qP5MTmQUrsWv8zgcGdnpHwNPWm72oQKL89D','proto','grpc','0x39f31Ac7B393fE2C6660b95b878FEB16eA8f3156','2019-01-17 04:43:48','2019-01-17 04:43:48');

CREATE TABLE `service_group` (
  `row_id` int(11) NOT NULL AUTO_INCREMENT,
  `service_row_id` int(11) NOT NULL,
  `org_id` varchar(256) NOT NULL,
  `service_id` varchar(256) NOT NULL,
  `group_id` varchar(256) NOT NULL,
  `group_name` varchar(128) DEFAULT NULL,
  `payment_address` varchar(256) DEFAULT NULL,
  `row_created` timestamp NULL DEFAULT NULL,
  `row_updated` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`row_id`),
  UNIQUE KEY `uq_srvc_grp` (`org_id`,`service_id`,`group_id`),
  KEY `ServiceFK_idx` (`service_row_id`),
  CONSTRAINT `ServiceGrpFK` FOREIGN KEY (`service_row_id`) REFERENCES `service` (`row_id`) ON DELETE CASCADE
) ;
INSERT INTO `service_group` (`row_id`,`service_row_id`,`org_id`,`service_id`,`group_id`,`group_name`,`payment_address`,`row_created`,`row_updated`) VALUES (149,149,'test-snet','tests','7nnoltEWnwv9w1qRE/Vym/rWiCXqeRQC7s8p0SlkjgQ=','default_group','0x3b2b3C2e2E7C93db335E69D827F3CC4bC2A2A2cB','2019-01-17 04:43:48','2019-01-17 04:43:48');

CREATE TABLE `service_endpoint` (
  `row_id` int(11) NOT NULL AUTO_INCREMENT,
  `service_row_id` int(11) NOT NULL,
  `org_id` varchar(256) NOT NULL,
  `service_id` varchar(256) NOT NULL,
  `group_id` varchar(256) NOT NULL,
  `endpoint` varchar(256) DEFAULT NULL,
  `row_created` timestamp NULL DEFAULT NULL,
  `row_updated` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`row_id`),
  KEY `ServiceFK_idx` (`service_row_id`),
  CONSTRAINT `ServiceEndpt` FOREIGN KEY (`service_row_id`) REFERENCES `service` (`row_id`) ON DELETE CASCADE
) ;
INSERT INTO `service_endpoint` (`row_id`,`service_row_id`,`org_id`,`service_id`,`group_id`,`endpoint`,`row_created`,`row_updated`) VALUES (129,149,'test-snet','tests','7nnoltEWnwv9w1qRE/Vym/rWiCXqeRQC7s8p0SlkjgQ=','localhost:8080','2019-01-17 04:43:48','2019-01-17 04:43:48');

CREATE TABLE `service_tags` (
  `row_id` int(11) NOT NULL AUTO_INCREMENT,
  `service_row_id` int(11) NOT NULL,
  `org_id` varchar(256) NOT NULL,
  `service_id` varchar(256) DEFAULT NULL,
  `tag_name` varchar(128) DEFAULT NULL,
  `row_created` timestamp NULL DEFAULT NULL,
  `row_updated` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`row_id`),
  UNIQUE KEY `uq_srvc_tag` (`org_id`, `service_id`, `tag_name`),
  KEY `ServiceFK_idx` (`service_row_id`),
  CONSTRAINT `ServiceFK` FOREIGN KEY (`service_row_id`) REFERENCES `service` (`row_id`) ON DELETE CASCADE
) ;
INSERT INTO `service_tags` (`row_id`,`service_row_id`,`org_id`,`service_id`,`tag_name`,`row_created`,`row_updated`) VALUES (18,149,'test-snet','tests','test-tag1','2019-01-17 12:03:07','2019-01-17 12:03:07');
INSERT INTO `service_tags` (`row_id`,`service_row_id`,`org_id`,`service_id`,`tag_name`,`row_created`,`row_updated`) VALUES (19,149,'test-snet','tests','test-tag2','2019-01-17 12:03:07','2019-01-17 12:03:07');

CREATE TABLE `members` (
  `row_id` int(11) NOT NULL AUTO_INCREMENT,
  `org_id` varchar(256) NOT NULL,
  `member` varchar(128) NOT NULL,
  `row_created` timestamp NULL DEFAULT NULL,
  `row_updated` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`row_id`),
  KEY `MembersFK_idx` (`org_id`),
  CONSTRAINT `MembersFK` FOREIGN KEY (`org_id`) REFERENCES `organization` (`org_id`) ON DELETE CASCADE
) ;

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
INSERT INTO `mpe_channel` (`row_id`,`channel_id`,`sender`,`recipient`,`groupId`,`balance_in_cogs`,`pending`,`nonce`,`expiration`,`signer`,`row_created`,`row_updated`) VALUES (321,43,'0xFF2a327ed1Ca40CE93F116C5d6646b56991c0ddE','0x3b2b3C2e2E7C93db335E69D827F3CC4bC2A2A2cB','7nnoltEWnwv9w1qRE/Vym/rWiCXqeRQC7s8p0SlkjgQ=',10.00000000,0.00000000,0,11000000,'0xFF2a327ed1Ca40CE93F116C5d6646b56991c0ddE','2019-01-16 14:46:07','2019-01-16 14:46:08');

 CREATE TABLE `user_service_vote` (
  `row_id` int(11) NOT NULL AUTO_INCREMENT,
  `user_address` varchar(256) NOT NULL,
  `org_id` varchar(128) NOT NULL,
  `service_id` varchar(128) NOT NULL,
  `vote` int(1) NOT NULL,
  `row_created` timestamp NULL DEFAULT NULL,
  `row_updated` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`row_id`),
  UNIQUE KEY `unique_vote` (`user_address`,`org_id`,`service_id`)
) ;

CREATE TABLE `user_service_feedback` (
  `row_id` int(11) NOT NULL AUTO_INCREMENT,
  `user_address` varchar(256) NOT NULL,
  `org_id` varchar(128) NOT NULL,
  `service_id` varchar(128) NOT NULL,
  `comment` varchar(1024) DEFAULT NULL,
  `row_created` timestamp NULL DEFAULT NULL,
  `row_updated` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`row_id`)
);

CREATE TABLE `service_status` (
  `row_id` int(11) NOT NULL AUTO_INCREMENT,
  `service_row_id` int(11) DEFAULT NULL,
  `org_id` varchar(256) DEFAULT NULL,
  `service_id` varchar(256) DEFAULT NULL,
  `group_id` varchar(256) DEFAULT NULL,
  `endpoint` varchar(256) DEFAULT NULL,
  `is_available` bit(1) DEFAULT NULL,
  `last_check_timestamp` timestamp NULL DEFAULT NULL,
  `row_created` timestamp NULL DEFAULT NULL,
  `row_updated` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`row_id`),
  KEY `ServiceStatusFK_idx` (`service_row_id`),
  CONSTRAINT `ServiceStatusFK` FOREIGN KEY (`service_row_id`) REFERENCES `service` (`row_id`) ON DELETE CASCADE
) ;
INSERT INTO `service_status` (`row_id`,`service_row_id`,`org_id`,`service_id`,`group_id`,`endpoint`,`is_available`,`last_check_timestamp`,`row_created`,`row_updated`) VALUES (28,149,'test-snet','tests','7nnoltEWnwv9w1qRE/Vym/rWiCXqeRQC7s8p0SlkjgQ=','localhost:8080',1,'2019-01-17 06:25:19','2019-01-17 06:25:19','2019-01-17 11:55:19');

