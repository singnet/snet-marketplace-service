import traceback
from enum import Enum

from common.constant import StatusDescription, ErrorDescription
from common.logger import get_logger
from common.repository import Repository
from common.utils import Utils, generate_lambda_response, extract_payload, validate_dict, format_error_message
from wallets.config import NETWORKS, NETWORK_ID, WALLET_TYPES_ALLOWED
from wallets.config import SLACK_HOOK
from wallets.constant import REQUIRED_KEYS_FOR_LAMBDA_EVENT
from wallets.service.wallet_service import WalletService
from wallets.wallet import Wallet

NETWORKS_NAME = dict((NETWORKS[netId]['name'], netId) for netId in NETWORKS.keys())
db = dict((netId, Repository(net_id=netId, NETWORKS=NETWORKS)) for netId in NETWORKS.keys())
util = Utils()
logger = get_logger(__name__)


class WalletStatus(Enum):
    ACTIVE = 1


def route_path(path, method, payload_dict, path_parameters):
    wallet_manager = WalletService(repo=db[NETWORK_ID])
    path_exist = True
    response_data = None

    if "/wallet" == path and method == "POST":
        response_data = wallet_manager.create_and_register_wallet(
            username=payload_dict["username"]
        )

    elif "/wallet" == path and method == "GET":
        username = payload_dict["username"]
        response_data = wallet_manager.get_wallet_details(username=username)

    elif "/wallet/channel/deposit" == path and method == 'POST':
        response_data = wallet_manager.add_funds_to_channel(org_id=payload_dict['org_id'],
                                                                group_id=payload_dict['group_id'],
                                                                channel_id=payload_dict['channel_id'],
                                                                sender=payload_dict['sender'],
                                                                recipient=payload_dict['recipient'],
                                                                order_id=payload_dict['order_id'],
                                                                amount=payload_dict['amount'],
                                                                currency=payload_dict['currency'],
                                                                amount_in_cogs=payload_dict['amount_in_cogs'])

    elif "/wallet/status" == path:
        response_data = wallet_manager.set_default_wallet(username=payload_dict["username"],
                                                              address=payload_dict['address'])

    elif "/wallet/channel/transactions" == path and method == 'GET':
        order_id = payload_dict.get('order_id', None)
        username = payload_dict.get('username', None)
        org_id = payload_dict.get('org_id', None)
        group_id = payload_dict.get('group_id', None)

        if order_id is not None:
            logger.info(f"Received request to fetch transactions against order_id: {order_id}")

            response_data = wallet_manager.get_channel_transactions_against_order_id(
                order_id=payload_dict["order_id"])
        elif username is not None and group_id is not None and org_id is not None:
            logger.info(f"Received request to fetch transactions for username: {username} "
                        f"group_id: {group_id} "
                        f"org_id: {org_id}")

            response_data = wallet_manager.get_transactions_from_username_recipient(
                username=username, group_id=group_id, org_id=org_id)
        else:
            raise Exception("Bad Parameters")

    elif "/wallet/register" == path:
        username = payload_dict["username"]
        status = WalletStatus.ACTIVE.value
        wallet_address = payload_dict["address"]
        wallet_type = payload_dict['type']

        if wallet_type not in WALLET_TYPES_ALLOWED:
            raise Exception("Wallet type invalid")

        wallet_manager.register_wallet(wallet_address, wallet_type, status, username)
        response_data = []

    else:
        path_exist = False

    return path_exist, response_data


def request_handler(event, context):
    logger.info(f"Wallets::event: {event}")
    try:
        valid_event = validate_dict(data_dict=event, required_keys=REQUIRED_KEYS_FOR_LAMBDA_EVENT)
        if not valid_event:
            return generate_lambda_response(400, StatusDescription.BAD_REQUEST)

        path = event['path'].lower()
        method = event['httpMethod']
        method_found, path_parameters, payload_dict = extract_payload(method=method, event=event)
        if not method_found:
            return generate_lambda_response(405, ErrorDescription.METHOD_NOT_ALLOWED)

        path_exist, response_data = route_path(
            path=path, method=method,
            payload_dict=payload_dict,
            path_parameters=path_parameters
        )

        if not path_exist:
            return generate_lambda_response(404, ErrorDescription.NOT_FOUND)

        if response_data is None:
            error_message = format_error_message(status="failed", error=StatusDescription.BAD_REQUEST, resource=path,
                                                 payload=payload_dict, net_id=NETWORK_ID)
            util.report_slack(error_message, SLACK_HOOK)
            response = generate_lambda_response(500, error_message)
        else:
            response = generate_lambda_response(200, {"status": "success", "data": response_data})
    except Exception as e:
        error_message = format_error_message(status="failed", error=StatusDescription.BAD_REQUEST, resource=path,
                                             payload=payload_dict, net_id=NETWORK_ID)
        util.report_slack(error_message, SLACK_HOOK)
        response = generate_lambda_response(500, error_message)
        traceback.print_exc()
    return response
