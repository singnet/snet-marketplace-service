from event_pubsub.domain.models.raw_events import RawEvents


class EventFactory:
    pass

    @staticmethod
    def convert_raw_events_raw_db_model_to_entity_model(raw_event):
        return RawEvents(
            block_no=raw_event.block_no,
            uncle_block_no=raw_event.uncle_block_no,
            event=raw_event.event,
            json_str=raw_event.json_str,
            processed=int.from_bytes(raw_event.processed, "big"),
            transactionHash=raw_event.transactionHash,
            logIndex=raw_event.logIndex,
            error_code=raw_event.error_code,
            error_msg=raw_event.error_msg
        )