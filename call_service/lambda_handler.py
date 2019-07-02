import json
import logging
import traceback

from common.constant import NETWORKS
from common.repository import Repository
from client import Client

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
        obj_cli = Client(dapp_user_address=payload_dict['dapp_user_address'])

        if event['httpMethod'] == 'POST':
            body = event['body']
            if body is not None and len(body) > 0:
                payload_dict = json.loads(body)
        elif event['httpMethod'] == 'GET':
            payload_dict = event.get('queryStringParameters')
        else:
            return get_response(400, "Bad Request")

        if "/call-service" == path:
            resp_dta = obj_cli.call_service(payload_dict['org_id'], payload_dict['service_id'],
                                                payload_dict['user_address'], payload_dict['input'],
                                                payload_dict['method'])
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
