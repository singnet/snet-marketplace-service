class EventSubscriber(object):

    def __init__(self):
        self.event_listener_map = {}

    def subscribe(self, event_names, event_listener):
        for event in event_names:
            if event.get_name() in self.event_listener_map:
                self.event_listener_map[event] = event_listener
            else:
                self.event_listener_map[event] = [event_listener]

