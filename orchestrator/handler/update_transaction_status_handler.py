import traceback

from aws_xray_sdk.core import patch_all

from common.repository import Repository
from common.utils import Utils
from orchestrator.config import NETWORKS, NETWORK_ID
from orchestrator.services.update_transaction_status_service import UpdateTransactionStatus

patch_all()
NETWORKS_NAME = dict((NETWORKS[netId]['name'], netId)
                     for netId in NETWORKS.keys())
obj_util = Utils()
db = dict((netId, Repository(net_id=netId, NETWORKS=NETWORKS))
          for netId in NETWORKS.keys())


def request_handler(event, context):
    try:
        obj_update_transaction_status = UpdateTransactionStatus(obj_repo=db[NETWORK_ID])
        response = obj_update_transaction_status.manage_update_canceled_order_in_txn_history()
        if response == False:
            raise Exception("Error in update transaction status for network id %s", NETWORK_ID)
        return "success"
    except Exception as e:
        error_message = "Error in updating channel transaction status \n"
        "NETWORK ID:" + str(NETWORK_ID) + "\n"
        "Error:" + repr(e)
        obj_util.report_slack(1, error_message)
        traceback.print_exc()