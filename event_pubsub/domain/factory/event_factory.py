from event_pubsub.domain.models.mpe_raw_events import MpeEventsRaw


class EventFactory:
    pass

    @staticmethod
    def convert_mpe_events_raw_db_model_to_entity_model(mpe_events_raw):
        if not mpe_events_raw:
            return None
        return MpeEventsRaw(
            block_no=mpe_events_raw.block_no,
            event=mpe_events_raw.event,
            json_str=mpe_events_raw.json_str,
            processed=mpe_events_raw.processed,
            transactionHash=mpe_events_raw.transactionHash,
            logIndex=mpe_events_raw.logIndex,
            error_code=mpe_events_raw.error_code,
            error_msg=mpe_events_raw.error_msg
        )
