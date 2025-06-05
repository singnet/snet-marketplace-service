import json
import sys
import traceback
from common.constant import StatusCode
from common.logger import get_logger
from common.utils import validate_dict_list, handle_exception_with_slack_notification, generate_lambda_response
from dapp_user.exceptions import BadRequestException
from dapp_user.config import SLACK_HOOK, NETWORK_ID
from dapp_user.domain.services.user_service import UserService
from common.utils import Utils

logger = get_logger(__name__)


@handle_exception_with_slack_notification(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger)
def add_or_update_user_preference(event, context):
    logger.debug(f"add_or_update_user_preference event {event}")
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


def register_user_post_aws_cognito_signup(event, context):
    try:
        logger.info(f"Post aws cognito sign up event {event}")
        user_service = UserService()
        if event['triggerSource'] == "PostConfirmation_ConfirmSignUp":
            user_service.register_user(user_attribute=event["request"]["userAttributes"],
                                       client_id=event["callerContext"]["clientId"])
    except Exception as e:
        error_message = f"Error Reported! \n" \
                        f"network_id: {NETWORK_ID}\n" \
                        f"event: {event['triggerSource']}, \n" \
                        f"handler: register_user_post_aws_cognito_signup \n" \
                        f"error_description: \n"
        exc_type, exc_obj, exc_tb = sys.exc_info()
        exc_tb_lines = traceback.format_tb(exc_tb)
        error_message = error_message + str(e)+ "\n"
        logger.exception(error_message)
        slack_message = error_message
        for exc_lines in exc_tb_lines:
            slack_message = slack_message + exc_lines
        slack_message = f"```{slack_message}```"
        Utils().report_slack(slack_msg=slack_message, SLACK_HOOK=SLACK_HOOK)
    return event
