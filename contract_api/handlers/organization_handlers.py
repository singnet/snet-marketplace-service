from urllib.parse import unquote

from common.repository import Repository
from common.logger import get_logger
from common.utils import Utils, generate_lambda_response
from common.exception_handler import exception_handler
from contract_api.config import NETWORKS, NETWORK_ID 
from contract_api.registry import Registry


db = Repository(net_id=NETWORK_ID, NETWORKS=NETWORKS)
obj_util = Utils()
logger = get_logger(__name__)


@exception_handler(logger=logger)
def get_all_org(event, context):
    obj_reg = Registry(obj_repo=db)
    response_data = obj_reg.get_all_org()
    return generate_lambda_response(
        200, {"status": "success", "data": response_data}, cors_enabled=True)


@exception_handler(logger=logger)
def get_all_group_for_org(event, context):
    obj_reg = Registry(obj_repo=db)
    org_id = event['pathParameters']['orgId']
    response_data = obj_reg.get_all_group_for_org_id(org_id=org_id)

    return generate_lambda_response(
        200, {"status": "success", "data": response_data}, cors_enabled=True)


@exception_handler(logger=logger)
def get_group_for_org_id(event, context):
    obj_reg = Registry(obj_repo=db)
    org_id = event['pathParameters']['orgId']
    group_id = unquote(event['pathParameters']['group_id'])
    response_data = obj_reg.get_group_details_for_org_id(org_id=org_id, group_id=group_id)
    return generate_lambda_response(
        200, {"status": "success", "data": response_data}, cors_enabled=True)


@exception_handler(logger=logger)
def get_org_for_org_id(event, context):
    org_id = event['pathParameters']['orgId']
    obj_reg = Registry(obj_repo=db)
    response_data = obj_reg.get_org_details(org_id=org_id)
    return generate_lambda_response(
        200, {"status": "success", "data": response_data}, cors_enabled=True)
