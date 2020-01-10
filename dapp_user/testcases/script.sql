INSERT INTO user (row_id, username, email, account_id, name, request_id, request_time_epoch)
VALUES(1, "dummy_user@dummy.io", "dummy_user@dummy.io", 123456789, "test name", "abcdef123456", 9267489440);
INSERT INTO user (row_id, username, email, account_id, name, request_id, request_time_epoch)
VALUES(10, "dummy_name@dummy.io", "dummy_name@dummy.io", 133456789, "test name", "bscdef123456", 9367489440);
INSERT INTO user_preference
(row_id, user_row_id, preference_type, communication_type, source, opt_out_reason, status, created_on, updated_on)
VALUES(1111, 10, 'FEATURE_RELEASE', 'SMS', 'PUBLISHER_DAPP', NULL, 0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);