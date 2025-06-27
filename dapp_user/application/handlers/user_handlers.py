from common.constant import StatusCode
from common.exception_handler import exception_handler, worker_exception_handler
from common.logger import get_logger
from common.request_context import RequestContext
from common.utils import generate_lambda_response
from dapp_user.application.schemas import (
    AddOrUpdateUserPreferencesRequest,
    CognitoUserPoolEvent,
    CreateUserServiceReviewRequest,
    DeleteUserRequest,
    GetUserFeedbackRequest,
    UpdateUserRequest,
)
from dapp_user.application.services.user_service import UserService
from dapp_user.constant import CognitoTriggerSource
from dapp_user.exceptions import UnauthorizedException

logger = get_logger(__name__)


__user_service = UserService()


@exception_handler(logger=logger)
def get_user_handler(event, context):
    req_ctx = RequestContext(event)

    response = __user_service.get_user(username=req_ctx.username)

    return generate_lambda_response(
        StatusCode.OK, {"status": "success", "data": response}, cors_enabled=True
    )


@exception_handler(logger=logger)
def add_or_update_user_preference_handler(event, context):
    req_ctx = RequestContext(event)

    request = AddOrUpdateUserPreferencesRequest.validate_event(event)

    response = __user_service.add_or_update_user_preference(
        username=req_ctx.username,
        request=request,
    )

    return generate_lambda_response(
        StatusCode.OK, {"status": "success", "data": response}, cors_enabled=True
    )


def update_user_handler(event, context):
    req_ctx = RequestContext(event)

    request = UpdateUserRequest.validate_event(event)

    response = __user_service.update_user(username=req_ctx.username, request=request)

    return generate_lambda_response(
        StatusCode.OK, {"status": "success", "data": response}, cors_enabled=True
    )


@exception_handler(logger=logger)
def get_user_preferences_handler(event, context):
    req_ctx = RequestContext(event)

    response = __user_service.get_user_preferences(username=req_ctx.username)

    return generate_lambda_response(
        StatusCode.OK, {"status": "success", "data": response}, cors_enabled=True
    )


@exception_handler(logger=logger)
def delete_user_handler(event, context):
    req_ctx = RequestContext(event)

    request = DeleteUserRequest.validate_event(event)

    if request.username and req_ctx.username != request.username:
        raise UnauthorizedException()

    response = __user_service.delete_user(req_ctx.username)

    return generate_lambda_response(
        StatusCode.OK, {"status": "success", "data": response}, cors_enabled=True
    )


@exception_handler(logger=logger)
def get_user_service_review_handler(event, context):
    req_ctx = RequestContext(event)

    request = GetUserFeedbackRequest.validate_event(event)

    response = __user_service.get_user_service_review(username=req_ctx.username, request=request)

    return generate_lambda_response(
        StatusCode.OK, {"status": "success", "data": response}, cors_enabled=True
    )


@exception_handler(logger=logger)
def create_user_review_handler(event, context):
    req_ctx = RequestContext(event)

    request = CreateUserServiceReviewRequest.validate_event(event)

    response = __user_service.create_user_review(
        username=req_ctx.username,
        request=request
    )

    return generate_lambda_response(
        StatusCode.OK, {"status": "success", "data": response}, cors_enabled=True
    )


@worker_exception_handler(logger=logger)
def post_aws_cognito_signup_handler(event, context):
    cognito_event = CognitoUserPoolEvent.model_validate(event)
    if cognito_event.trigger_source == CognitoTriggerSource.POST_CONFIRMATION:
        __user_service.register_user(cognito_event)
    return event


@worker_exception_handler(logger=logger)
def sync_users_handler(event, context):
    __user_service.sync_users()
