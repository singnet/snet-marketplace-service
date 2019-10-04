import traceback

from common.repository import Repository
from common.utils import Utils
from wallets.config import NETWORKS, NETWORK_ID

NETWORKS_NAME = dict((NETWORKS[netId]['name'], netId)
                     for netId in NETWORKS.keys())
obj_util = Utils()
db = dict((netId, Repository(net_id=netId, NETWORKS=NETWORKS))
          for netId in NETWORKS.keys())


def request_handler(event, context):
    try:
        print("Test Event:", event)
    except Exception as e:
        error_message = "Error in updating channel transaction status \n"
        "NETWORK ID:" + NETWORK_ID + "\n"
        "Error:" + repr(e)
    obj_util.report_slack(1, error_message)
    traceback.print_exc()

    return
