import json
import re
import traceback

from common.constant import NETWORKS
from common.repository import Repository
from common.utils import Utils
from service_status.service_status import ServiceStatus

NETWORKS_NAME = dict((NETWORKS[netId]['name'], netId) for netId in NETWORKS.keys())
obj_util = Utils()
db = dict((netId, Repository(net_id=netId)) for netId in NETWORKS.keys())


def request_handler(event, context):
    print(event)
    try:
        stage = event['requestContext']['stage']
        net_id = NETWORKS_NAME[stage]
        if db[net_id].connection is None:
            raise Exception('database connection is not initialized')

        print('update service status', net_id)
        obj_srvc_st = ServiceStatus(repo=db[net_id], net_id=net_id)
        obj_srvc_st.update_service_status()
    except Exception as e:
        print(repr(e))
        obj_util.report_slack(1, str(err_msg))
        traceback.print_exc()
    return
