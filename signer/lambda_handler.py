import json
import re
import traceback
from urllib.parse import unquote

from aws_xray_sdk.core import patch_all

from common.constant import StatusCode
from common.exceptions import BadRequestException
from common.logger import get_logger
from common.utils import Utils, generate_lambda_response, handle_exception_with_slack_notification
from signer.config import NETWORK_ID, NET_ID, SIGNER_ADDRESS, SLACK_HOOK
from signer.signers import Signer

patch_all()

obj_util = Utils()

logger = get_logger(__name__)

@handle_exception_with_slack_notification(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger)
def request_handler(event, context):
    logger.info(f"Signer::event: {event}")
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
                sender_private_key=payload_dict["signer_key"],
                executor_wallet_address=payload_dict["executor_wallet_address"])
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
            obj_util.report_slack(str(err_msg), SLACK_HOOK)
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
        obj_util.report_slack(str(err_msg), SLACK_HOOK)
        response = generate_lambda_response(500, err_msg, cors_enabled=True)
        traceback.print_exc()
    return response


@handle_exception_with_slack_notification(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger)
def free_call_token_handler(event, context):
    logger.info(f"Request for freecall token event {event}")
    signer = Signer(net_id=NET_ID)
    payload_dict = event.get("queryStringParameters")
    email = event["requestContext"]["authorizer"]["claims"]["email"]
    org_id = payload_dict["org_id"]
    service_id = payload_dict["service_id"]
    group_id = unquote(payload_dict["group_id"])
    public_key = payload_dict["public_key"]
    logger.info(
        f"Free call token generation for email:{email} org_id:{org_id} service_id:{service_id} group_id:{group_id} public_key:{public_key}")

    token_data = signer.token_to_make_free_call(email, org_id, service_id, group_id, public_key)


    return generate_lambda_response(200, {
        "status": "success",
        "data": token_data
    }, cors_enabled=True)


@handle_exception_with_slack_notification(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger)
def get_free_call_signer_address(event, context):
    username = event["requestContext"]["authorizer"]["claims"]["email"]
    query_string_parameters = event["queryStringParameters"]
    if "org_id" not in query_string_parameters and "service_id" not in query_string_parameters and "group_id" not in query_string_parameters:
        raise BadRequestException()
    response = {"free_call_signer_address": SIGNER_ADDRESS}
    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@handle_exception_with_slack_notification(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger)
def signature_to_get_free_call_from_daemon_handler(event, context):
    logger.info(f"Request for freecall token event {event}")
    signer = Signer(net_id=NET_ID)
    payload_dict = event.get("queryStringParameters")
    email = payload_dict["username"]
    org_id = payload_dict["org_id"]
    service_id = payload_dict["service_id"]
    group_id = unquote(payload_dict["group_id"])
    #public_key = payload_dict["public_key"]
    logger.info(
        f"Free call signature for daemon  generation for email:{email} org_id:{org_id} service_id:{service_id} group_id:{group_id}")

    token_to_get_free_call, expiry_date_block, signature, current_block_number, daemon_endpoint ,free_calls_allowed= signer.token_to_get_free_call(email, org_id, service_id, group_id)
    signature_data = {
        "token_to_get_free_call": token_to_get_free_call.hex(),
        "expiry_date_block": expiry_date_block,
        "signature": signature.hex(),
        "current_block_number": current_block_number, "daemon_endpoint": daemon_endpoint ,"free_calls_allowed": free_calls_allowed
    }


    return generate_lambda_response(200, {
        "status": "success",
        "data": signature_data
    }, cors_enabled=True)
