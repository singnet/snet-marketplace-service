from event_pubsub.config import NETWORKS, NETWORK_ID
from event_pubsub.infrastructure.repositories.channel_repo import ChannelRepo
from event_pubsub.repository import Repository
from event_pubsub.event_repository import EventRepository

connection = Repository(NETWORKS=NETWORKS, NETWORK_ID=NETWORK_ID)
event_repository = EventRepository(connection)


class EventPubsubService():
    pass

    @staticmethod
    def get_mpe_processed_transactions(transaction_list):
        mpe_raw_events = ChannelRepo().get_mpe_raw_events(transaction_list=transaction_list, processed_state=1)
        processed_transactions = []
        for event in mpe_raw_events:
            processed_transactions.append(event.transactionHash)
        return processed_transactions

