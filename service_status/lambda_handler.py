import json
import re
import traceback

from service_status.config import NETWORKS, NETWORK_ID
from common.repository import Repository
from common.utils import Utils
from service_status.service_status import ServiceStatus

NETWORKS_NAME = dict((NETWORKS[netId]["name"], netId) for netId in NETWORKS.keys())
obj_util = Utils()
db = dict(
    (netId, Repository(net_id=netId, NETWORKS=NETWORKS)) for netId in NETWORKS.keys()
)


def request_handler(event, context):
    print(event)
    try:
        obj_srvc_st = ServiceStatus(repo=db[NETWORK_ID], net_id=NETWORK_ID)
        obj_srvc_st.update_service_status()
    except Exception as e:
        print(repr(e))
        obj_util.report_slack(
            1,
            "Error in updating service status::NETWORK_ID:" + NETWORK_ID + "|err:" + e,
        )
        traceback.print_exc()
    return
