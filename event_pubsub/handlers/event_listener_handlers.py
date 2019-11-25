from event_pubsub.listeners.event_listeners import RegistryEventListener, MPEEventListener, RFAIEventListener


def registry_event_listener_handler(event, context):
    RegistryEventListener().listen_and_publish_registry_events()


def mpe_event_listener_handler(event, context):
    MPEEventListener().listen_and_publish_mpe_events()


def rfai_event_listener_handler(event,context):
    RFAIEventListener().listen_and_publish_rfai_events()
