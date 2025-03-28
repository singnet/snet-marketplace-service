import json

from common.constant import StatusCode, ResponseStatus, StatusDescription
from common.logger import get_logger
from common.repository import Repository
from common.utils import Utils, handle_exception_with_slack_notification, generate_lambda_response, make_response_body, \
    format_error_message
from wallets.config import NETWORKS, NETWORK_ID, SLACK_HOOK
from wallets.application.service.wallet_service import WalletService

NETWORKS_NAME = dict((NETWORKS[netId]['name'], netId) for netId in NETWORKS.keys())
repo = Repository(net_id=NETWORK_ID, NETWORKS=NETWORKS)
utils = Utils()
logger = get_logger(__name__)
wallet_service = WalletService(repo=repo)


@handle_exception_with_slack_notification(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger)
def delete_user_wallet(event, context):
    query_parameters = event["queryStringParameters"]
    username = query_parameters["username"]
    wallet_service.remove_user_wallet(username)
    return generate_lambda_response(StatusCode.CREATED, make_response_body(
        ResponseStatus.SUCCESS, "OK", {}
    ), cors_enabled=False)

def create_and_register_wallet(event, context):
    logger.info(f"Received request to create and register wallet: {event}")
    body = event.get('body', None)
    if body is None:
        logger.error("Body not found")
        return generate_lambda_response(400, StatusDescription.BAD_REQUEST)

    payload_dict = json.loads(body)
    if payload_dict.get('username', None) is None:
        logger.error("Username field in the request body not found")
        return generate_lambda_response(400, StatusDescription.BAD_REQUEST)

    try:
        response_data = wallet_service.create_and_register_wallet(username=payload_dict['username'])
        if response_data is None:
            error_message = format_error_message(status = "failed", error = StatusDescription.BAD_REQUEST,
                                                 payload = payload_dict, net_id = NETWORK_ID,
                                                 handler = "create_and_register_wallet")
            response = generate_lambda_response(500, error_message)
        else:
            response = generate_lambda_response(200, {"status": "success", "data": response_data})
    except Exception as e:
        error_message = format_error_message(status = "failed", error = StatusDescription.BAD_REQUEST,
                                             payload = payload_dict, net_id = NETWORK_ID,
                                             handler = "create_and_register_wallet")
        response = generate_lambda_response(500, error_message)

    return response

def get_wallets(event, context):
    logger.info(f"Received request to get wallets: {event}")

def register_wallet(event, context):
    logger.info(f"Received request to register wallet: {event}")

def channel_add_funds(event, context):
    logger.info(f"Received request to add funds to channel: {event}")

def set_default_wallet(event, context):
    logger.info(f"Received request to set default wallet: {event}")

def get_transactions_for_order(event, context):
    logger.info(f"Received request to get transactions for order: {event}")
