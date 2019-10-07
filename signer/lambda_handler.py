import json
import re
import traceback

from common.logger import get_logger
from common.utils import Utils
from signer.config import NET_ID
from signer.config import SLACK_HOOK
from signer.signer import Signer

obj_util = Utils()

logger = get_logger(__name__)


def request_handler(event, context):
    logger.info(event)
    if "path" not in event:
        return get_response(400, "Bad Request")
    try:
        payload_dict = None
        path = event["path"].lower()
        path = re.sub(r"^(\/signer)", "", path)
        signer_object = Signer(net_id=NET_ID)
        method = event["httpMethod"]
        response_data = None

        if method == "POST":
            payload_dict = json.loads(event["body"])
        elif method == "GET":
            payload_dict = event.get("queryStringParameters")
        else:
            return get_response(405, "Method Not Allowed")

        if "/free-call" == path:
            response_data = signer_object.signature_for_free_call(
                user_data=event["requestContext"],
                org_id=payload_dict["org_id"],
                service_id=payload_dict["service_id"],
            )

        elif "/state-service" == path:

            response_data = signer_object.signature_for_state_service(
                user_data=event["requestContext"],
                channel_id=payload_dict["channel_id"])

        elif "/regular-call" == path:

            response_data = signer_object.signature_for_regular_call(
                user_data=event["requestContext"],
                channel_id=payload_dict["channel_id"],
                nonce=payload_dict["nonce"],
                amount=payload_dict["amount"],
            )
            logger.info(response_data)
        else:
            return get_response(404, "Not Found")

        if response_data is None:
            err_msg = {
                "status": "failed",
                "error": "Bad Request",
                "api": event["path"],
                "payload": payload_dict,
                "network_id": NET_ID,
            }
            obj_util.report_slack(1, str(err_msg), SLACK_HOOK)
            response = get_response(500, err_msg)
        else:
            response = get_response(200, {
                "status": "success",
                "data": response_data
            })
    except Exception as e:
        err_msg = {
            "status": "failed",
            "error": repr(e),
            "api": event["path"],
            "payload": payload_dict,
            "network_id": NET_ID,
        }
        obj_util.report_slack(1, str(err_msg), SLACK_HOOK)
        response = get_response(500, err_msg)
        traceback.print_exc()
    return response


def get_response(status_code, message):
    return {
        "statusCode": status_code,
        "body": json.dumps(message),
        "headers": {
            "Content-Type": "application/json",
            "X-Requested-With": "*",
            "Access-Control-Allow-Headers":
            "Access-Control-Allow-Origin, Content-Type,X-Amz-Date,Authorization,X-Api-Key,x-requested-with",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET,OPTIONS,POST",
        },
    }
