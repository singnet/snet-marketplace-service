import traceback

from common.logger import get_logger
from common.repository import Repository
from common.utils import Utils
from orchestrator.config import NETWORKS, NETWORK_ID
from orchestrator.services.order_service import OrderService

obj_util = Utils()
repo = Repository(net_id=NETWORK_ID, NETWORKS=NETWORKS)
logger = get_logger(__name__)


def request_handler(event, context):
    try:
        order_service = OrderService(obj_repo=repo)
        response = order_service.cancel_order()
        logger.info(f"Response for update transaction status {response}")
        return "success"
    except Exception:
        traceback.print_exc()
