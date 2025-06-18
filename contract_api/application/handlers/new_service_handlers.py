import json

from common.constant import StatusCode
from common.logger import get_logger
from common.repository import Repository
from common.utils import Utils, generate_lambda_response
from contract_api.application.services.registry_service import RegistryService
from contract_api.config import NETWORK_ID, NETWORKS
from contract_api.application.services.registry import Registry

db = Repository(net_id=NETWORK_ID, NETWORKS=NETWORKS)
obj_util = Utils()
logger = get_logger(__name__)


def get_all_services(event, context):
    logger.info(f"get_service_get:: {event}")
    obj_reg = Registry(obj_repo = db)
    payload_dict = event.get('queryStringParameters')
    response_data = obj_reg.get_filter_attribute(
        attribute = payload_dict["attribute"])
    return generate_lambda_response(
        200, {"status": "success", "data": response_data}, cors_enabled = True)


def get_services(event, context):
    logger.info(f"Got service post:: {event}")
    obj_reg = Registry(obj_repo = db)
    payload_dict = json.loads(event['body'])
    response_data = obj_reg.get_services(qry_param = payload_dict)
    return generate_lambda_response(
        200, {"status": "success", "data": response_data}, cors_enabled = True)


def get_service(event, context):
    logger.info(f"Got service for given org :: {event}")
    obj_reg = Registry(obj_repo = db)
    org_id = event['pathParameters']['orgId']
    service_id = event['pathParameters']['serviceId']
    response_data = obj_reg.get_service(
        org_id = org_id, service_id = service_id)
    logger.info(f"Response data: {response_data}")
    return generate_lambda_response(
        200, {"status": "success", "data": response_data}, cors_enabled = True)


def curate_service(event, context):
    logger.info(f"Got service curation event :: {event}")
    registry = Registry(obj_repo = db)
    org_id = event['pathParameters']['orgId']
    service_id = event['pathParameters']['serviceId']
    curate = event['queryStringParameters']['curate']
    response = registry.curate_service(
        org_id = org_id, service_id = service_id, curated = curate)
    return generate_lambda_response(
        StatusCode.CREATED, {"status": "success", "data": response}, cors_enabled = True)


def save_offchain_attribute(event, context):
    logger.info(f"Got save offchain attribute event:: {event}")
    org_id = event["pathParameters"]["orgId"]
    service_id = event["pathParameters"]["serviceId"]
    attributes = json.loads(event["body"])
    response = RegistryService(org_id = org_id, service_id = service_id).save_offchain_service_attribute(
        new_offchain_attributes = attributes)
    logger.info(f"Response data: {response}")
    return generate_lambda_response(
        200, {"status": "success", "data": response}, cors_enabled = True)


