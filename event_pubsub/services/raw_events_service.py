from event_pubsub.constants import EventType
from event_pubsub.infrastructure.repositories.mpe_event_repo import MPEEventRepository

mpe_repo = MPEEventRepository()


class RawEventsService:
    def __init__(self):
        pass

    @staticmethod
    def get_repo_obj(event_name):
        if event_name == EventType.MPE.value:
            return mpe_repo
        raise Exception(f"Invalid Contract name :: {event_name}")

    def get_raw_events(self, transaction_hash_list, event_name):
        repo_obj = self.get_repo_obj(event_name=event_name)
        raw_events = repo_obj.get_raw_events(transaction_hash_list=transaction_hash_list)
        if raw_events:
            raw_events = [raw_event.to_dict() for raw_event in raw_events]
        return raw_events
