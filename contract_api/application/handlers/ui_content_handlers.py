from common.constant import StatusCode
from common.exception_handler import exception_handler
from common.logger import get_logger
from common.utils import generate_lambda_response
from contract_api.config import SLACK_HOOK
from contract_api.services.banner_service import BannerService

logger = get_logger(__name__)


@exception_handler(SLACK_HOOK=SLACK_HOOK, logger = logger)
def get_marketplace_carousel(event, context):
    carousel = BannerService().get_banners()
    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": carousel, "error": {}}, cors_enabled=True
    )
