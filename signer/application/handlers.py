from common.constant import StatusCode
from common.exceptions import BadRequestException
from common.logger import get_logger
from common.utils import generate_lambda_response, handle_exception_with_slack_notification

from signer.application.schemas import (
    GetFreeCallSignatureRequest,
    GetSignatureForOpenChannelForThirdPartyRequest,
    GetSignatureForRegularCallRequest,
    GetSignatureForStateServiceRequest,
    GetFreeCallTokenRequest,
    GetFreecallSignerAddress,
    GetSignatureForFreeCallFromDaemonRequest
)
from signer.application.service import SignerService

from common.schemas import PayloadValidationError
from common.request_context import RequestContext
from signer.settings import settings

logger = get_logger(__name__)


@handle_exception_with_slack_notification(SLACK_HOOK="", NETWORK_ID=settings.network.id, logger=logger)
def get_signature_for_free_call(event, context):
    req_ctx = RequestContext(event)

    try:
        request = GetFreeCallSignatureRequest.validate_event(event)
    except PayloadValidationError:
        raise BadRequestException()

    response = SignerService().get_signature_for_free_call(
        username=req_ctx.username,
        request=request
    )
    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response},
        cors_enabled=True,
    )


@handle_exception_with_slack_notification(SLACK_HOOK="", NETWORK_ID=settings.network.id, logger=logger)
def get_signature_for_state_service(event, context):
    req_ctx = RequestContext(event)

    try:
        request = GetSignatureForStateServiceRequest.validate_event(event)
    except PayloadValidationError:
        raise BadRequestException()

    response = SignerService().get_signature_for_state_service(
        username=req_ctx.username,
        request=request
    )
    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response},
        cors_enabled=True,
    )


@handle_exception_with_slack_notification(SLACK_HOOK="", NETWORK_ID=settings.network.id, logger=logger)
def get_signature_for_regular_call_handler(event, context):
    req_ctx = RequestContext(event)

    try:
        request = GetSignatureForRegularCallRequest.validate_event(event)
    except PayloadValidationError:
        raise BadRequestException()
    
    response = SignerService().get_signature_for_regular_call(
        username=req_ctx.username,
        request=request
    )
    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response},
        cors_enabled=True,
    )


@handle_exception_with_slack_notification(SLACK_HOOK="", NETWORK_ID=settings.network.id, logger=logger)
def get_signature_for_open_channel_for_third_party_handler(event, context):
    try:
        request = GetSignatureForOpenChannelForThirdPartyRequest.validate_event(event)
    except PayloadValidationError:
        raise BadRequestException()

    response = SignerService().get_signature_for_open_channel_for_third_party(
        request=request
    )
    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response},
        cors_enabled=True,
    )


@handle_exception_with_slack_notification(SLACK_HOOK="", NETWORK_ID=settings.network.id, logger=logger)
def get_free_call_token_handler(event, context):
    req_ctx = RequestContext(event)

    try:
        request = GetFreeCallTokenRequest.validate_event(event)
    except PayloadValidationError:
        raise BadRequestException()

    response = SignerService().get_free_call_token(
        username=req_ctx.username,
        request=request
    )
    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response},
        cors_enabled=True,
    )


@handle_exception_with_slack_notification(SLACK_HOOK="", NETWORK_ID=settings.network.id, logger=logger)
def get_free_call_signer_address_handler(event, context):
    try:
        GetFreecallSignerAddress.validate_event(event)
    except PayloadValidationError:
        raise BadRequestException()

    response = SignerService().get_freecall_signer_address()
    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response},
        cors_enabled=True,
    )


@handle_exception_with_slack_notification(SLACK_HOOK="", NETWORK_ID=settings.network.id, logger=logger)
def get_signature_for_free_call_daemon(event, context):
    req_ctx = RequestContext(event)

    try:
        request = GetSignatureForFreeCallFromDaemonRequest.validate_event(event)
    except PayloadValidationError:
        raise BadRequestException()

    response = SignerService().get_signature_for_free_call_from_daemon(
        username=req_ctx.username,
        request=request
    )
    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response},
        cors_enabled=True
    )