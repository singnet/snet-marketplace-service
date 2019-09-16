import traceback

from common.repository import Repository
from common.utils import extract_payload
from common.utils import format_error_message
from common.utils import generate_lambda_response
from common.utils import Utils
from common.utils import validate_dict
from wallets.config import NETWORK_ID
from wallets.config import NETWORKS
from wallets.wallet_service import WalletService

NETWORKS_NAME = dict((NETWORKS[netId]["name"], netId) for netId in NETWORKS.keys())
db = dict((netId, Repository(net_id=netId)) for netId in NETWORKS.keys())
obj_util = Utils()


def route_path(path, method, payload_dict):
    obj_wallet_manager = WalletService(obj_repo=db[NETWORK_ID])
    path_exist = True
    if "/wallet" == path:
        response_data = obj_wallet_manager.create_and_register_wallet()

    elif "/wallet/channel" == path and method == "POST":
        response_data = obj_wallet_manager.open_channel_by_third_party(
            order_id=payload_dict["order_id"],
            sender=payload_dict["sender"],
            sender_private_key=payload_dict["sender_private_key"],
            group_id=payload_dict["group_id"],
            amount=payload_dict["amount"],
            currency=payload_dict["currency"],
            recipient=payload_dict["recipient"],
        )

    elif "/wallet/channel/deposit" == path and method == "GET":
        response_data = obj_wallet_manager.add_funds_to_channel(
            order_id=payload_dict["order_id"],
            amount=payload_dict["amount"],
            currency=payload_dict["currency"],
        )

    elif "/wallet/status" == path:
        response_data = obj_wallet_manager.update_wallet_status(
            address=payload_dict["address"]
        )
    else:
        path_exist = False

    return path_exist, response_data


def request_handler(event, context):
    try:
        valid_event = validate_dict(event=event, required_keys=required_keys)
        if not valid_event:
            return generate_lambda_response(400, "Bad Request")

        path = event["path"].lower()
        method = event["httpMethod"]

        method_found, payload_dict = extract_payload(method=method, event=event)
        if not method_found:
            return generate_lambda_response(405, "Method Not Allowed")

        path_exist, response_data = route_path(
            path=path, method=method, payload_dict=payload_dict
        )
        if not path_exist:
            return generate_lambda_response(404, "Not Found")

        if response_data is None:
            error_message = format_error_message(
                status="failed",
                error="Bad Request",
                resource=path,
                payload=payload_dict,
                net_id=NETWORK_ID,
            )
            obj_util.report_slack(1, error_message)
            response = generate_lambda_response(500, error_message)
        else:
            response = generate_lambda_response(
                200, {"status": "success", "data": response_data}
            )
    except Exception as e:
        error_message = format_error_message(
            status="failed",
            error="Bad Request",
            resource=path,
            payload=payload_dict,
            net_id=NETWORK_ID,
        )
        obj_util.report_slack(1, error_message)
        response = generate_lambda_response(500, error_message)
        traceback.print_exc()
    return response
