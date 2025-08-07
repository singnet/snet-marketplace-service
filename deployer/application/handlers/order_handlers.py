from common.exception_handler import exception_handler
from common.logger import get_logger

logger = get_logger(__name__)


@exception_handler(logger=logger)
def initiate_order(event, context):
    pass


@exception_handler(logger=logger)
def get_order(event, context):
    pass

