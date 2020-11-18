import traceback

from aws_xray_sdk.core import patch_all

from common.logger import get_logger
from common.repository import Repository
from common.utils import Utils
from orchestrator.config import NETWORKS, NETWORK_ID, SLACK_HOOK
from orchestrator.services.order_service import OrderService

patch_all()
obj_util = Utils()
repo = Repository(net_id=NETWORK_ID, NETWORKS=NETWORKS)
logger = get_logger(__name__)


def request_handler(event, context):
    try:
        order_service = OrderService(obj_repo=repo)
        response = order_service.cancel_order()
        logger.info(f"Response for update transaction status {response}")
        return "success"
    except Exception as e:
        error_message = "Error in updating channel transaction status \n"
        "NETWORK ID:" + str(NETWORK_ID) + "\n"
        "Error:" + repr(e)
        obj_util.report_slack(error_message, SLACK_HOOK)
        traceback.print_exc()
