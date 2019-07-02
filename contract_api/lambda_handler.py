import json
import re
import traceback

from common.constant import NETWORKS
from common.repository import Repository
from marketplace_api.registry import Registry

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
        elif event['httpMethod'] == 'GET':
            payload_dict = event.get('queryStringParameters')
        else:
            return get_response(400, "Bad Request")

        if path in ["/service", "/feedback"] or path[0:4] == "/org":
            obj_reg = Registry(obj_repo=db[net_id])

        if "/org" == path:
            resp_dta = obj_reg.get_all_org()
        elif "/service" == path:
            if payload_dict is None:
                payload_dict = {}
            resp_dta = obj_reg.get_all_srvcs(qry_param=payload_dict)
            print(type(resp_dta))
            print(resp_dta)
        elif re.match("(\/org\/)[^\/]*(\/service\/)[^\/]*(\/group)[/]{0,1}$", path):
            params = path.split("/")
            org_id = params[2]
            service_id = params[4]
            resp_dta = obj_reg.get_group_info(org_id=org_id, service_id=service_id)
        elif "/channels" == path:
            resp_dta = "Inside" + path
        elif "/feedback" == path:
            resp_dta = "Inside" + path
        else:
            return get_response(400, path)
        if resp_dta is None:
            err_msg = {'status': 'failed', 'error': 'Bad Request', 'api': event['path'], 'payload': payload_dict}
            response = get_response("500", err_msg)
        else:
            response = get_response("200", {"status": "success", "data": resp_dta})
    except Exception as e:
        err_msg = {"status": "failed", "error": repr(e), 'api': event['path'], 'payload': payload_dict}
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
