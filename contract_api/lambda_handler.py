import json
import re
import traceback
from schema import Schema, And
from common.constant import NETWORKS
from common.repository import Repository
from common.utils import Utils
from contract_api.registry import Registry

NETWORKS_NAME = dict((NETWORKS[netId]['name'], netId) for netId in NETWORKS.keys())
db = dict((netId, Repository(net_id=netId)) for netId in NETWORKS.keys())
obj_util = Utils()

def request_handler(event, context):
    print(event)
    if 'path' not in event:
        return get_response(400, "Bad Request")
    try:
        payload_dict = None
        path = event['path'].lower()
        stage = event['requestContext']['stage']
        net_id = NETWORKS_NAME[stage]
        method = event['httpMethod']
        resp_dta = None

        if method == 'POST':
            payload_dict = json.loads(event['body'])
        elif method == 'GET':
            payload_dict = event.get('queryStringParameters')
        else:
            return get_response(405, "Method Not Allowed")

        if path in ["/org", "/service", "/feedback"] or path.split("/")[1] == "/org":
            obj_reg = Registry(obj_repo=db[net_id])

        if "/org" == path:
            resp_dta = obj_reg.get_all_org()

        elif "/service" == path and method == 'POST':
            payload_dict = {} if payload_dict is None else payload_dict
            resp_dta = obj_reg.get_all_srvcs(qry_param=payload_dict)

        elif "/service" == path and method == 'GET':
            resp_dta = obj_reg.get_filter_attribute(attribute=payload_dict["attribute"])

        elif re.match("(\/org\/)[^\/]*(\/service\/)[^\/]*(\/group)[/]{0,1}$", path):
            params = path.split("/")
            org_id = params[2]
            service_id = params[4]
            resp_dta = obj_reg.get_group_info(org_id=org_id, service_id=service_id)

        elif "/feedback" == path and method == 'GET':
            resp_dta = obj_reg.get_usr_feedbk(payload_dict["user_address"])

        elif "/feedback" == path and method == 'POST':
            resp_dta = set_user_feedback(payload_dict['feedback'], obj_reg=obj_reg, net_id=net_id)

        else:
            return get_response(404, "Not Found")

        if resp_dta is None:
            err_msg = {'status': 'failed', 'error': 'Bad Request', 'api': event['path'], 'payload': payload_dict, 'network_id': net_id}
            obj_util.report_slack(1, str(err_msg))
            response = get_response(500, err_msg)
        else:
            response = get_response(200, {"status": "success", "data": resp_dta})
    except Exception as e:
        err_msg = {"status": "failed", "error": repr(e), 'api': event['path'], 'payload': payload_dict, 'network_id': net_id}
        obj_util.report_slack(1, str(err_msg))
        response = get_response(500, err_msg)
        traceback.print_exc()
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

def set_user_feedback(feedbk_info, obj_reg, net_id):
    schema = Schema([{'user_address': And(str),
                      'org_id': And(str),
                      'service_id': And(str),
                      'user_rating': And(str),
                      'comment': And(str)
                      }])
    try:
        feedback_data = schema.validate([feedbk_info])
        feedbk_recorded = obj_reg.set_usr_feedbk(feedback_data[0], net_id=net_id)
    except Exception as err:
        print("Invalid Input ", err)
        return None
    if feedbk_recorded:
        return []
    return None
