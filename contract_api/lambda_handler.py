import json
import re
import traceback
from urllib.parse import unquote

from contract_api.config import NETWORKS, SLACK_HOOK, NETWORK_ID
from common.repository import Repository
from common.utils import Utils
from contract_api.registry import Registry
from contract_api.mpe import MPE
from aws_xray_sdk.core import patch_all

patch_all()

NETWORKS_NAME = dict((NETWORKS[netId]['name'], netId)
                     for netId in NETWORKS.keys())
db = dict((netId, Repository(net_id=netId, NETWORKS=NETWORKS))
          for netId in NETWORKS.keys())
obj_util = Utils()


def request_handler(event, context):
    print(event)
    if 'path' not in event:
        return get_response(400, "Bad Request")
    try:
        payload_dict = None
        path = event['path'].lower()
        path = re.sub(r"^(\/contract-api)", "", path)
        net_id = NETWORK_ID
        method = event['httpMethod']
        response_data = None

        if method == 'POST':
            payload_dict = json.loads(event['body'])
        elif method == 'GET':
            payload_dict = event.get('queryStringParameters')
        else:
            return get_response(405, "Method Not Allowed")

        sub_path = path.split("/")
        if sub_path[1] in ["org", "service"]:
            obj_reg = Registry(obj_repo=db[net_id])

        elif sub_path[1] in ["channel", "group"]:
            obj_mpe = MPE(net_id=net_id, obj_repo=db[net_id])







        if "/service" == path and method == 'POST':
            payload_dict = {} if payload_dict is None else payload_dict
            response_data = obj_reg.get_all_srvcs(qry_param=payload_dict)

        elif "/service" == path and method == 'GET':
            response_data = obj_reg.get_filter_attribute(
                attribute=payload_dict["attribute"])

        elif re.match("(\/org\/)[^\/]*(\/service\/)[^\/]*(\/group)[/]{0,1}$", path):
            """ Format /org/{orgId}/service/{serviceId}/group """
            org_id = sub_path[2]
            service_id = sub_path[4]
            response_data = obj_reg.get_group_info(
                org_id=org_id, service_id=service_id)

        elif "/channel" == path:
            user_address = payload_dict["user_address"]
            org_id = payload_dict.get("org_id", None)
            service_id = payload_dict.get("service_id", None)
            group_id = payload_dict.get("group_id", None)
            response_data = obj_mpe.get_channels(
                user_address=user_address,
                org_id=org_id,
                service_id=service_id,
                group_id=group_id
            )

        elif re.match("(\/org\/)[^\/]*(\/service\/)[^\/]*[/]{0,1}$", path):
            """ Format /org/{orgId}/service/{serviceId} """
            org_id = sub_path[2]
            service_id = sub_path[4]
            response_data = obj_reg.get_service_data_by_org_id_and_service_id(
                org_id=org_id, service_id=service_id)

        elif re.match("(\/group\/)[^\/]*(\/channel\/)[^\/]*[/]{0,1}$", path):
            """ Format /group/{groupId}/channel """
            group_id = sub_path[2]
            channel_id = sub_path[4]
            response_data = obj_mpe.get_channel_data_by_group_id_and_channel_id(
                group_id=group_id, channel_id=channel_id)


        elif re.match("(\/org\/)[^\/]*(\/service\/)[^\/]*(\/rating)[/]{0,1}$", path) and method == 'POST':
            """ Format /org/{orgId}/service/{serviceId}/rating """
            org_id = sub_path[2]
            service_id = sub_path[4]
            response_data = obj_reg.update_service_rating(org_id=org_id, service_id=service_id)

        else:
            return get_response(404, "Not Found")

        if response_data is None:
            err_msg = {'status': 'failed', 'error': 'Bad Request',
                       'api': event['path'], 'payload': payload_dict, 'network_id': net_id}
            obj_util.report_slack(1, str(err_msg), SLACK_HOOK)
            response = get_response(500, err_msg)
        else:
            response = get_response(
                200, {"status": "success", "data": response_data})
    except Exception as e:
        err_msg = {"status": "failed", "error": repr(
            e), 'api': event['path'], 'payload': payload_dict, 'network_id': net_id}
        obj_util.report_slack(1, str(err_msg), SLACK_HOOK)
        response = get_response(500, err_msg)
        traceback.print_exc()
    return response


def get_response(status_code, message):
    return {
        'statusCode': status_code,
        'body': json.dumps(message),
        'headers': {
            'Content-Type': 'application/json',
            "X-Requested-With": '*',
            "Access-Control-Allow-Headers": 'Access-Control-Allow-Origin, Content-Type,X-Amz-Date,Authorization,X-Api-Key,x-requested-with',
            "Access-Control-Allow-Origin": '*',
            "Access-Control-Allow-Methods": 'GET,OPTIONS,POST'
        }
    }
