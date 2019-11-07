from event_pubsub.listeners.event_listeners import EventListener


def registry_event_listener_handler(event, context):
    EventListener().listen_and_publish_registry_events()


def mpe_event_listener_handler(event, context):
    EventListener().listen_and_publish_mpe_events()
