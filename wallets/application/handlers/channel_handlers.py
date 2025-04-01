import json
import traceback

from common.constant import StatusCode, ResponseStatus, TransactionStatus
from common.exception_handler import exception_handler
from common.logger import get_logger
from common.utils import Utils, validate_dict, generate_lambda_response, make_response_body
from wallets.config import NETWORK_ID, SLACK_HOOK
from wallets.domain.models.channel_transaction_history import ChannelTransactionHistoryModel
from wallets.error import Error
from wallets.exceptions import EXCEPTIONS, BadRequestException
from wallets.infrastructure.repositories.channel_repository import ChannelRepository
from wallets.application.service.manage_create_channel_event import ManageCreateChannelEvent
from wallets.application.service.wallet_service import WalletService


logger = get_logger(__name__)
wallet_service = WalletService()


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
    response_data = wallet_service.open_channel_by_third_party(
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
    ChannelRepository().add_channel_transaction_history_record(ChannelTransactionHistoryModel(
        order_id=payload_dict["order_id"],
        amount=payload_dict["amount"],
        currency=payload_dict["currency"],
        type=payload_dict.get("type", "openChannelByThirdParty"),
        address=payload_dict["sender"],
        recipient=payload_dict["recipient"],
        signature=payload_dict["signature"],
        org_id=payload_dict["org_id"],
        group_id=payload_dict["group_id"],
        request_parameters=payload_dict.get("request_parameters", ""),
        transaction_hash=payload_dict.get("transaction_hash", ""),
        status=TransactionStatus.NOT_SUBMITTED
    ))
    response_data = wallet_service.record_create_channel_event(payload_dict)
    response = generate_lambda_response(StatusCode.CREATED, {"status": ResponseStatus.SUCCESS, "data": response_data})

    return response


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger, EXCEPTIONS=EXCEPTIONS)
def open_channel_by_third_party(event, context):
    logger.info(f"Open channel by third party {event}")
    ManageCreateChannelEvent().manage_create_channel_event()
    return {}
