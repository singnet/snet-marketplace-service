from event_pubsub.repository import Repository
from event_pubsub.config import NETWORKS, EVENT_SUBSCRIPTIONS
from event_pubsub.event_repository import EventRepository

from event_pubsub.subscriber.listener_handlers import WebHookHandler
from subscriber.listener_handlers import LambdaArnHandler


class EventSubscriber(object):
    EVENTS_LIMIT = 30

    connection = Repository(NETWORKS=NETWORKS)
    event_repository = EventRepository(connection)

    def __init__(self, repository=None):
        self.event_consumer_map = EventSubscriber.initiate_event_subscription()

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

    def listen_and_publish_registry_events(self):
        registry_events = self.event_repository.read_registry_events()
        error_map = self.publish_events(registry_events)
        # need to change it to batch update
        for row_id, error in error_map.items():
            self.event_repository.update_registry_raw_events(row_id, error['error_code'], error['error_message'])

    def listen_and_publish_mpe_events(self):
        mpe_events = self.event_repository.read_mpe_events()
        error_map = self.publish_events(mpe_events)
        # need to change it to batch update
        for row_id, error in error_map:
            self.event_repository.update_mpe_raw_events(row_id, error['error_code'], error['error_message'])

    def publish_events(self, events):

        error_map = {}

        for event in events:
            listeners = []
            if event['event'] in self.event_consumer_map:
                listeners = self.event_consumer_map[event['event']]
            for listener in listeners:
                push_event = {"data": event, "name": event["event"]}
                try:
                    if listener["type"] == "webhook":
                        WebHookHandler(listener["url"], push_event).push_event()
                    elif listener["type"] == "lambda_arn":
                        LambdaArnHandler(listener["lambda_arn"],push_event).push_event()
                except Exception as e:
                    error_map[event["row_id"]] = {"error_code": 500, "error_message": str(e)}

        return error_map


if __name__ == "__main__":
    EventSubscriber().listen_and_publish_registry_events()
