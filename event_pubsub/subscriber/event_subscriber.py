from common.repository import Repository
from event_pubsub.subscriber.event_repository import EventRepository

import requests

from event_pubsub.subscriber.listeners import WebHookHandler


class EventSubscriber(object):
    EVENTS_LIMIT = 30

    connection = (Repository(NETWORKS={
        'db': {"HOST": "localhost",
               "USER": "root",
               "PASSWORD": "password",
               "NAME": "pub_sub",
               "PORT": 3306,
               }
    }))
    event_repository = EventRepository(connection)

    def __init__(self, repository):
        self.event_consumer_map = EventSubscriber.initiate_event_subscription(repository)

    def subscribe(self, event_names, event_consumer):
        for event in event_names:
            if event.get_name() in self.event_consumer_map:
                self.event_consumer_map[event] = event_consumer
            else:
                self.event_consumer_map[event] = [event_consumer]

        self.persist_event_subscription(event_names, event_consumer)

    def persist_event_subscription(self, event_names, event_consumer):
        pass

    @classmethod
    def initiate_event_subscription(cls):
        return {"OrganizationCreated": [{"name": "", "tyoe": "webhook", "url": "https://subsribedpai1"},
                                        {"tyoe": "lambda_arn", "url": "https://subsribedpai1"}]}

    def listen_events(self):
        registry_events = self.event_repository.read_registry_events()

        mpe_events = self.event_repository.read_mpe_events()
        self.publish_events(mpe_events)
        self.publish_events(registry_events)

    def publish_events(self, events):

        error_map = {}

        for event in events:
            listeners = self.event_consumer_map[event['event']]
            # error_map[0] = { event[]}
            for listener in listeners:
                push_event = {"data": event, "name": event["event"]}
                try:
                    if listener["type"] == "webhook":

                        WebHookHandler(listener["url"], push_event).push_event()

                    elif listener["type"] == "lambda_arn":
                        # execute lambda here
                        pass
                except Exception as e:
                    error_map[event["row_id"]] = {"error_message": str(e), "error_code": 1}
                    raise e

        return error_map
