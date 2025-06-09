import json
from common.constant import StatusCode
from common.logger import get_logger
from common.utils import validate_dict_list, generate_lambda_response
from common.exception_handler import exception_handler
from common.exceptions import BadRequestException
from dapp_user.config import NETWORK_ID
from dapp_user.domain.services.user_service import UserService

logger = get_logger(__name__)


@exception_handler(logger=logger)
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


@exception_handler(logger=logger)
def get_user_preference(event, context):
    username = event["requestContext"]["authorizer"]["claims"]["email"]
    user_service = UserService()
    response = user_service.get_user_preference(username=username)
    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@exception_handler(logger=logger)
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
        error_message = error_message + str(e)+ "\n"
        logger.exception(error_message)
    return event
