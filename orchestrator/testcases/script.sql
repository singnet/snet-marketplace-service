INSERT INTO transaction_history (username, order_id, order_type, raw_payment_data, status, row_created, row_updated)
        VALUES ('dummy1@dummy.io', 'cb736cfa-dae4-11e9-9769-26327914c219', 'TOP_UP', '{}', 'PAYMENT_INITIATION_FAILED', CURRENT_TIMESTAMP() - 150000, CURRENT_TIMESTAMP());
INSERT INTO transaction_history (username, order_id, order_type, raw_payment_data, status, row_created, row_updated)
        VALUES ('dummy2@dummy.io', 'db736cfa-dae4-11e9-9769-26327914c219', 'CREATE_CHANNEL', '{}', 'PAYMENT_INITIATION_FAILED', CURRENT_TIMESTAMP() - 150000, CURRENT_TIMESTAMP());
INSERT INTO transaction_history (username, order_id, order_type, raw_payment_data, status, row_created, row_updated)
        VALUES ('dummy3@dummy.io', 'eb736cfa-dae4-11e9-9769-26327914c219', 'CREATE_WALLET_AND_CHANNEL', '{}', 'PAYMENT_INITIATION_FAILED', CURRENT_TIMESTAMP() - 150000, CURRENT_TIMESTAMP());
INSERT INTO transaction_history (username, order_id, order_type, raw_payment_data, status, row_created, row_updated)
        VALUES ('dummy4@dummy.io', 'Fb736cfa-dae4-11e9-9769-26327914c219', 'CREATE_WALLET_AND_CHANNEL', '{}', 'PAYMENT_INITIATION_FAILED', CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP());
