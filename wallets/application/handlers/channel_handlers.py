import json

from common.constant import StatusCode, ResponseStatus
from common.exception_handler import exception_handler
from common.logger import get_logger
from common.utils import validate_dict, generate_lambda_response
from wallets.config import NETWORK_ID, SLACK_HOOK
from wallets.exceptions import EXCEPTIONS, BadRequestException
from wallets.application.service.channel_service import ChannelService

logger = get_logger(__name__)
channel_service = ChannelService()


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger, EXCEPTIONS=EXCEPTIONS)
def create_channel(event, context):
    logger.info(f"Received request to initiate order: {event}")
    try:
        body = event.get('body', None)
        assert body is not None, "Body not found"
        payload_dict = json.loads(event["body"])
        required_fields = ["order_id", "sender", "signature", "r", "s", "v", "current_block_no",
                         "group_id", "org_id", "amount", "currency", "recipient", "amount_in_cogs"]
        assert validate_dict(payload_dict, required_fields, True), \
            f"Missing required fields. Required fields: {str(required_fields)}"
    except AssertionError as e:
        raise BadRequestException(str(e))

    logger.info(f"Payload for create channel: {payload_dict}")
    response_data = channel_service.open_channel_by_third_party(
        order_id=payload_dict['order_id'], sender=payload_dict['sender'], signature=payload_dict['signature'],
        r=payload_dict['r'], s=payload_dict['s'], v=payload_dict['v'], current_block_no=payload_dict['current_block_no'],
        group_id=payload_dict['group_id'], org_id=payload_dict["org_id"], recipient=payload_dict['recipient'],
        amount=payload_dict['amount'], currency=payload_dict['currency'],
        amount_in_cogs=payload_dict['amount_in_cogs']
    )
    response = generate_lambda_response(StatusCode.CREATED, {"status": ResponseStatus.SUCCESS, "data": response_data})

    return response


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger, EXCEPTIONS=EXCEPTIONS)
def record_create_channel_event(event, context):
    logger.info(f"Received request to initiate order: {event}")
    try:
        body = event.get('body', None)
        assert body is not None, "Body not found"
        payload_dict = json.loads(event["body"])
        required_fields = ["order_id", "sender", "signature", "r", "s", "v", "current_block_no",
                         "group_id", "org_id", "amount", "currency", "recipient", "amount_in_cogs"]
        assert validate_dict(payload_dict, required_fields, True), \
            f"Missing required fields. Required fields: {str(required_fields)}"
    except AssertionError as e:
        raise BadRequestException(str(e))

    logger.info(f"Payload for create channel: {payload_dict}")
    response_data = channel_service.record_create_channel_event(payload_dict)
    response = generate_lambda_response(StatusCode.CREATED, {"status": ResponseStatus.SUCCESS, "data": response_data})

    return response


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger, EXCEPTIONS=EXCEPTIONS)
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
        response_data = channel_service.get_channel_transactions_against_order_id(
            order_id = payload_dict["order_id"]
        )
    else:
        response_data = channel_service.get_transactions_from_username_recipient(
            username = username,
            group_id = group_id,
            org_id = org_id
        )
    response = generate_lambda_response(200, {"status": ResponseStatus.SUCCESS, "data": response_data})

    return response


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger, EXCEPTIONS=EXCEPTIONS)
def channel_add_funds(event, context):
    logger.info(f"Received request to add funds to channel: {event}")
    try:
        body = event.get('body', None)
        assert body is not None, "Body not found"
        payload_dict = json.loads(body)
        required_fields = ["org_id", "group_id", "channel_id", "sender", "recipient",
                           "order_id", "amount", "currency", "amount_in_cogs"]
        assert validate_dict(payload_dict, required_fields, True), \
            f"Missing required fields. Required fields: {str(required_fields)}"
    except AssertionError as e:
        raise BadRequestException(str(e))

    response_data = channel_service.add_funds_to_channel(**payload_dict)
    response = generate_lambda_response(200, {"status": ResponseStatus.SUCCESS, "data": response_data})

    return response


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger, EXCEPTIONS=EXCEPTIONS)
def update_channel_transaction_status(event, context):
    channel_service.manage_channel_transaction_status()
    return


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger, EXCEPTIONS=EXCEPTIONS)
def open_channel_by_third_party(event, context):
    logger.info(f"Open channel by third party {event}")
    channel_service.manage_create_channel_event()
    return {}