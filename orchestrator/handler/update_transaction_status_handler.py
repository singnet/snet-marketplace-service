import traceback

from aws_xray_sdk.core import patch_all

from common.repository import Repository
from common.utils import Utils
from orchestrator.config import NETWORKS, NETWORK_ID
from orchestrator.services.order_service import OrderService

patch_all()
obj_util = Utils()
repo =Repository(net_id=NETWORK_ID, NETWORKS=NETWORKS)


def request_handler(event, context):
    try:
        order_service = OrderService(obj_repo=repo)
        response = order_service.manage_update_canceled_order_in_txn_history()
        if response == False:
            raise Exception("Error in update transaction status for network id %s", NETWORK_ID)
        return "success"
    except Exception as e:
        error_message = "Error in updating channel transaction status \n"
        "NETWORK ID:" + str(NETWORK_ID) + "\n"
        "Error:" + repr(e)
        obj_util.report_slack(1, error_message)
        traceback.print_exc()