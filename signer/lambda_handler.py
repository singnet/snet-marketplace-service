import json
import re
import traceback

from aws_xray_sdk.core import patch_all

from common.logger import get_logger
from common.utils import Utils, generate_lambda_response, handle_exception_with_slack_notification
from signer.config import NETWORK_ID, NET_ID, SLACK_HOOK
from signer.signers import Signer

patch_all()

obj_util = Utils()

logger = get_logger(__name__)

@handle_exception_with_slack_notification(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger)
def request_handler(event, context):
    logger.info("Signer::event: ", event)
    if "path" not in event:
        return generate_lambda_response(400, "Bad Request", cors_enabled=True)
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
            return generate_lambda_response(405, "Method Not Allowed", cors_enabled=True)

        if "/free-call" == path:
            response_data = signer_object.signature_for_free_call(
                user_data=event["requestContext"],
                org_id=payload_dict["org_id"],
                service_id=payload_dict["service_id"],
                group_id=payload_dict["group_id"]
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

        elif "/open-channel-for-third-party" == path:

            response_data = signer_object.signature_for_open_channel_for_third_party(
                recipient=payload_dict["recipient"], group_id=payload_dict['group_id'],
                amount_in_cogs=payload_dict["amount_in_cogs"], expiration=payload_dict["expiration"],
                message_nonce=payload_dict["message_nonce"],
                sender_private_key=payload_dict["signer_key"], executor_wallet_address=payload_dict["executor_wallet_address"])
        else:
            return generate_lambda_response(404, "Not Found", cors_enabled=True)
        logger.info("Signer::response_data: ", response_data)
        if response_data is None:
            err_msg = {
                "status": "failed",
                "error": "Bad Request",
                "api": event["path"],
                "payload": payload_dict,
                "network_id": NET_ID,
            }
            obj_util.report_slack(1, str(err_msg), SLACK_HOOK)
            response = generate_lambda_response(500, err_msg, cors_enabled=True)
        else:
            response = generate_lambda_response(200, {
                "status": "success",
                "data": response_data
            }, cors_enabled=True)
    except Exception as e:
        err_msg = {
            "status": "failed",
            "error": repr(e),
            "api": event["path"],
            "payload": payload_dict,
            "network_id": NET_ID,
        }
        obj_util.report_slack(1, str(err_msg), SLACK_HOOK)
        response = generate_lambda_response(500, err_msg, cors_enabled=True)
        traceback.print_exc()
    return response


@handle_exception_with_slack_notification(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger)
def free_call_token_handler(event, context):
    signer = Signer(net_id=NET_ID)
    payload_dict = event.get("queryStringParameters")
    email = event["requestContext"]["authorizer"]["claims"]["email"]
    org_id = payload_dict["org_id"],
    service_id = payload_dict["service_id"],
    group_id = payload_dict["group_id"]
    token_data = signer.token_for_free_call(email, org_id, service_id, group_id)

    return generate_lambda_response(200, {
        "status": "success",
        "data": token_data
    }, cors_enabled=True)
