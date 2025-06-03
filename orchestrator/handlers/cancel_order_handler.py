import traceback

from common.logger import get_logger
from common.repository import Repository
from common.utils import Utils
from common.utils import format_error_message
from common.utils import generate_lambda_response
from common.utils import validate_dict
from orchestrator.config import NETWORKS
from orchestrator.config import NETWORK_ID
from orchestrator.config import SLACK_HOOK
from orchestrator.services.order_service import OrderService

REQUIRED_KEYS_FOR_CANCEL_ORDER_EVENT = ["pathParameters"]
repo = Repository(net_id=NETWORK_ID, NETWORKS=NETWORKS)
obj_util = Utils()
logger = get_logger(__name__)


def request_handler(event, context):
    try:
        valid_event = validate_dict(
            data_dict=event, required_keys=REQUIRED_KEYS_FOR_CANCEL_ORDER_EVENT)
        if not valid_event:
            return generate_lambda_response(400, "Bad Request", cors_enabled=True)

        path_parameters = event.get("pathParameters", None)

        order_service = OrderService(obj_repo=repo)
        cancel_order_status = order_service.cancel_order_for_given_order_id(order_id=path_parameters["order_id"])
        response = generate_lambda_response(200, {"status": "success", "data": cancel_order_status}, cors_enabled=True)
    except Exception as e:
        error_message = format_error_message(
            status="failed",
            error=repr(e),
            payload=event,
            net_id=NETWORK_ID,
            handler="cancel_order_handler"
        )
        obj_util.report_slack(error_message, SLACK_HOOK)
        response = generate_lambda_response(500, error_message, cors_enabled=True)
        traceback.print_exc()
    return response
