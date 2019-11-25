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


def create_channel_event_consumer():
    logger.info("Getting events")
    try:
        create_channel_event_details = channel_dao.get_one_create_channel_event(TransactionStatus.PENDING)
        if create_channel_event_details is None:
            return
        wallet_manager = WalletService(connection)
        payload = json.loads(create_channel_event_details["payload"])
    except Exception as e:
        logger.error(f"Failed to get record for create channel, error:{repr(e)}")
        traceback.print_exc()
        utils.report_slack(1, f"Failed to get record for create channel, module: create_channel_consumer, "
                              f"NETWORK_ID:{NETWORK_ID}, error: {(repr(e))}", SLACK_HOOK)
        return

    try:
        logger.info(f"fetched event:{create_channel_event_details}")
        response = wallet_manager.open_channel_by_third_party(
            order_id=payload['order_id'], sender=payload['sender'], signature=payload['signature'],
            r=payload['r'], s=payload['s'], v=payload['v'], current_block_no=payload['current_block_no'],
            group_id=payload['group_id'], org_id=payload["org_id"], recipient=payload['recipient'],
            amount=payload['amount'], currency=payload['currency'],
            amount_in_cogs=payload['amount_in_cogs']
        )
        channel_dao.update_create_channel_event(create_channel_event_details, TransactionStatus.SUCCESS)

    except Exception as e:
        logger.error(f"Exception occurred while create channel, event: {create_channel_event_details}, error:{repr(e)}")
        utils.report_slack(1, f"Exception occurred while create channel, module: create_channel_consumer, "
                              f"event_id: {create_channel_event_details['row_id']} "
                              f"NETWORK_ID:{NETWORK_ID}, error: {(repr(e))}", SLACK_HOOK)
        traceback.print_exc()
        channel_dao.update_create_channel_event(create_channel_event_details, TransactionStatus.FAILED)
    logger.info("done getting events")


if __name__ == "__main__":
    while True:
        create_channel_event_consumer()
        sleep(300)
