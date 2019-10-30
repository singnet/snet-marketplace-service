from datetime import datetime


class EventRepository(object):
    EVENTS_LIMIT = 10

    def __init__(self, connection):
        self.connection = connection

    def read_registry_events(self):
        query = 'select * from registry_events_raw where processed = 0 order by block_no asc limit ' + str(
            EventRepository.EVENTS_LIMIT)
        events = self.connection.execute(query)
        return events

    def read_mpe_events(self):
        query = 'select * from mpe_events_raw where processed = 0 order by block_no asc limit ' + str(
            EventRepository.EVENTS_LIMIT)
        events = self.connection.execute(query)
        return events

    def update_mpe_raw_events(self, row_id, error_code, error_message):
        try:
            update_events = 'UPDATE mpe_events_raw SET processed = 1, error_code = %s, error_msg = %s WHERE row_id = %s '
            update_events_reponse = self.connection.execute(update_events, [error_code, error_message, row_id])

        except Exception as e:
            self.connection.rollback_transaction()

    def update_registry_raw_events(self, row_id, error_code, error_message):
        try:
            update_events = 'UPDATE registry_events_raw SET processed = 1, error_code = %s, error_msg = %s WHERE row_id = %s '
            update_events_reponse = self.connection.execute(update_events, [error_code, error_message, row_id])

        except Exception as e:
            self.connection.rollback_transaction()

    def insert_registry_event(self, block_number, event_name, json_str, processed, transaction_hash, log_index,
                              error_code, error_message):
        # insert into database here
        insert_query = "Insert into registry_events_raw (block_no, event, json_str, processed, transactionHash, logIndex ,error_code,error_msg,row_updated,row_created) " \
                       "VALUES ( %s, %s, %s, %s, %s , %s, %s, %s, %s, %s ) "
        insert_params = [block_number, event_name, json_str, processed, transaction_hash, log_index, error_code,
                         error_message,
                         datetime.utcnow(), datetime.utcnow()]

        query_reponse = self.connection.execute(insert_query, insert_params)

    def insert_mpe_event(self, block_number, event_name, json_str, processed, transaction_hash, log_index, error_code,
                         error_message):
        # insert into database here
        insert_query = "Insert into mpe_events_raw (block_no, event, json_str, processed, transactionHash, logIndex ,error_code,error_msg,row_updated,row_created) " \
                       "VALUES ( %s, %s, %s, %s, %s , %s, %s, %s, %s, %s ) "
        insert_params = [block_number, event_name, json_str, processed, transaction_hash, log_index, error_code,
                         error_message,
                         datetime.utcnow(), datetime.utcnow()]

        query_reponse = self.connection.execute(insert_query, insert_params)

    def read_last_read_block_number_for_event(self, event_type):
        read_query = "SELECT row_id, event_type, last_block_number, row_created, row_updated FROM  event_blocknumber_marker where event_type = %s"

        read_params = [event_type]
        result = self.connection.execute(read_query, read_params)

        return result[0]['last_block_number']

    def update_last_read_block_number_for_event(self, event_type, last_block_number):
        update_query = "update event_blocknumber_marker set last_block_number = %s where event_type =%s "

        update_params = [last_block_number, event_type]
        result = self.connection.execute(update_query, update_params)
