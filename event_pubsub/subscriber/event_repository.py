from datetime import datetime
import json

from event_pubsub.consumers.marketplace_event_consumer.dao.repository import Repository


class  EventRepository(Repository):
    EVENTS_LIMIT=10
    def __init__(self, connection):

        super().__init__(connection)
        self.connection = connection


    def read_registry_events(self):
        query = 'select * from registry_events_raw where processed = 0 order by block_no asc limit ' + EventRepository.EVENTS_LIMIT
        events = self.connection.execute(query)
        return events

    def read_mpe_events(self):
        query = 'select * from mpe_events_raw where processed = 0 order by block_no asc limit ' + EventRepository.EVENTS_LIMIT
        events = self.connection.execute(query)
        return events

    def update_raw_events(self, row_id, type, error_code, error_message):
        try:
            if type == 'REG':
                update_events = 'UPDATE registry_events_raw SET processed = 1, error_code = %s, error_msg = %s WHERE row_id = %s '
            elif type == 'MPE':
                update_events = 'UPDATE mpe_events_raw SET processed = 1, error_code = %s, error_msg = %s WHERE row_id = %s '
            update_events_reponse = self.connection.execute(update_events, [error_code, error_message, row_id])

        except Exception as e:
            self.connection.rollback_transaction()
