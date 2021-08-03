from event_pubsub.domain.factory.event_factory import EventFactory
from event_pubsub.infrastructure.models import MpeEventsRaw
from event_pubsub.infrastructure.repositories.base_repository import BaseRepository


class ChannelRepo(BaseRepository):
    pass

    def get_mpe_raw_events(self, transaction_list=[], processed_state=None):
        try:
            query = self.session.query(MpeEventsRaw)
            if transaction_list:
                query.filter(MpeEventsRaw.transactionHash.in_(transaction_list))
            if processed_state:
                query.filter(MpeEventsRaw.processed == processed_state)
            mpe_events_raw_db = query.all()
            self.session.commit()
        except Exception as e:
            self.connection.rollback_transaction()
            raise e
        mpe_events_raw = []
        for event in mpe_events_raw_db:
            mpe_events_raw.append(EventFactory().convert_mpe_events_raw_db_model_to_entity_model(event))
        return mpe_events_raw


