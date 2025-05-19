import ast
import base64
import os

from common.blockchain_util import BlockChainUtil
from common.logger import get_logger
from common.repository import Repository
from contract_api.consumers.event_consumer import EventConsumer
from contract_api.config import NETWORK_ID, NETWORKS, CONTRACT_BASE_PATH, TOKEN_NAME, STAGE
from contract_api.dao.mpe_repository import MPERepository

logger=get_logger(__name__)


class MPEEventConsumer(EventConsumer):
    _mpe_repository = MPERepository(Repository(NETWORK_ID, NETWORKS=NETWORKS))

    def __init__(self, ws_provider):
        self.blockchain_util = BlockChainUtil("WS_PROVIDER", ws_provider)

    def on_event(self, event):
        net_id = NETWORK_ID
        base_contract_path = os.path.abspath(
            os.path.join(CONTRACT_BASE_PATH,'node_modules', 'singularitynet-platform-contracts'))
        mpe_contract = self.blockchain_util.get_contract_instance(base_contract_path,
                                                                  "MPE",
                                                                  net_id,
                                                                  TOKEN_NAME,
                                                                  STAGE)

        event = event["blockchain_event"]
        event_name = event["name"]
        data = event["data"]
        event_data = ast.literal_eval(data["json_str"])
        logger.info(f"Processing MPE event: {event_name} with data {event_data}")

        if event_name == 'ChannelOpen':
            self._mpe_repository.create_channel(event_data)
            logger.info(f"Created channel {int(event_data['channelId'])}")
        elif event_name in ['ChannelClaim', 'ChannelExtend', 'ChannelAddFunds']:
            channel_id = int(event_data['channelId'])
            channel_data = mpe_contract.functions.channels(
                channel_id).call()
            group_id = base64.b64encode(channel_data[4]).decode('utf8')
            self._mpe_repository.update_channel(
                channel_id=channel_id, group_id=group_id, channel_data=channel_data)
            logger.info(f"Updated channel {channel_id}")
        else:
            logger.info(f"Unhandled event: {event_name}")
