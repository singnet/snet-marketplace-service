import json
import traceback


from common.constant import StatusCode, ResponseStatus
from common.logger import get_logger
from common.repository import Repository
from common.utils import (
    generate_lambda_response,
    validate_dict,
    Utils,
    make_response_body
)
from common.exception_handler import exception_handler
from contract_api.config import NETWORKS, NETWORK_ID
from contract_api.errors import Error
from contract_api.mpe import MPE

logger = get_logger(__name__)
repo = Repository(net_id=NETWORK_ID, NETWORKS=NETWORKS)
obj_mpe = MPE(obj_repo=repo)
utils = Utils()

@exception_handler(logger=logger)
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
        logger.error(e)
        status_code = StatusCode.INTERNAL_SERVER_ERROR
    return generate_lambda_response(
        status_code=status_code,
        message=response,
        cors_enabled=True
    )

@exception_handler(logger=logger)
def get_channels_for_group(event, context):
    group_id = event['pathParameters']['groupId']
    channel_id = event['pathParameters']['channelId']
    response_data = obj_mpe.get_channel_data_by_group_id_and_channel_id(
        group_id=group_id, channel_id=channel_id)
    return generate_lambda_response(
        200, {"status": "success", "data": response_data}, cors_enabled=True)

@exception_handler(logger=logger)
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
    """
    for METAMASK sender wallet: channel_id, signed_amount
    for GENERAL sender wallet: channel_id, org_id, service_id
    """
    logger.info(f"Received request to update consumed balance: {event}")
    try:
        path_parameters = event["pathParameters"]
        channel_id = path_parameters.get("channel_id", None)
        payload = json.loads(event["body"])
        if channel_id is not None:
            response = None
            if "signed_amount" in payload:
                signed_amount = payload["signed_amount"]
                response = obj_mpe.update_consumed_balance(channel_id,
                                                           signed_amount = signed_amount)
            elif "org_id" in payload and "service_id" in payload:
                org_id = payload["org_id"]
                service_id = payload["service_id"]
                response = obj_mpe.update_consumed_balance(channel_id,
                                                           org_id = org_id,
                                                           service_id = service_id)
            if response is not None:
                return generate_lambda_response(
                    StatusCode.CREATED,
                    make_response_body(ResponseStatus.SUCCESS, response, {}),
                    cors_enabled=True
                )

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
        traceback.print_exc()
        return generate_lambda_response(
            StatusCode.INTERNAL_SERVER_ERROR,
            make_response_body(ResponseStatus.FAILED, response, error),
            cors_enabled=True
        )
