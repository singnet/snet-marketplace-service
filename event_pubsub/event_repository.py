from datetime import datetime

from common.logger import get_logger

logger = get_logger(__name__)


class EventRepository(object):
    EVENTS_LIMIT = 10

    def __init__(self, connection):
        self.connection = connection

    def read_rfai_events(self):
        self.connection.begin_transaction()
        try:
            query = 'select row_id, block_no, event, json_str, processed, transactionHash, logIndex, error_code, error_msg, row_updated, row_created from rfai_events_raw where processed = 0 order by block_no asc limit ' + str(
                EventRepository.EVENTS_LIMIT)
            events = self.connection.execute(query)
            self.connection.commit_transaction()
        except Exception as e:
            self.connection.rollback_transaction()
            raise e

        return events

    def read_registry_events(self):
        self.connection.begin_transaction()
        try:
            query = 'select * from registry_events_raw where processed = 0 order by block_no asc limit ' + str(
                EventRepository.EVENTS_LIMIT)
            events = self.connection.execute(query)
            self.connection.commit_transaction()
        except Exception as e:
            self.connection.rollback_transaction()
            raise e

        return events

    def read_mpe_events(self):
        self.connection.begin_transaction()
        try:
            query = 'select * from mpe_events_raw where processed = 0 order by block_no asc limit ' + str(
                EventRepository.EVENTS_LIMIT)
            events = self.connection.execute(query)
            self.connection.commit_transaction()
        except Exception as e:
            self.connection.rollback_transaction()
            raise e

        return events

    def read_token_stake_events(self):

        self.connection.begin_transaction()
        try:
            query = 'select * from token_stake_events_raw where processed = 0 order by block_no asc limit ' + str(
                EventRepository.EVENTS_LIMIT)
            events = self.connection.execute(query)
            self.connection.commit_transaction()
            return events
        except Exception as e:
            self.connection.rollback_transaction()
            raise e

    def update_mpe_raw_events(self, processed, row_id, error_code, error_message):
        try:
            self.connection.begin_transaction()
            update_events = 'UPDATE mpe_events_raw SET processed = %s , error_code = %s, error_msg = %s WHERE row_id = %s '
            update_events_reponse = self.connection.execute(update_events,
                                                            [processed, error_code, error_message, row_id])
            self.connection.commit_transaction()

        except Exception as e:
            self.connection.rollback_transaction()
            raise e

    def update_registry_raw_events(self, processed, row_id, error_code, error_message):
        try:
            self.connection.begin_transaction()
            update_events = 'UPDATE registry_events_raw SET processed = %s, error_code = %s, error_msg = %s WHERE row_id = %s '
            update_events_reponse = self.connection.execute(update_events,
                                                            [processed, error_code, error_message, row_id])
            self.connection.commit_transaction()

        except Exception as e:
            logger.exception(f"Error while updating the registry_raw_event {str(e)}")
            self.connection.rollback_transaction()
            raise e

    def update_token_stake_raw_events(self, processed, row_id, error_code, error_message):
        try:
            self.connection.begin_transaction()
            update_events = 'UPDATE token_stake_events_raw SET processed = %s, error_code = %s, error_msg = %s WHERE row_id = %s '
            update_events_response = self.connection.execute(update_events,
                                                             [processed, error_code, error_message, row_id])
            self.connection.commit_transaction()

        except Exception as e:
            logger.exception(f"Error while updating the token_stake_raw_event {str(e)}")
            self.connection.rollback_transaction()
            raise e

    def update_rfai_raw_events(self, processed, row_id, error_code, error_message):
        try:
            self.connection.begin_transaction()
            update_events = 'UPDATE rfai_events_raw SET processed = %s, error_code = %s, error_msg = %s WHERE row_id = %s '
            update_events_reponse = self.connection.execute(update_events,
                                                            [processed, error_code, error_message, row_id])
            self.connection.commit_transaction()

        except Exception as e:
            logger.exception(f"Error while updating the registry_raw_event {str(e)}")
            self.connection.rollback_transaction()
            raise e

    def insert_registry_event(self, block_number, event_name, json_str, processed, transaction_hash, log_index,
                              error_code, error_message):
        # insert into database here
        self.connection.begin_transaction()
        try:

            insert_query = "INSERT INTO registry_events_raw (block_no, event, json_str, processed, transactionHash, logIndex ,error_code,error_msg,row_updated,row_created) " \
                           "VALUES ( %s, %s, %s, %s, %s , %s, %s, %s, %s, %s ) " \
                           "ON DUPLICATE KEY UPDATE row_updated=%s "
            insert_params = [block_number, event_name, json_str, processed, transaction_hash, log_index, error_code,
                             error_message, datetime.utcnow(), datetime.utcnow(), datetime.utcnow()]

            query_response = self.connection.execute(insert_query, insert_params)
            self.connection.commit_transaction()
        except Exception as e:
            self.connection.rollback_transaction()
            raise e

    def insert_mpe_event(self, block_number, event_name, json_str, processed, transaction_hash, log_index, error_code,
                         error_message):
        # insert into database here
        self.connection.begin_transaction()
        try:
            insert_query = "Insert into mpe_events_raw (block_no, event, json_str, processed, transactionHash, logIndex ,error_code,error_msg,row_updated,row_created) " \
                           "VALUES ( %s, %s, %s, %s, %s , %s, %s, %s, %s, %s ) " \
                           "ON DUPLICATE KEY UPDATE row_updated=%s "
            insert_params = [block_number, event_name, json_str, processed, transaction_hash, log_index, error_code,
                             error_message, datetime.utcnow(), datetime.utcnow(), datetime.utcnow()]

            query_response = self.connection.execute(insert_query, insert_params)
            self.connection.commit_transaction()
        except Exception as e:
            self.connection.rollback_transaction()
            raise e

    def insert_rfai_event(self, block_number, event_name, json_str, processed, transaction_hash, log_index, error_code,
                          error_message):
        # insert into database here
        try:
            self.connection.begin_transaction()
            insert_query = "Insert into rfai_events_raw (block_no, event, json_str, processed, transactionHash, logIndex ,error_code,error_msg,row_updated,row_created) " \
                           "VALUES ( %s, %s, %s, %s, %s , %s, %s, %s, %s, %s ) " \
                           "ON DUPLICATE KEY UPDATE row_updated=%s "
            insert_params = [block_number, event_name, json_str, processed, transaction_hash, log_index, error_code,
                             error_message, datetime.utcnow(), datetime.utcnow(), datetime.utcnow()]

            query_response = self.connection.execute(insert_query, insert_params)
            self.connection.commit_transaction()
        except Exception as e:
            self.connection.rollback_transaction()
            raise e

    def insert_token_stake_event(self, block_number, event_name, json_str, processed, transaction_hash, log_index,
                                 error_code, error_message):
        # insert into database here
        self.connection.begin_transaction()
        try:
            insert_query = "Insert into token_stake_events_raw (block_no, event, json_str, processed, transactionHash, logIndex ,error_code,error_msg,row_updated,row_created) " \
                           "VALUES ( %s, %s, %s, %s, %s , %s, %s, %s, %s, %s ) " \
                           "ON DUPLICATE KEY UPDATE row_updated=%s "
            insert_params = [block_number, event_name, json_str, processed, transaction_hash, log_index, error_code,
                             error_message, datetime.utcnow(), datetime.utcnow(), datetime.utcnow()]

            query_response = self.connection.execute(insert_query, insert_params)
            self.connection.commit_transaction()
        except Exception as e:
            self.connection.rollback_transaction()
            raise e

    def read_last_read_block_number_for_event(self, event_type):
        self.connection.begin_transaction()
        try:
            read_query = "SELECT row_id, event_type, last_block_number, row_created, row_updated FROM  event_blocknumber_marker where event_type = %s"

            read_params = [event_type]
            result = self.connection.execute(read_query, read_params)
            self.connection.commit_transaction()

            return result[0]['last_block_number']


        except Exception as e:
            self.connection.rollback_transaction()
            raise e

    def update_last_read_block_number_for_event(self, event_type, last_block_number):
        self.connection.begin_transaction()
        try:
            update_query = "update event_blocknumber_marker set last_block_number = %s , row_updated = %s where event_type =%s "

            update_params = [last_block_number, datetime.utcnow(), event_type]
            result = self.connection.execute(update_query, update_params)
            self.connection.commit_transaction()
        except Exception as e:
            self.connection.rollback_transaction()
            raise e
