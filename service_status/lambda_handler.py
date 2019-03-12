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
route_path = {}


def request_handler(event, context):
    print(event)
    if 'path' not in event:
        print("request_handler::path: ", None)
        return get_response("400", "Bad Request")
    try:
        path = event['path'].lower()
        stage = event['requestContext']['stage']
        net_id = NETWORKS_NAME[stage]
        if db[net_id].connection is None:
            raise Exception('database connection is not initialized')

        data = None

        if "update-service-status" == path:
            print('update service status', net_id)
            obj_srvc_st = ServiceStatus(repo=db[net_id], net_id=net_id)
            obj_srvc_st.update_service_status()
            data = {}

        if data is None:
            err_msg = {'status': 'failed', 'error': 'Bad Request', 'api': event['path']}
            obj_util.report_slack(1, str(err_msg))
            response = get_response("400", err_msg)
        else:
            response = get_response("200", {"status": "success", "data": data})
    except Exception as e:
        err_msg = {"status": "failed", "error": repr(e)}
        obj_util.report_slack(1, str(err_msg))
        response = get_response(500, err_msg)
        traceback.print_exc()

    print(response)
    return response

def get_response(status_code, message):
    return {
        'statusCode': status_code,
        'body': json.dumps(message),
        'headers': {
            'Content-Type': 'application/json',
            "X-Requested-With": '*',
            "Access-Control-Allow-Headers": 'Access-Control-Allow-Origin, Content-Type,X-Amz-Date,Authorization,X-Api-Key,x-requested-with',
            "Access-Control-Allow-Origin": '*',
            "Access-Control-Allow-Methods": 'GET,OPTIONS,POST'
        }
    }
