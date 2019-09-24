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
CREATE TABLE `wallet` (
  `row_id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(128) DEFAULT NULL,
  `address` varchar(256) NOT NULL,
  `is_default` bit(1) DEFAULT b'0',
  `type` varchar(128) DEFAULT NULL,
  `status` bit(1) DEFAULT b'1',
  `created_by` varchar(256) DEFAULT NULL,
  `row_created` timestamp NULL DEFAULT NULL,
  `row_updated` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`row_id`),
  UNIQUE KEY `uq_w_addr` (`username`, `address`)
);
-- -----------------------------------------
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
-- -----------------------------------------
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
-- -----------------------------------------
