from urllib.parse import unquote

from aws_xray_sdk.core import patch_all

from common.repository import Repository
from common.utils import Utils, generate_lambda_response
from contract_api.config import NETWORKS, NETWORK_ID
from contract_api.registry import Registry

patch_all()

NETWORKS_NAME = dict((NETWORKS[netId]['name'], netId)
                     for netId in NETWORKS.keys())
db = dict((netId, Repository(net_id=netId, NETWORKS=NETWORKS))
          for netId in NETWORKS.keys())
obj_util = Utils()

net_id = NETWORK_ID

def get_all_org(event,context):

    obj_reg = Registry(obj_repo=db[net_id])
    response_data = obj_reg.get_all_org()
    return generate_lambda_response(
                200, {"status": "success", "data": response_data},cors_enabled=True)



def get_all_group_for_org(event,context):
    obj_reg = Registry(obj_repo=db[net_id])
    org_id=event['pathParameters']['orgId']
    response_data = obj_reg.get_all_group_for_org_id(org_id=org_id)

    return generate_lambda_response(
                200, {"status": "success", "data": response_data},cors_enabled=True)


def get_group_for_org_id(event,context):
    obj_reg = Registry(obj_repo=db[net_id])
    org_id = event['pathParameters']['orgId']
    group_id = unquote(event['pathParameters']['group_id'])
    response_data = obj_reg.get_group_details_for_org_id(org_id=org_id, group_id=group_id)
    return generate_lambda_response(
                200, {"status": "success", "data": response_data},cors_enabled=True)



def get_org_for_org_id(event,context):
    org_id = event['pathParameters']['orgId']
    obj_reg = Registry(obj_repo=db[net_id])
    response_data = obj_reg.get_org_details(org_id=org_id)
    return generate_lambda_response(
                200, {"status": "success", "data": response_data},cors_enabled=True)
