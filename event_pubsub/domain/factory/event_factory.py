from event_pubsub.domain.models.raw_event import RawEvent


class RawEventFactory:
    pass

    @staticmethod
    def convert_raw_event_dbs_raw_db_model_to_entity_model(raw_event_db):
        return RawEvent(
            block_no=raw_event_db.block_no,
            uncle_block_no=raw_event_db.uncle_block_no,
            event=raw_event_db.event,
            event_data=raw_event_db.event_data,
            processed=raw_event_db.processed,
            transactionHash=raw_event_db.transactionHash,
            logIndex=raw_event_db.logIndex,
            error_code=raw_event_db.error_code,
            error_msg=raw_event_db.error_msg
        )