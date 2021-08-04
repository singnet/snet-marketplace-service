from event_pubsub.domain.models.raw_events import RawEvents


class EventFactory:
    pass

    @staticmethod
    def convert_raw_events_raw_db_model_to_entity_model(raw_events):
        if not raw_events:
            return None
        return RawEvents(
            block_no=raw_events.block_no,
            uncle_block_no=raw_events.uncle_block_no,
            event=raw_events.event,
            json_str=raw_events.json_str,
            processed=int.from_bytes(raw_events.processed, "big"),
            transactionHash=raw_events.transactionHash,
            logIndex=raw_events.logIndex,
            error_code=raw_events.error_code,
            error_msg=raw_events.error_msg
        )
