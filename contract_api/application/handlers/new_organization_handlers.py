from urllib.parse import unquote

from common.logger import get_logger
from common.repository import Repository
from common.utils import Utils, generate_lambda_response
from contract_api.config import NETWORK_ID, NETWORKS
from contract_api.application.services.registry import Registry

db = Repository(net_id=NETWORK_ID, NETWORKS=NETWORKS)
obj_util = Utils()
logger = get_logger(__name__)

def get_all_organizations(event, context):
    obj_reg = Registry(obj_repo = db)
    response_data = obj_reg.get_all_organizations()
    return generate_lambda_response(
        200, {"status": "success", "data": response_data}, cors_enabled = True)


def get_group(event, context):
    obj_reg = Registry(obj_repo = db)
    org_id = event['pathParameters']['orgId']
    group_id = unquote(event['pathParameters']['group_id'])
    response_data = obj_reg.get_group(org_id = org_id, group_id = group_id)
    return generate_lambda_response(
        200, {"status": "success", "data": response_data}, cors_enabled = True)