import json
import re
import traceback
import boto3
from common.constant import NETWORKS, GET_FREE_CALLS_METERING_ARN
from common.repository import Repository
from common.utils import Utils

from dapp_user.user import User

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
        response_data = None

        if event['httpMethod'] == 'POST':
            payload_dict = json.loads(event['body'])
        elif event['httpMethod'] == 'GET':
            payload_dict = event.get('queryStringParameters')
        else:
            return get_response(405, "Method Not Allowed")

        if "/signup" == path:
            response_data = usr_obj.user_signup(
                user_data=event['requestContext'])

        elif "/profile" == path and event['httpMethod'] == 'POST':
            response_data = usr_obj.update_user_profile(
                user_data=event['requestContext'], email_alerts=payload_dict['email_alerts'])

        elif "/profile" == path and event['httpMethod'] == 'GET':
            response_data = usr_obj.get_user_profile(
                user_data=event['requestContext'])

        elif "/wallet" == path:
            response_data = usr_obj.get_wallet_details(
                user_data=event['requestContext'])

        elif "/delete-user" == path:
            response_data = usr_obj.del_user_data(
                user_data=event['requestContext'])

        elif "/feedback" == path and event['httpMethod'] == 'GET':
            response_data = usr_obj.get_user_feedback(user_data=event['requestContext'], org_id=payload_dict.get("org_id", None),
                                                      service_id=payload_dict.get("service_id", None))
        elif "/feedback" == path and event['httpMethod'] == 'POST':
            response_data = usr_obj.validate_and_set_user_feedback(
                feedback_data=payload_dict['feedback'], user_data=event['requestContext'])

        elif "/usage/freecalls" == path:
            lambda_client = boto3.client('lambda')
            response = lambda_client.invoke(FunctionName=GET_FREE_CALLS_METERING_ARN, InvocationType='RequestResponse',
                                            Payload=json.dumps(event))
            result = json.loads(response.get('Payload').read())
            return result

        else:
            return get_response(404, "Not Found")

        if response_data is None:
            err_msg = {'status': 'failed', 'error': 'Bad Request',
                       'api': event['path'], 'payload': payload_dict, 'network_id': net_id}
            obj_util.report_slack(1, str(err_msg))
            response = get_response(500, err_msg)
        else:
            response = get_response(
                200, {"status": "success", "data": response_data})
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
