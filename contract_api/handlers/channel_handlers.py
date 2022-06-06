import json
import traceback

from aws_xray_sdk.core import patch_all

from common.constant import StatusCode, ResponseStatus
from common.logger import get_logger
from common.repository import Repository
from common.utils import generate_lambda_response, validate_dict, Utils, make_response_body, \
    handle_exception_with_slack_notification
from contract_api.config import NETWORKS, SLACK_HOOK, NETWORK_ID
from contract_api.errors import Error
from contract_api.mpe import MPE

patch_all()
logger = get_logger(__name__)
repo = Repository(net_id=NETWORK_ID, NETWORKS=NETWORKS)
obj_mpe = MPE(obj_repo=repo)
utils = Utils()

@handle_exception_with_slack_notification(logger=logger, NETWORK_ID=NETWORK_ID, SLACK_HOOK=SLACK_HOOK)
def get_channels(event, context):
    logger.info("Received request to get channel details from user address")
    try:
        query_string_parameters = event["queryStringParameters"]
        if validate_dict(query_string_parameters, ["wallet_address"]):
            wallet_address = query_string_parameters["wallet_address"]
            logger.info(f"Fetched values from request wallet_address: {wallet_address}")
            response = obj_mpe.get_channels_by_user_address_v2(wallet_address)
            status_code = StatusCode.OK
        else:
            status_code = StatusCode.BAD_REQUEST
            response = "Bad Request"
            logger.error(response)
            logger.info(event)
    except Exception as e:
        logger.info(event)
        response = repr(e)
        utils.report_slack(str(response), SLACK_HOOK)
        logger.error(e)
        status_code = StatusCode.INTERNAL_SERVER_ERROR
    return generate_lambda_response(
        status_code=status_code,
        message=response,
        cors_enabled=True
    )

@handle_exception_with_slack_notification(logger=logger, NETWORK_ID=NETWORK_ID, SLACK_HOOK=SLACK_HOOK)
def get_channels_for_group(event, context):
    group_id = event['pathParameters']['groupId']
    channel_id = event['pathParameters']['channelId']
    response_data = obj_mpe.get_channel_data_by_group_id_and_channel_id(
        group_id=group_id, channel_id=channel_id)
    return generate_lambda_response(
        200, {"status": "success", "data": response_data}, cors_enabled=True)

@handle_exception_with_slack_notification(logger=logger, NETWORK_ID=NETWORK_ID, SLACK_HOOK=SLACK_HOOK)
def get_channels_old_api(event, context):
    payload_dict = event.get('queryStringParameters')
    user_address = payload_dict["user_address"]
    org_id = payload_dict.get("org_id", None)
    service_id = payload_dict.get("service_id", None)
    group_id = payload_dict.get("group_id", None)
    response_data = obj_mpe.get_channels(
        user_address=user_address,
        org_id=org_id,
        service_id=service_id,
        group_id=group_id
    )
    return generate_lambda_response(
        200, {"status": "success", "data": response_data}, cors_enabled=True)


def update_consumed_balance(event, context):
    logger.info("Received request to update consumed balance")
    try:
        path_parameters = event["pathParameters"]
        payload = json.loads(event["body"])
        if validate_dict(
                payload, ["OrganizationID", "ServiceID", "GroupID", "AuthorizedAmount",
                          "FullAmount", "ChannelId", "Nonce"]) \
                and "channel_id" in path_parameters:
            org_id = payload["OrganizationID"]
            service_id = payload["ServiceID"]
            group_id = payload["GroupID"]
            authorized_amount = payload["AuthorizedAmount"]
            full_amount = payload["FullAmount"]
            nonce = payload["Nonce"]
            channel_id = path_parameters["channel_id"]
            logger.info(f"Fetched values from request\n"
                        f"org_id: {org_id} group_id: {group_id} service_id: {service_id} "
                        f"authorized_amount: {authorized_amount} full_amount: {full_amount} nonce: {nonce}")
            response = obj_mpe.update_consumed_balance(channel_id, authorized_amount, full_amount, nonce)
            return generate_lambda_response(
                StatusCode.CREATED,
                make_response_body(ResponseStatus.SUCCESS, response, {}),
                cors_enabled=True
            )
        else:
            logger.error("Bad Request")
            logger.info(event)
            return generate_lambda_response(
                StatusCode.BAD_REQUEST,
                make_response_body(ResponseStatus.FAILED, "Bad Request", {}),
                cors_enabled=True
            )

    except Exception as e:
        response = "Failed to update consumed balance"
        logger.error(response)
        logger.info(event)
        logger.error(e)
        error = Error.handle_undefined_error(repr(e))
        utils.report_slack(str(error), SLACK_HOOK)
        traceback.print_exc()
        return generate_lambda_response(
            StatusCode.INTERNAL_SERVER_ERROR,
            make_response_body(ResponseStatus.FAILED, response, error),
            cors_enabled=True
        )
