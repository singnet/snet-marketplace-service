from subscriber.event_subscriber import EventSubscriber


def registry_event_subscription_handler(event, context):
    EventSubscriber().listen_and_publish_registry_events()


def mpe_event_subscription_handler(event, context):
    EventSubscriber().listen_and_publish_mpe_events()
