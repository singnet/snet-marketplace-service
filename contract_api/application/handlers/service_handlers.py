from http import HTTPStatus
import json

from aws_xray_sdk.core import patch_all
from pydantic import ValidationError

from common.constant import StatusCode
from common.exception_handler import exception_handler
from common.exceptions import BadRequestException
from common.logger import get_logger
from common.repository import Repository
from common.utils import Utils, generate_lambda_response
from common.utils import handle_exception_with_slack_notification
from contract_api.application.services.update_assets_service import UpdateServiceAssets
from contract_api.application.services.registry_service import RegistryService
from contract_api.application.services.service_service import ServiceService
from contract_api.config import NETWORK_ID, NETWORKS, SLACK_HOOK
from contract_api.registry import Registry
from contract_api.application.schema.service import GetServiceRequest, AttributeNameEnum

patch_all()

db = Repository(net_id=NETWORK_ID, NETWORKS=NETWORKS)
obj_util = Utils()
logger = get_logger(__name__)


@handle_exception_with_slack_notification(logger=logger, NETWORK_ID=NETWORK_ID, SLACK_HOOK=SLACK_HOOK)
def get_services_handler(event, context):
    logger.info(f"Get services :: {event}")
    try:
        body = json.loads(event["body"])
        get_services_request = GetServiceRequest.model_validate(body)
    except ValidationError as e:
        logger.error(f"Request parsing error: {e}")
        raise BadRequestException(str(e))
    response = ServiceService().get_services(get_services_request)
    return generate_lambda_response(HTTPStatus.OK, response, cors_enabled=True)


@handle_exception_with_slack_notification(logger=logger, NETWORK_ID=NETWORK_ID, SLACK_HOOK=SLACK_HOOK)
def get_services_filter_handler(event, context):
    logger.info(f"Get services filter :: {event}")
    try:
        query_parameters = event.get("queryStringParameters")
        assert query_parameters is not None, "Invalid query string parameters"
        attribute_str = query_parameters.get("attribute")
        assert attribute_str is not None, "Attribute is not provided in query string parameters"
        attribute_enum = AttributeNameEnum.map_string_to_enum(attribute_str)
    except (AssertionError, ValueError) as e:
        logger.error(f"Request parsing error: {e}")
        raise BadRequestException(str(e))
    response = ServiceService().get_services_filter(attribute_enum)
    return generate_lambda_response(HTTPStatus.OK, response, cors_enabled=True)


@handle_exception_with_slack_notification(logger=logger, NETWORK_ID=NETWORK_ID, SLACK_HOOK=SLACK_HOOK)
def get_service_for_given_org(event, context):
    logger.info(f"Got service for given org :: {event}")
    obj_reg = Registry(obj_repo=db)
    org_id = event['pathParameters']['orgId']
    service_id = event['pathParameters']['serviceId']
    response_data = obj_reg.get_service_data_by_org_id_and_service_id(
        org_id=org_id, service_id=service_id)
    return generate_lambda_response(200, {"status": "success", "data": response_data}, cors_enabled=True)


@handle_exception_with_slack_notification(logger=logger, NETWORK_ID=NETWORK_ID, SLACK_HOOK=SLACK_HOOK)
def get_group_for_service(event, context):
    logger.info(f"Got group fpr service event :: {event}")
    obj_reg = Registry(obj_repo=db)
    org_id = event['pathParameters']['orgId']
    service_id = event['pathParameters']['serviceId']
    response_data = obj_reg.get_group_info(
        org_id=org_id, service_id=service_id)
    return generate_lambda_response(
        200, {"status": "success", "data": response_data}, cors_enabled=True)


@handle_exception_with_slack_notification(logger=logger, NETWORK_ID=NETWORK_ID, SLACK_HOOK=SLACK_HOOK)
def post_rating_for_given_service(event, context):
    logger.info(f"Got post rating for given service event :: {event}")
    obj_reg = Registry(obj_repo=db)
    org_id = event['pathParameters']['orgId']
    service_id = event['pathParameters']['serviceId']
    response_data = obj_reg.update_service_rating(org_id=org_id, service_id=service_id)
    return generate_lambda_response(
        200, {"status": "success", "data": response_data}, cors_enabled=True)


@exception_handler(logger=logger, NETWORK_ID=NETWORK_ID, SLACK_HOOK=SLACK_HOOK)
def service_curation(event, context):
    logger.info(f"Got service curation event :: {event}")
    registry = Registry(obj_repo=db)
    org_id = event['pathParameters']['orgId']
    service_id = event['pathParameters']['serviceId']
    curate = event['queryStringParameters']['curate']
    response = registry.curate_service(
        org_id=org_id, service_id=service_id, curated=curate)
    return generate_lambda_response(
        StatusCode.CREATED, {"status": "success", "data": response}, cors_enabled=True)


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger)
def service_deployment_status_notification_handler(event, context):
    logger.info(f"Service Build status event {event}")
    org_id = event['org_id']
    service_id = event['service_id']
    build_status = int(event['build_status'])
    Registry(obj_repo=db).service_build_status_notifier(org_id, service_id, build_status)
    return generate_lambda_response(
        StatusCode.CREATED,
        {"status": "success", "data": "Build failure notified", "error": {}}, cors_enabled=True
    )


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger)
def trigger_demo_component_build(event, context):
    logger.info(f"trigger_demo_component_build event :: {event}")
    response = UpdateServiceAssets().trigger_demo_component_build(payload=event)
    return generate_lambda_response(
        StatusCode.CREATED,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )

@handle_exception_with_slack_notification(logger=logger, NETWORK_ID=NETWORK_ID, SLACK_HOOK=SLACK_HOOK)
def save_offchain_attribute(event, context):
    logger.info(f"Got save offchain attribute event:: {event}")
    org_id = event["pathParameters"]["orgId"]
    service_id = event["pathParameters"]["serviceId"]
    attributes = json.loads(event["body"])
    response = RegistryService(org_id=org_id, service_id=service_id).save_offchain_service_attribute(
        new_offchain_attributes=attributes)
    return generate_lambda_response(
        200, {"status": "success", "data": response}, cors_enabled=True)

