from event_pubsub.domain.factory.event_factory import EventFactory
from event_pubsub.infrastructure.models import MpeEventsRaw
from event_pubsub.infrastructure.repositories.base_repository import BaseRepository


class MPEEventRepository(BaseRepository):
    pass

    def get_raw_events(self, transaction_hash_list):
        try:
            query = self.session.query(MpeEventsRaw)
            if transaction_hash_list:
                query = query.filter(MpeEventsRaw.transactionHash.in_(transaction_hash_list))
            mpe_events_raw_db = query.all()
            self.session.commit()
        except Exception as e:
            self.connection.rollback_transaction()
            raise e
        mpe_events_raw = []
        for event in mpe_events_raw_db:
            mpe_events_raw.append(EventFactory().convert_raw_events_raw_db_model_to_entity_model(event))
        return mpe_events_raw


