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
INSERT INTO user (username, email, account_id, name, request_id, request_time_epoch)
VALUES("dummy_user@dummy.io", "dummy_user@dummy.io", 123456789, "test name", "abcdef123456", 9267489440);