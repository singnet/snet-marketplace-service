from verification.services.passbase_verification_service import PassbaseVerificationService
from common.utils import generate_lambda_response, handle_exception_with_slack_notification
from common.constant import StatusCode, ResponseStatus
from aws_xray_sdk.core import patch_all
from common.logger import get_logger
from verification.config import SLACK_HOOK, NETWORK_ID

logger = get_logger(__name__)

passbase_verification_service = PassbaseVerificationService()


@handle_exception_with_slack_notification(logger=logger, SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID)
def get_all_authentication(event, context):
    limit = event["pathParameters"]["limit"]
    offset = event["pathParameters"]["offset"]
    from_created_at = event["pathParameters"]["from_created_at"]
    to_created_at = event["pathParameters"]["to_created_at"]

    response = passbase_verification_service.get_all_authentications(
        limit, offset, from_created_at, to_created_at)

    return generate_lambda_response(StatusCode.OK, {"status": ResponseStatus.SUCCESS, "data": response})
