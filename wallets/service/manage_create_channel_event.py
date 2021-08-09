import json
import traceback
from time import sleep

from common.constant import TransactionStatus
from common.logger import get_logger
from common.repository import Repository
from common.utils import Utils
from wallets.config import NETWORKS, NETWORK_ID, SLACK_HOOK
from wallets.dao.channel_dao import ChannelDAO
from wallets.service.wallet_service import WalletService

connection = Repository(net_id=NETWORK_ID, NETWORKS=NETWORKS)
channel_dao = ChannelDAO(connection)
utils = Utils()

logger = get_logger(__name__)


class ManageCreateChannelEvent:
    def __init__(self):
        pass

    @staticmethod
    def manage_create_channel_event():
        create_channel_event_from_orchestrator = channel_dao.get_one_create_channel_event(TransactionStatus.NOT_SUBMITTED)
        if not bool(create_channel_event_from_orchestrator):
            return
        wallet_manager = WalletService(connection)
        payload = json.loads(create_channel_event_from_orchestrator["payload"])
        try:
            wallet_manager.open_channel_by_third_party(
                    order_id=payload['order_id'], sender=payload['sender'], signature=payload['signature'],
                    r=payload['r'], s=payload['s'], v=payload['v'], current_block_no=payload['current_block_no'],
                    group_id=payload['group_id'], org_id=payload["org_id"], recipient=payload['recipient'],
                    amount=payload['amount'], currency=payload['currency'],
                    amount_in_cogs=payload['amount_in_cogs']
                )
            channel_dao.update_create_channel_event(create_channel_event_from_orchestrator, TransactionStatus.SUCCESS)
        except Exception as e:
            channel_dao.update_create_channel_event(create_channel_event_from_orchestrator, TransactionStatus.FAILED)
            utils.report_slack(
                slack_msg=f"Error while submitting blockchain transaction |method_name:: 'open_channel_by_third_party' |network_id: {NETWORK_ID} |error: {repr(e)}",
                SLACK_HOOK=SLACK_HOOK)