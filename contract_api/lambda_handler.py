import json
import logging
import re
import traceback
from schema import Schema, And

from tests.common.constant import NETWORKS
from tests.common.repository import Repository
from mpe import MPE
from registry import Registry

NETWORKS_NAME = dict((NETWORKS[netId]['name'], netId) for netId in NETWORKS.keys())
db = dict((netId, Repository(net_id=netId)) for netId in NETWORKS.keys())


def request_handler(event, context):
    print(event)
    if 'path' not in event:
        return get_response(400, "Bad Request")
    try:
        payload_dict = None
        resp_dta = None
        path = event['path'].lower()
        stage = event['requestContext']['stage']
        net_id = NETWORKS_NAME[stage]

        if event['httpMethod'] == 'POST':
            body = event['body']
            if body is not None and len(body) > 0:
                payload_dict = json.loads(body)
        elif event['httpMethod'] == 'GET':
            payload_dict = event.get('queryStringParameters')
        else:
            return get_response(400, "Bad Request")

        if path in ["/service", "/feedback"] or path[0:4] == "/org" or path[0:5] == "/user":
            obj_reg = Registry(obj_repo=db[net_id])

        if "/org" == path:
            resp_dta = obj_reg.get_all_org()
        elif re.match("(\/service)[/]{0,1}$", path):
            if payload_dict is None:
                payload_dict = {}
            resp_dta = obj_reg.get_all_srvcs(qry_param=payload_dict)
        elif re.match("(\/org\/)[^\/]*(\/service\/)[^\/]*(\/group)[/]{0,1}$", path):
            params = path.split("/")
            org_id = params[2]
            service_id = params[4]
            resp_dta = obj_reg.get_group_info(org_id=org_id, service_id=service_id)
        elif "/channels" == path:
            obj_mpe = MPE(net_id=net_id, obj_repo=db[net_id])
            resp_dta = obj_mpe.get_channels_by_user_address(payload_dict['user_address'],
                                                            payload_dict.get('org_id', None),
                                                            payload_dict.get('service_id', None))
        elif re.match("(\/user\/)[^\/]*(\/feedback)[/]{0,1}$", path):
            params = path.split("/")
            user_address = params[2]
            resp_dta = get_user_feedback(user_address=user_address, obj_reg=obj_reg)
        elif "/feedback" == path:
            resp_dta = set_user_feedback(payload_dict['feedback'], obj_reg=obj_reg, net_id=net_id)
        else:
            return get_response(400, "Invalid URL path.")
        if resp_dta is None:
            err_msg = {'status': 'failed', 'error': 'Bad Request', 'api': event['path'], 'payload': payload_dict}
            response = get_response(500, err_msg)
        else:
            response = get_response(200, {"status": "success", "data": resp_dta})
    except Exception as e:
        err_msg = {"status": "failed", "error": repr(e), 'api': event['path'], 'payload': payload_dict}
        response = get_response(500, err_msg)
        traceback.print_exc()
    return response


def check_for_blank(field):
    if field is None or len(field) == 0:
        return True
    return False


def get_user_feedback(user_address, obj_reg):
    if check_for_blank(user_address):
        return []
    return obj_reg.get_usr_feedbk(user_address)


def set_user_feedback(feedbk_info, obj_reg, net_id):
    feedbk_recorded = False
    schema = Schema([{'user_address': And(str),
                      'org_id': And(str),
                      'service_id': And(str),
                      'up_vote': bool,
                      'down_vote': bool,
                      'comment': And(str),
                      'signature': And(str)
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
