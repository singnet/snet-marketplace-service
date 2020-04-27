import json

from aws_xray_sdk.core import patch_all

from common.exception_handler import exception_handler
from common.logger import get_logger
from common.repository import Repository
from common.utils import Utils, generate_lambda_response
from common.utils import handle_exception_with_slack_notification
from contract_api.config import NETWORKS, NETWORK_ID, SLACK_HOOK
from contract_api.registry import Registry

patch_all()

db = Repository(net_id=NETWORK_ID, NETWORKS=NETWORKS)
obj_util = Utils()
logger = get_logger(__name__)


@handle_exception_with_slack_notification(logger=logger, NETWORK_ID=NETWORK_ID, SLACK_HOOK=SLACK_HOOK)
def get_service_get(event, context):
    obj_reg = Registry(obj_repo=db)
    payload_dict = event.get('queryStringParameters')
    response_data = obj_reg.get_filter_attribute(
        attribute=payload_dict["attribute"])
    return generate_lambda_response(
        200, {"status": "success", "data": response_data}, cors_enabled=True)


@handle_exception_with_slack_notification(logger=logger, NETWORK_ID=NETWORK_ID, SLACK_HOOK=SLACK_HOOK)
def get_service_post(event, context):
    obj_reg = Registry(obj_repo=db)
    payload_dict = json.loads(event['body'])
    response_data = obj_reg.get_all_srvcs(qry_param=payload_dict)
    return generate_lambda_response(
        200, {"status": "success", "data": response_data}, cors_enabled=True)


@handle_exception_with_slack_notification(logger=logger, NETWORK_ID=NETWORK_ID, SLACK_HOOK=SLACK_HOOK)
def get_service_for_given_org(event, context):
    obj_reg = Registry(obj_repo=db)
    org_id = event['pathParameters']['orgId']
    service_id = event['pathParameters']['serviceId']
    response_data = obj_reg.get_service_data_by_org_id_and_service_id(
        org_id=org_id, service_id=service_id)
    return generate_lambda_response(
        200, {"status": "success", "data": response_data}, cors_enabled=True)


@handle_exception_with_slack_notification(logger=logger, NETWORK_ID=NETWORK_ID, SLACK_HOOK=SLACK_HOOK)
def get_group_for_service(event, context):
    obj_reg = Registry(obj_repo=db)
    org_id = event['pathParameters']['orgId']
    service_id = event['pathParameters']['serviceId']
    response_data = obj_reg.get_group_info(
        org_id=org_id, service_id=service_id)
    return generate_lambda_response(
        200, {"status": "success", "data": response_data}, cors_enabled=True)


@handle_exception_with_slack_notification(logger=logger, NETWORK_ID=NETWORK_ID, SLACK_HOOK=SLACK_HOOK)
def post_rating_for_given_service(event, context):
    obj_reg = Registry(obj_repo=db)
    org_id = event['pathParameters']['orgId']
    service_id = event['pathParameters']['serviceId']
    response_data = obj_reg.update_service_rating(org_id=org_id, service_id=service_id)
    return generate_lambda_response(
        200, {"status": "success", "data": response_data}, cors_enabled=True)


@exception_handler(logger=logger, NETWORK_ID=NETWORK_ID, SLACK_HOOK=SLACK_HOOK)
def service_curation(event, context):
    registry = Registry(obj_repo=db)
    org_id = event['pathParameters']['orgId']
    service_id = event['pathParameters']['serviceId']
    curate = event['queryParameters']['curate']
    response = registry.curate_service(
        org_id=org_id, service_id=service_id, curate=curate)
    return generate_lambda_response(
        200, {"status": "success", "data": response}, cors_enabled=True)
