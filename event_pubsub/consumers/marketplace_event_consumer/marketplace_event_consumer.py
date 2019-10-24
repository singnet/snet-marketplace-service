from event_pubsub.consumers.event_consumer import EventConsumer
from event_pubsub.consumers.marketplace_event_consumer.handle_contracts import HandleContracts


class MarketPlaceEventConsumer(EventConsumer):

    def on_event(self, event):
        net_id = 1
        handle_contracts = HandleContracts(net_id=net_id)
