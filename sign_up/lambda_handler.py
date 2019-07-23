import json
import re
import traceback
from common.constant import NETWORKS
from common.repository import Repository
from common.utils import Utils

from sign_up.user import User

NETWORKS_NAME = dict((NETWORKS[netId]['name'], netId)
                     for netId in NETWORKS.keys())
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
        usr_obj = User(obj_repo=db[net_id])
        resp_dta = None

        if event['httpMethod'] == 'POST':
            payload_dict = json.loads(event['body'])
        elif event['httpMethod'] == 'GET':
            payload_dict = event.get('queryStringParameters')
        else:
            return get_response(405, "Method Not Allowed")

        if "/signup" == path:
            resp_dta = usr_obj.user_signup(event['requestContext'])

        elif "/profile" == path and event['httpMethod'] == 'POST':
            resp_dta = usr_obj.update_user_profile(
                username=payload_dict['username'], email_alerts=payload_dict['email_alerts'])

        elif "/profile" == path and event['httpMethod'] == 'GET':
            resp_dta = usr_obj.get_user_profile(
                username=payload_dict['username'])

        elif "/wallet" == path:
            status = usr_obj.check_for_existing_wallet(
                payload_dict['username'])
            resp_dta = {"isAssigned": status,
                        "username": payload_dict['username']}

        elif re.match("(\/delete-user\/)[^\/]*$", path):
            username = path.split("/")[2]
            resp_dta = usr_obj.del_user_data(username=username)

        else:
            return get_response(404, "Not Found")

        if resp_dta is None:
            err_msg = {'status': 'failed', 'error': 'Bad Request',
                       'api': event['path'], 'payload': payload_dict, 'network_id': net_id}
            obj_util.report_slack(1, str(err_msg))
            response = get_response(500, err_msg)
        else:
            response = get_response(
                200, {"status": "success", "data": resp_dta})
    except Exception as e:
        err_msg = {"status": "failed", "error": repr(
            e), 'api': event['path'], 'payload': payload_dict, 'network_id': net_id}
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
