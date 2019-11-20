import json

from common.constant import TransactionStatus
from common.logger import file_logger
from common.repository import Repository
from common.utils import Utils
from wallets.config import NETWORKS, NETWORK_ID, SLACK_HOOK
from wallets.dao.wallet_data_access_object import WalletDAO
from wallets.service.wallet_service import WalletService

connection = Repository(net_id=NETWORK_ID, NETWORKS=NETWORKS)
wallet_dao = WalletDAO(connection)
utils = Utils()

logger = file_logger(__name__)


def create_channel_event_consumer():

    try:
        create_channel_event_details = wallet_dao.get_pending_create_channel_event()
        if create_channel_event_details is None:
            return
        wallet_manager = WalletService(connection)
        payload = json.loads(create_channel_event_details["payload"])
    except Exception as e:
        logger.error("Failed to get record for create channel")
        utils.report_slack(1, f"Failed to get record for create channel, module: create_channel_consumer, "
                              f"NETWORK_ID:{NETWORK_ID}, error: {(repr(e))}", SLACK_HOOK)
        return

    try:
        response = wallet_manager.open_channel_by_third_party(
            order_id=payload['order_id'], sender=payload['sender'], signature=payload['signature'],
            r=payload['r'], s=payload['s'], v=payload['v'], current_block_no=payload['current_block_no'],
            group_id=payload['group_id'], org_id=payload["org_id"], recipient=payload['recipient'],
            amount=payload['amount'], currency=payload['currency'],
            amount_in_cogs=payload['amount_in_cogs']
        )
        wallet_dao.update_create_channel_event(create_channel_event_details, TransactionStatus.SUCCESS)

    except Exception as e:
        logger.error(f"Exception occurred while create channel, event: {create_channel_event_details}")
        utils.report_slack(1, f"Exception occurred while create channel, module: create_channel_consumer, "
                              f"event_id: {create_channel_event_details['row_id']} "
                              f"NETWORK_ID:{NETWORK_ID}, error: {(repr(e))}", SLACK_HOOK)
        wallet_dao.update_create_channel_event(create_channel_event_details, TransactionStatus.FAILED)


if __name__ == "__main__":
    create_channel_event_consumer()
