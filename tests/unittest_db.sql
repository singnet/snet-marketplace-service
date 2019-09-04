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
);
CREATE TABLE `wallet` (
  `row_id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(128) DEFAULT NULL,
  `address` varchar(256) NOT NULL,
  `status` bit(1) DEFAULT b'1',
  `row_created` timestamp NULL DEFAULT NULL,
  `row_updated` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`row_id`),
  UNIQUE KEY `uq_w_addr` (`address`),
  UNIQUE KEY `uq_w_usr` (`username`)
);
CREATE TABLE `user_service_vote` (
  `row_id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(128) NOT NULL,
  `org_id` varchar(128) NOT NULL,
  `service_id` varchar(128) NOT NULL,
  `rating` float(2,1) DEFAULT NULL,
  `row_created` timestamp NULL DEFAULT NULL,
  `row_updated` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`row_id`),
  UNIQUE KEY `unique_vote` (`username`,`org_id`,`service_id`)
);
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
);
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
  `ranking` int(4) DEFAULT '1',
  `contributors` varchar(128) DEFAULT NULL,
  `row_created` timestamp NULL DEFAULT NULL,
  `row_updated` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`row_id`),
  UNIQUE KEY `uq_srvc_mdata` (`org_id`,`service_id`),
  KEY `ServiceFK_idx` (`service_row_id`),
  CONSTRAINT `ServiceMdataFK` FOREIGN KEY (`service_row_id`) REFERENCES `service` (`row_id`) ON DELETE CASCADE
);
