from event_pubsub.constants import EventType
from event_pubsub.infrastructure.repositories.mpe_event_repo import MPEEventRepository

mpe_repo = MPEEventRepository()


class RawEventsService:
    def __init__(self):
        pass

    @staticmethod
    def get_repo_obj(contract_name):
        if contract_name == EventType.MPE.value:
            return mpe_repo
        raise Exception(f"Invalid Contract name :: {contract_name}")

    def get_raw_events(self, transaction_hash_list, contract_name):
        repo_obj = self.get_repo_obj(contract_name=contract_name)
        raw_events = repo_obj.get_raw_events(transaction_hash_list=transaction_hash_list)
        return [raw_event.to_dict() for raw_event in raw_events]

