import json
import re
import traceback
from urllib.parse import unquote

from aws_xray_sdk.core import patch_all

from common.repository import Repository
from common.utils import generate_lambda_response
from common.utils import make_response
from common.utils import Utils
from contract_api.config import NETWORK_ID
from contract_api.config import NETWORKS
from contract_api.config import SLACK_HOOK
from contract_api.lambda_handler import get_response
from contract_api.mpe import MPE
from contract_api.registry import Registry

patch_all()

NETWORKS_NAME = dict(
    (NETWORKS[netId]["name"], netId) for netId in NETWORKS.keys())
db = dict((netId, Repository(net_id=netId, NETWORKS=NETWORKS))
          for netId in NETWORKS.keys())
obj_util = Utils()

net_id = NETWORK_ID


def get_service_get(event, context):
    obj_reg = Registry(obj_repo=db[net_id])
    payload_dict = event.get("queryStringParameters")
    response_data = obj_reg.get_filter_attribute(
        attribute=payload_dict["attribute"])
    return generate_lambda_response(200, {
        "status": "success",
        "data": response_data
    },
                                    cors_enabled=True)


def get_service_post(event, context):
    obj_reg = Registry(obj_repo=db[net_id])
    payload_dict = json.loads(event["body"])
    response_data = obj_reg.get_all_srvcs(qry_param=payload_dict)
    return generate_lambda_response(200, {
        "status": "success",
        "data": response_data
    },
                                    cors_enabled=True)


def get_service_for_given_org(event, context):
    obj_reg = Registry(obj_repo=db[net_id])
    org_id = event["pathParameters"]["orgId"]
    service_id = event["pathParameters"]["serviceId"]
    response_data = obj_reg.get_service_data_by_org_id_and_service_id(
        org_id=org_id, service_id=service_id)
    return generate_lambda_response(200, {
        "status": "success",
        "data": response_data
    },
                                    cors_enabled=True)


def get_group_for_service(event, context):
    obj_reg = Registry(obj_repo=db[net_id])
    org_id = event["pathParameters"]["orgId"]
    service_id = event["pathParameters"]["serviceId"]
    response_data = obj_reg.get_group_info(org_id=org_id,
                                           service_id=service_id)
    return generate_lambda_response(200, {
        "status": "success",
        "data": response_data
    },
                                    cors_enabled=True)


def post_rating_for_given_service(event, context):
    obj_reg = Registry(obj_repo=db[net_id])
    org_id = event["pathParameters"]["orgId"]
    service_id = event["pathParameters"]["serviceId"]
    response_data = obj_reg.update_service_rating(org_id=org_id,
                                                  service_id=service_id)
    return generate_lambda_response(200, {
        "status": "success",
        "data": response_data
    },
                                    cors_enabled=True)
