from common.logger import get_logger
from event_pubsub.repository import Repository
from event_pubsub.config import NETWORKS, EVENT_SUBSCRIPTIONS, NETWORK_ID
from event_pubsub.event_repository import EventRepository

from event_pubsub.listeners.listener_handlers import WebHookHandler
from event_pubsub.listeners.listener_handlers import LambdaArnHandler

logger = get_logger(__name__)


class EventListener(object):
    _connection = Repository(NETWORKS=NETWORKS, NETWORK_ID=NETWORK_ID)
    _event_repository = EventRepository(_connection)

    def __init__(self, repository=None):
        self.event_consumer_map = EventListener.initiate_event_subscription()

    def subscribe(self, event_names, event_consumer):
        for event in event_names:
            if event.get_name() in self.event_consumer_map:
                self.event_consumer_map[event] = event_consumer
            else:
                self.event_consumer_map[event] = [event_consumer]

        self.persist_event_subscription(event_names, event_consumer)

    @classmethod
    def initiate_event_subscription(cls):
        return EVENT_SUBSCRIPTIONS

    def _tranform_event_to_push(self, event):
        event['row_created'] = str(event['row_created'])
        event['row_updated'] = str(event['row_updated'])
        event['processed'] = 0
        push_event = {"data": event, "name": event["event"]}

        return push_event

    def _get_listener_handler(self, listener):
        if listener["type"] == "webhook":
            return WebHookHandler(listener["url"])
        elif listener["type"] == "lambda_arn":
            return LambdaArnHandler(listener["url"])

    def _publish_events(self, events):

        error_map = {}
        success_list = []

        for event in events:
            listeners = []
            if event['event'] in self.event_consumer_map:
                listeners = self.event_consumer_map[event['event']]
            for listener in listeners:
                push_event = self._tranform_event_to_push(event)
                logger.debug(f"pushing events {push_event} to listener {listener['url']}")
                try:
                    listener_handler = self._get_listener_handler(listener)
                    listener_handler.push_event(push_event)
                except Exception as e:
                    logger.exception(
                        f"Error while processing event with error {str(e)} for event {event} listener {listener['url']}")
                    error_map[event["row_id"]] = {"error_code": 500,
                                                  "error_message": f"for listener {listener['url']} got error {str(e)}"}
            success_list.append(event["row_id"])

        return error_map, success_list


class MPEEventListener(EventListener):
    EVENTS_LIMIT = 30

    def listen_and_publish_mpe_events(self):
        mpe_events = self._event_repository.read_mpe_events()
        logger.debug(f" read mpe_events to push to subscribers {mpe_events}")
        error_map, success_list = self._publish_events(mpe_events)
        # need to change it to batch update
        for row_id, error in error_map.items():
            self._event_repository.update_mpe_raw_events(1, row_id, error['error_code'], error['error_message'])

        for row_id in success_list:
            self._event_repository.update_mpe_raw_events(1, row_id, 200, "")

        return error_map, success_list


class RegistryEventListener(EventListener):
    EVENTS_LIMIT = 30

    def listen_and_publish_registry_events(self):
        registry_events = self._event_repository.read_registry_events()
        error_map, success_map = self._publish_events(registry_events)
        # need to change it to batch update
        for row_id, error in error_map.items():
            self._event_repository.update_registry_raw_events(1, row_id, error['error_code'], error['error_message'])

        for row_id in success_map:
            self._event_repository.update_registry_raw_events(1, row_id, 200, "")
        return error_map, success_map


class RFAIEventListener(EventListener):
    EVENTS_LIMIT = 30

    def listen_and_publish_rfai_events(self):
        rfai_events = self._event_repository.read_rfai_events()
        error_map, success_map = self._publish_events(rfai_events)
        # need to change is to batch update
        for row_id, error in error_map.items():
            self._event_repository.update_rfai_raw_events(1, row_id, error['error_code'], error['error_message'])

        for row_id in success_map:
            self._event_repository.update_rfai_raw_events(1, row_id, 200, "")

        return error_map, success_map


class TokenStakeEventListener(EventListener):
    EVENTS_LIMIT = 30

    def listen_and_publish_token_stake_events(self):
        token_stake_events = self._event_repository.read_token_stake_events()
        error_map, success_map = self._publish_events(token_stake_events)
        for row_id, error in error_map.items():
            logger.debug(f"Updated event process status for error {row_id} {error}")
            self._event_repository.update_token_stake_raw_events(1, row_id, error['error_code'], error['error_message'])

        for row_id in success_map:
            logger.debug(f"Updated event process status for success {row_id} ")
            self._event_repository.update_token_stake_raw_events(1, row_id, 200, "")
        return error_map, success_map
