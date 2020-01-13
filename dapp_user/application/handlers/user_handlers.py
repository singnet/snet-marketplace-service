import json

from common.constant import StatusCode
from dapp_user.exceptions import BadRequestException
from common.logger import get_logger
from common.utils import validate_dict_list, handle_exception_with_slack_notification, generate_lambda_response
from dapp_user.config import SLACK_HOOK, NETWORK_ID
from dapp_user.domain.services.user_service import UserService

logger = get_logger(__name__)


@handle_exception_with_slack_notification(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger)
def add_or_update_user_preference(event, context):
    payload = json.loads(event["body"])
    username = event["requestContext"]["authorizer"]["claims"]["email"]
    required_keys = ["communication_type", "preference_type", "source", "status"]
    if not validate_dict_list(payload, required_keys):
        raise BadRequestException()
    user_service = UserService()
    response = user_service.add_or_update_user_preference(payload=payload, username=username)

    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@handle_exception_with_slack_notification(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger)
def get_user_preference(event, context):
    username = event["requestContext"]["authorizer"]["claims"]["email"]
    user_service = UserService()
    response = user_service.get_user_preference(username=username)
    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@handle_exception_with_slack_notification(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger)
def delete_user(event, context):
    username = event["requestContext"]["authorizer"]["claims"]["email"]
    user_service = UserService()
    response = user_service.delete_user(username=username)
    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )
