from event_pubsub.config import NETWORKS, NETWORK_ID
from event_pubsub.repository import Repository
from event_pubsub.event_repository import EventRepository

connection = Repository(NETWORKS=NETWORKS)
event_repository = EventRepository(connection)


class EventPubsubService():
    pass

    @staticmethod
    def get_mpe_processed_transactions(transaction_list):
        transactions = event_repository.get_mpe_processed_transactions(transaction_list=transaction_list)
        return transactions
