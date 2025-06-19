from common.constant import StatusCode
from common.exception_handler import exception_handler
from common.logger import get_logger
from common.request_context import RequestContext
from common.utils import generate_lambda_response
from dapp_user.application.schemas import (
    AddOrUpdateUserPreferencesRequest,
    CognitoUserPoolEvent,
    CreateUserServiceReviewRequest,
    DeleteUserRequest,
    GetUserFeedbackRequest,
    UpdateUserAlertRequest,
)
from dapp_user.application.services.user_service import UserService
from dapp_user.exceptions import UnauthorizedException

logger = get_logger(__name__)


@exception_handler(logger=logger)
def get_user(event, context):
    req_ctx = RequestContext(event)

    response = UserService().get_user(username=req_ctx.username)

    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@exception_handler(logger=logger)
def add_or_update_user_preference(event, context):
    req_ctx = RequestContext(event)
    
    request = AddOrUpdateUserPreferencesRequest.validate_event(event)

    response = UserService().add_or_update_user_preference(
        username=req_ctx.username, request=request,
    )

    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


def update_user_alerts(event, context):
    req_ctx = RequestContext(event)

    request = UpdateUserAlertRequest.validate_event(event)

    response = UserService().update_user_alerts(username=req_ctx.username, request=request)

    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@exception_handler(logger=logger)
def get_user_preferences(event, context):
    req_ctx = RequestContext(event)

    response = UserService().get_user_preferences(username=req_ctx.username)

    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@exception_handler(logger=logger)
def delete_user(event, context):
    req_ctx = RequestContext(event)

    request = DeleteUserRequest.validate_event(event)

    if req_ctx.username != request.username:
        raise UnauthorizedException()

    response = UserService().delete_user(request.username)

    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response},
        cors_enabled=True
    )


@exception_handler(logger=logger)
def get_user_feedback(event, context):
    req_ctx = RequestContext(event)

    request = GetUserFeedbackRequest.validate_event(event)

    response = UserService().get_user_feedback(
        username=req_ctx.username, request=request
    )

    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@exception_handler(logger=logger)
def create_user_service_review(event, context):
    request = CreateUserServiceReviewRequest.validate_event(event)

    response = UserService().create_user_review(request=request)

    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


def register_user_post_aws_cognito_signup(event, context):
    cognito_event = CognitoUserPoolEvent.model_validate(event)
    if cognito_event.trigger_source == "PostConfirmation_ConfirmSignUp":
        UserService().register_user(cognito_event)
    return event
