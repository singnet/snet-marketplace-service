import json

from common.constant import StatusCode, ResponseStatus
from common.exception_handler import exception_handler
from common.logger import get_logger
from common.utils import handle_exception_with_slack_notification, generate_lambda_response, make_response_body, \
    validate_dict
from wallets.config import NETWORK_ID, SLACK_HOOK
from wallets.application.service.wallet_service import WalletService
from wallets.exceptions import BadRequestException, EXCEPTIONS

logger = get_logger(__name__)
wallet_service = WalletService()


@handle_exception_with_slack_notification(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger)
def delete_user_wallet(event, context):
    query_parameters = event["queryStringParameters"]
    username = query_parameters["username"]
    wallet_service.remove_user_wallet(username)
    return generate_lambda_response(StatusCode.CREATED, make_response_body(
        ResponseStatus.SUCCESS, "OK", {}
    ), cors_enabled=False)


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger, EXCEPTIONS=EXCEPTIONS)
def create_and_register_wallet(event, context):
    logger.info(f"Received request to create and register wallet: {event}")
    try:
        body = event.get('body', None)
        assert body is not None, "Body not found"
        payload_dict = json.loads(body)
        assert payload_dict.get('username', None) is not None, "'username' field in the request body not found"
    except AssertionError as e:
        raise BadRequestException(str(e))

    response_data = wallet_service.create_and_register_wallet(username=payload_dict['username'])
    response = generate_lambda_response(200, {"status": "success", "data": response_data})

    return response


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger, EXCEPTIONS=EXCEPTIONS)
def get_wallets(event, context):
    logger.info(f"Received request to get wallets: {event}")
    try:
        body = event.get('body', None)
        assert body is not None, "Body not found"
        payload_dict = json.loads(body)
        assert payload_dict.get('username', None) is not None, "'username' field in the request body not found"
    except AssertionError as e:
        raise BadRequestException(str(e))

    response_data = wallet_service.get_wallet_details(username = payload_dict['username'])
    response = generate_lambda_response(200, {"status": "success", "data": response_data})

    return response


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger, EXCEPTIONS=EXCEPTIONS)
def register_wallet(event, context):
    logger.info(f"Received request to register wallet: {event}")
    try:
        body = event.get('body', None)
        assert body is not None, "Body not found"
        payload_dict = json.loads(body)
        assert payload_dict.get('username', None) is not None, "'username' field in the request body not found"
        assert payload_dict.get('address', None) is not None, "'address' field in the request body not found"
        assert payload_dict.get('type', None) is not None, "'type' field in the request body not found"
    except AssertionError as e:
        raise BadRequestException(str(e))

    status = 1 # ACTIVE
    response_data = wallet_service.register_wallet(
        payload_dict["address"],
        payload_dict["type"],
        status,
        payload_dict['username']
    )
    response = generate_lambda_response(200, {"status": "success", "data": response_data})

    return response


def channel_add_funds(event, context):
    logger.info(f"Received request to add funds to channel: {event}")
    try:
        body = event.get('body', None)
        assert body is not None, "Body not found"
        payload_dict = json.loads(body)
    except AssertionError as e:
        raise BadRequestException(str(e))

    required_fields = ["org_id", "group_id", "channel_id", "sender", "recipient",
                       "order_id", "amount", "currency", "amount_in_cogs"]
    if not validate_dict(payload_dict, required_fields, True):
        raise BadRequestException("Missing required fields")

    response_data = wallet_service.add_funds_to_channel(**payload_dict)
    response = generate_lambda_response(200, {"status": "success", "data": response_data})

    return response


def set_default_wallet(event, context):
    logger.info(f"Received request to set default wallet: {event}")
    try:
        body = event.get('body', None)
        assert body is not None, "Body not found"
        payload_dict = json.loads(body)
        assert payload_dict.get('username', None) is not None, "'username' field in the request body not found"
        assert payload_dict.get('address', None) is not None, "'address' field in the request body not found"
    except AssertionError as e:
        raise BadRequestException(str(e))

    response_data = wallet_service.set_default_wallet(
        payload_dict["username"],
        payload_dict["address"]
    )
    response = generate_lambda_response(200, {"status": "success", "data": response_data})

    return response


def get_transactions_for_order(event, context):
    logger.info(f"Received request to get transactions for order: {event}")
    try:
        body = event.get('body', None)
        assert body is not None, "Body not found"
        payload_dict = json.loads(body)
        order_id = payload_dict.get('order_id', None)
        username = payload_dict.get('username', None)
        org_id = payload_dict.get('org_id', None)
        group_id = payload_dict.get('group_id', None)
        assert (order_id is not None) or (username is not None and org_id is not None and group_id is not None), \
            "Body must contain either 'order_id' or 'username' and 'org_id' and 'group_id'"
    except AssertionError as e:
        raise BadRequestException(str(e))

    if order_id is not None:
        response_data = wallet_service.get_channel_transactions_against_order_id(
            order_id = payload_dict["order_id"]
        )
    elif username is not None and group_id is not None and org_id is not None:
        response_data = wallet_service.get_transactions_from_username_recipient(
            username = username,
            group_id = group_id,
            org_id = org_id
        )
    response = generate_lambda_response(200, {"status": "success", "data": response_data})

    return response

