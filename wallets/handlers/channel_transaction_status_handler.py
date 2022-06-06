import traceback

from common.repository import Repository
from common.utils import Utils
from wallets.config import NETWORKS, NETWORK_ID, SLACK_HOOK
from wallets.service.channel_transaction_status_service import ChannelTransactionStatusService
from aws_xray_sdk.core import patch_all

patch_all()
NETWORKS_NAME = dict((NETWORKS[netId]['name'], netId)
                     for netId in NETWORKS.keys())
obj_util = Utils()
db = dict((netId, Repository(net_id=netId, NETWORKS=NETWORKS))
          for netId in NETWORKS.keys())


def request_handler(event, context):
    try:
        ChannelTransactionStatusService().manage_channel_transaction_status()
    except Exception as e:
        error_message = "Error in updating channel transaction status \n"
        "NETWORK ID:" + str(NETWORK_ID) + "\n"
        "Error:" + repr(e)
        obj_util.report_slack(error_message, SLACK_HOOK)
        traceback.print_exc()
    return
