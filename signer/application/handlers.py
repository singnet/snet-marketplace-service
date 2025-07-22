from common.constant import StatusCode
from common.exception_handler import exception_handler
from common.exceptions import BadRequestException
from common.logger import get_logger
from common.request_context import RequestContext
from common.utils import generate_lambda_response
from signer.application.schemas import (
    GetFreeCallSignatureRequest,
    GetSignatureForOpenChannelForThirdPartyRequest,
    GetSignatureForRegularCallRequest,
    GetSignatureForStateServiceRequest,
)
from signer.application.service import SignerService

logger = get_logger(__name__)


@exception_handler(logger=logger)
def get_free_call_signature_handler(event, context):
    req_ctx = RequestContext(event)

    request = GetFreeCallSignatureRequest.validate_event(event)

    response = SignerService().get_free_call_signature(req_ctx=req_ctx, request=request)

    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response},
        cors_enabled=True,
    )


@exception_handler(logger=logger)
def get_state_service_signature_handler(event, context):
    try:
        req_ctx = RequestContext(event)
    except BadRequestException:
        req_ctx = RequestContext(
            event=event,
            username="CONTRACT_API_SERVICE",
        )

    request = GetSignatureForStateServiceRequest.validate_event(event)

    response = SignerService().get_signature_for_state_service(req_ctx=req_ctx, request=request)

    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response},
        cors_enabled=True,
    )


@exception_handler(logger=logger)
def get_regular_call_signature_handler(event, context):
    req_ctx = RequestContext(event)

    request = GetSignatureForRegularCallRequest.validate_event(event)

    response = SignerService().get_signature_for_regular_call(req_ctx=req_ctx, request=request)

    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response},
        cors_enabled=True,
    )


@exception_handler(logger=logger)
def get_open_channel_for_third_party_signature_handler(event, context):
    req_ctx = RequestContext(event)

    request = GetSignatureForOpenChannelForThirdPartyRequest.validate_event(event)

    response = SignerService().get_signature_for_open_channel_for_third_party(
        req_ctx=req_ctx, request=request
    )

    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response},
        cors_enabled=True,
    )


@exception_handler(logger=logger)
def get_free_call_signer_address_handler(event, context):
    response = SignerService().get_freecall_signer_address()
    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response},
        cors_enabled=True,
    )
