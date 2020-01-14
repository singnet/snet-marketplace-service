import json
import re
import traceback
import boto3
from dapp_user.config import NETWORKS, GET_FREE_CALLS_METERING_ARN, SLACK_HOOK, NETWORK_ID
from common.repository import Repository
from common.utils import Utils
from common.utils import handle_exception_with_slack_notification
from common.logger import get_logger

from dapp_user.user import User
from aws_xray_sdk.core import patch_all

patch_all()


db = Repository(net_id=NETWORK_ID, NETWORKS=NETWORKS)
logger = get_logger(__name__)
obj_util = Utils()


@handle_exception_with_slack_notification(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger)
def request_handler(event, context):
    print(event)
    if 'path' not in event:
        return get_response(400, "Bad Request")
    payload_dict = None
    path = event['path'].lower()
    path = re.sub(r"^(\/dapp-user)", "", path)
    usr_obj = User(obj_repo=db)
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
            user_data=event['requestContext'], email_alerts=payload_dict['email_alerts'], is_terms_accepted=payload_dict['is_terms_accepted'])

    elif "/profile" == path and event['httpMethod'] == 'GET':
        response_data = usr_obj.get_user_profile(
            user_data=event['requestContext'])

    elif "/wallet" == path and event['httpMethod'] == 'GET':
        """ Deprecated """
        response_data = []

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

    elif "/wallet/register" == path:
        """ Deprecated """
        response_data = []

    else:
        return get_response(404, "Not Found")

    if response_data is None:
        err_msg = {'status': 'failed', 'error': 'Bad Request',
                   'api': event['path'], 'payload': payload_dict, 'network_id': NETWORK_ID}
        obj_util.report_slack(1, str(err_msg), SLACK_HOOK)
        response = get_response(500, err_msg)
    else:
        response = get_response(
            200, {"status": "success", "data": response_data})
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
