from common.constant import StatusCode
from common.exception_handler import exception_handler
from common.logger import get_logger
from common.utils import generate_lambda_response

from contract_api.application.schemas.service_schemas import (
    GetServiceFiltersRequest,
    GetServicesRequest,
    GetServiceRequest,
    CurateServiceRequest,
    SaveOffchainAttributeRequest, UpdateServiceRatingRequest
)
from contract_api.application.services.service_service import ServiceService


logger = get_logger(__name__)


@exception_handler(logger=logger)
def get_service_filters(event, context):
    request = GetServiceFiltersRequest.validate_event(event)

    response = ServiceService().get_service_filters(request)

    return generate_lambda_response(
        200, {"status": "success", "data": response}, cors_enabled = True
    )


@exception_handler(logger=logger)
def get_services(event, context):
    request = GetServicesRequest.validate_event(event)

    response = ServiceService().get_services(request)

    return generate_lambda_response(
        200, {"status": "success", "data": response}, cors_enabled = True
    )


@exception_handler(logger=logger)
def get_service(event, context):
    request = GetServiceRequest.validate_event(event)

    response = ServiceService().get_service(request)

    return generate_lambda_response(
        200, {"status": "success", "data": response}, cors_enabled = True
    )


@exception_handler(logger=logger)
def curate_service(event, context):
    request = CurateServiceRequest.validate_event(event)

    response = ServiceService().curate_service(request)

    return generate_lambda_response(
        StatusCode.CREATED, {"status": "success", "data": response}, cors_enabled = True
    )


@exception_handler(logger=logger)
def save_offchain_attribute(event, context):
    request = SaveOffchainAttributeRequest.validate_event(event)

    response = ServiceService().save_offchain_service_attribute(request)

    return generate_lambda_response(
        200, {"status": "success", "data": response}, cors_enabled = True
    )

@exception_handler(logger=logger)
def get_offchain_attribute(event, context):
    request = GetServiceRequest.validate_event(event)

    response = ServiceService().get_offchain_service_attribute(request)

    return generate_lambda_response(
        200, {"status": "success", "data": response}, cors_enabled = True
    )

@exception_handler(logger=logger)
def update_service_rating(event, context):
    request = UpdateServiceRatingRequest.validate_event(event)

    response = ServiceService().update_service_rating(request)

    return generate_lambda_response(
        200, {"status": "success", "data": response}, cors_enabled = True
    )
