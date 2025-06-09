import traceback
import re
from common.repository import Repository
from common.logger import get_logger
from common.utils import extract_payload
from common.utils import format_error_message
from common.utils import generate_lambda_response
from common.utils import Utils
from common.utils import validate_dict
from orchestrator.config import NETWORK_ID
from orchestrator.config import NETWORKS
from orchestrator.constant import REQUIRED_KEYS_FOR_LAMBDA_EVENT
from orchestrator.services.order_service import OrderService
from orchestrator.services.wallet_service import WalletService


NETWORKS_NAME = dict(
    (NETWORKS[netId]["name"], netId) for netId in NETWORKS.keys())
db = dict((netId, Repository(net_id=netId, NETWORKS=NETWORKS)) for netId in NETWORKS.keys())
obj_util = Utils()
logger = get_logger(__name__)

def route_path(path, method, payload_dict, request_context, path_parameters):
    obj_order_service = OrderService(obj_repo=db[NETWORK_ID])
    path_exist = True
    response_data = None

    if "/wallet" == path:
        username = request_context["authorizer"]["claims"]["email"]
        logger.info(f"Received request to get wallets for user:{username}")
        response_data = WalletService().get_wallets(username)

    elif "/wallet/channel" == path and method == 'GET':
        org_id = payload_dict["org_id"]
        username = request_context["authorizer"]["claims"]["email"]
        group_id = payload_dict["group_id"]
        response_data = WalletService().get_channel_details(username, org_id, group_id)

    elif re.match("(\/order\/)[^\/]*[/]{0,1}$", path):
        """ Format /order/{orderId} """
        username = request_context["authorizer"]["claims"]["email"]
        order_id = path_parameters["order_id"]
        response_data = obj_order_service.get_order_details_by_order_id(username=username, order_id=order_id)

    elif "/wallet/register" == path and method == "POST":
        username = request_context["authorizer"]["claims"]["email"]
        response_data = WalletService().register_wallet(username=username, wallet_details=payload_dict)

    elif "/wallet/status" == path and method == "POST":
        username = request_context["authorizer"]["claims"]["email"]
        response_data = WalletService().set_default_wallet(username=username, address=payload_dict["address"])

    else:
        path_exist = False

    return path_exist, response_data


def request_handler(event, context):
    logger.info(f"Orchestrator::event: {event}")
    try:
        valid_event = validate_dict(
            data_dict=event, required_keys=REQUIRED_KEYS_FOR_LAMBDA_EVENT)
        if not valid_event:
            return generate_lambda_response(400, "Bad Request", cors_enabled=True)

        path = event["path"].lower()
        path = re.sub(r"^(\/orchestrator)", "", path)
        method = event["httpMethod"]

        method_found, path_parameters, payload_dict = extract_payload(
            method=method, event=event)
        if not method_found:
            return generate_lambda_response(405, "Method Not Allowed", cors_enabled=True)

        path_exist, response_data = route_path(
            path=path,
            method=method,
            payload_dict=payload_dict,
            request_context=event.get("requestContext", None),
            path_parameters=path_parameters
        )
        if not path_exist:
            return generate_lambda_response(404, "Not Found", cors_enabled=True)
        logger.info(f"Orchestrator::response_data: {response_data}")
        if response_data is None:
            error_message = format_error_message(
                status="failed",
                error="Bad Request",
                resource=path,
                payload=payload_dict,
                net_id=NETWORK_ID,
            )
            response = generate_lambda_response(500, error_message, cors_enabled=True)
        else:
            response = generate_lambda_response(200, {
                "status": "success",
                "data": response_data
            }, cors_enabled=True)
    except Exception as e:
        error_message = format_error_message(
            status="failed",
            error=repr(e),
            resource=path,
            payload=payload_dict,
            net_id=NETWORK_ID,
        )
        response = generate_lambda_response(500, error_message, cors_enabled=True)
        traceback.print_exc()
    return response
