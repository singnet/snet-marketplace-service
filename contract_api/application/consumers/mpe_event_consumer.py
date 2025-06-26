import base64

from common.logger import get_logger
from contract_api.application.consumers.event_consumer import EventConsumer
from contract_api.application.schemas.consumer_schemas import MpeEventConsumerRequest
from contract_api.domain.models.channel import NewChannelDomain
from contract_api.infrastructure.repositories.channel_repository import ChannelRepository

logger = get_logger(__name__)


class MPEEventConsumer(EventConsumer):
    def __init__(self):
        super().__init__()
        self._channel_repo = ChannelRepository()

    def on_event(self, request: MpeEventConsumerRequest) -> None:
        event_name = request.event_name
        channel_id = request.channel_id

        if event_name == 'ChannelOpen':
            channel_data = self._get_channel_data_from_blockchain(channel_id)
            logger.info(f"Created channel {channel_id}")
        elif event_name in ['ChannelClaim', 'ChannelExtend', 'ChannelAddFunds']:
            channel_data = self._get_channel_data_from_blockchain(channel_id)
            logger.info(f"Updated channel {channel_id}")
        else:
            logger.info(f"Unhandled event: {event_name}")
            return

        self._channel_repo.upsert_channel(channel_data)

    @staticmethod
    def convert_channel_to_domain(request_data: MpeEventConsumerRequest) -> NewChannelDomain:
        group_id = request_data.group_id
        if request_data.group_id[0:2] == '0x':
            group_id = request_data.group_id[2:]
        group_id = base64.b64encode(group_id).decode('utf8')

        channel = NewChannelDomain(
            channel_id = request_data.channel_id,
            nonce = request_data.nonce,
            sender = request_data.sender,
            signer = request_data.signer,
            recipient = request_data.recipient,
            group_id = group_id,
            balance_in_cogs = request_data.amount,
            expiration = request_data.expiration
        )

        return channel

    def _get_channel_data_from_blockchain(self, channel_id: int) -> NewChannelDomain:
        mpe_contract = self._get_contract("MPE")
        channel_data = mpe_contract.functions.channels(channel_id).call()
        group_id = base64.b64encode(channel_data[4]).decode('utf8')

        channel = NewChannelDomain(
            channel_id = channel_id,
            nonce = channel_data[0],
            sender = channel_data[1],
            signer = channel_data[2],
            recipient = channel_data[3],
            group_id = group_id,
            balance_in_cogs = channel_data[5],
            expiration = channel_data[6]
        )

        return channel

