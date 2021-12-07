import ast
import base64
import os

from common.blockchain_util import BlockChainUtil
from common.logger import get_logger
from common.repository import Repository
from contract_api.consumers.event_consumer import EventConsumer
from contract_api.config import NETWORK_ID, NETWORKS
from contract_api.dao.mpe_repository import MPERepository

logger=get_logger(__name__)


class MPEEventConsumer(EventConsumer):
    _mpe_repository = MPERepository(Repository(NETWORK_ID, NETWORKS=NETWORKS))

    def __init__(self, ws_provider):
        self.blockchain_util = BlockChainUtil("WS_PROVIDER", ws_provider)

    def on_event(self, event):
        net_id = NETWORK_ID
        base_contract_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', '..','node_modules', 'singularitynet-platform-contracts'))
        mpe_contract = self.blockchain_util.get_contract_instance(base_contract_path, "MPE", net_id)

        logger.info(f"processing mpe event {event}")
        event_name = event["name"]
        event_data = event["data"]
        mpe_data = ast.literal_eval(event_data['json_str'])

        if event_name == 'ChannelOpen':
            self._mpe_repository.create_channel(mpe_data)
        else:
            channel_id = int(mpe_data['channelId'])
            channel_data = mpe_contract.functions.channels(
                channel_id).call()
            group_id = base64.b64encode(channel_data[4]).decode('utf8')
            self._mpe_repository.update_channel(
                channel_id=channel_id, group_id=group_id, channel_data=channel_data)
