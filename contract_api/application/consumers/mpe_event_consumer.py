import base64

from common.logger import get_logger
from common.repository import Repository
from contract_api.application.consumers.event_consumer import EventConsumer
from contract_api.application.schemas.consumer_schemas import MpeEventConsumerRequest
from contract_api.config import NETWORK_ID, NETWORKS, CONTRACT_BASE_PATH, TOKEN_NAME, STAGE
from contract_api.dao.mpe_repository import MPERepository

logger=get_logger(__name__)


class MPEEventConsumer(EventConsumer):
    def __init__(self):
        super().__init__()
        self._mpe_repository = MPERepository(Repository(NETWORK_ID, NETWORKS=NETWORKS))

    def on_event(self, request: MpeEventConsumerRequest):
        mpe_contract = self._get_contract("MPE")
        event_name = request.event_name
        channel_id = request.channel_id

        if event_name == 'ChannelOpen':
            self._mpe_repository.create_channel(request)
            logger.info(f"Created channel {channel_id}")
        elif event_name in ['ChannelClaim', 'ChannelExtend', 'ChannelAddFunds']:
            channel_data = mpe_contract.functions.channels(channel_id).call()
            group_id = base64.b64encode(channel_data[4]).decode('utf8')
            self._mpe_repository.update_channel(
                channel_id=channel_id, group_id=group_id, channel_data=channel_data
            )
            logger.info(f"Updated channel {channel_id}")
        else:
            logger.info(f"Unhandled event: {event_name}")
