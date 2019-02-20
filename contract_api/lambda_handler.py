import json
import re
import traceback

from common.constant import NETWORKS
from common.repository import Repository
from common.utils import Utils
from contract_api.channel import Channel
from contract_api.search import Search
from contract_api.service import Service
from contract_api.service_status import ServiceStatus
from schema import Schema, And

NETWORKS_NAME = dict((NETWORKS[netId]['name'], netId) for netId in NETWORKS.keys())
obj_util = Utils()
db = dict((netId, Repository(net_id=netId)) for netId in NETWORKS.keys())
route_path = {}


def request_handler(event, context):
    print(event)
    if 'path' not in event:
        print("request_handler::path: ", None)
        return get_response("400", "Bad Request")
    try:
        payload_dict = None
        path = event['path'].lower()
        if event['httpMethod'] == 'POST':
            body = event['body']
            if body is not None and len(body) > 0:
                payload_dict = json.loads(body)
                print("Processing [" + str(path) + "] with body [" + str(body) + "]")
        elif event['httpMethod'] == 'GET':
            payload_dict = event.get('queryStringParameters')
            print("Processing [" + str(path) + "] with queryStringParameters [" + str(payload_dict) + "]")
        stage = event['requestContext']['stage']
        net_id = NETWORKS_NAME[stage]
        if db[net_id].connection is None:
            db[net_id] = None
            db[net_id] = Repository(net_id=net_id)

        data = None
        if path in ["/service", "/channels", "/fetch-vote", "/user-vote", "/group-info"]:
            obj_srvc = Service(obj_repo=db[net_id])
        elif path in ["/available-channels", "/expired-channels"]:
            obj_chnnl = Channel(net_id, obj_repo=db[net_id])
        elif path[0:14] in ["/organizations"] or path[0:5] in ["/tags"]:
            obj_srch = Search(obj_repo=db[net_id])

        if "/service" == path:
            data = obj_srvc.get_curated_services()
        elif "/channels" == path:
            data = get_profile_details(user_address=payload_dict['user_address'], obj_srvc=obj_srvc)
        elif "/fetch-vote" == path:
            data = get_user_vote(payload_dict['user_address'], obj_srvc=obj_srvc)
        elif "/user-vote" == path:
            data = set_user_vote(payload_dict['vote'], obj_srvc=obj_srvc, net_id=net_id)
        elif "/group-info" == path:
            data = obj_srvc.get_group_info()
        elif "/available-channels" == path:
            data = obj_chnnl.get_channel_info(payload_dict['user_address'], payload_dict['service_id'],
                                              payload_dict['org_id'])
        elif "/expired-channels" == path:
            data = obj_chnnl.get_expired_channel_info(payload_dict['user_address'])
        elif "/organizations" == path:
            data = {"organizations": obj_srch.get_all_org()}
        elif re.match("^(/organizations)[/][[a-z0-9]+$", path):
            data = obj_srch.get_org(org_id=event['path'].split("/")[2])
        elif re.match("^(/organizations)[/][a-zA-Z0-9]{1,}[/](services)$", path):
            data = {"services": obj_srch.get_all_srvc(org_id=event['path'].split("/")[2])}
        elif re.match("^(/organizations)[/][a-zA-Z0-9]{1,}[/](services)[/][a-z0-9]+$", path):
            data = []
        elif re.match("^(/tags)[/][[a-z0-9]+$", path):
            data = {"services": obj_srch.get_all_srvc_by_tag(tag_name=event['path'].split("/")[2])}
        elif "update-service-status" == path:
            print('update service status')
            obj_srvc_st = ServiceStatus(repo=db[net_id])
            obj_srvc_st.update_service_status()
            data = {}

        if data is None:
            err_msg = {'status': 'failed', 'error': 'Bad Request', 'api': event['path']}
            obj_util.report_slack(1, str(err_msg))
            response = get_response("400", err_msg)
        else:
            response = get_response("200", {"status": "success", "data": data})
    except Exception as e:
        err_msg = {"status": "failed", "error": repr(e)}
        obj_util.report_slack(1, str(err_msg))
        response = get_response(500, err_msg)
        traceback.print_exc()

    print(response)
    return response


def check_for_blank(field):
    if field is None or len(field) == 0:
        return True
    return False


def get_profile_details(user_address, obj_srvc):
    if check_for_blank(user_address):
        return []
    return obj_srvc.get_profile_details(user_address)


def get_user_vote(user_address, obj_srvc):
    if check_for_blank(user_address):
        return []
    return obj_srvc.get_user_vote(user_address)


def set_user_vote(vote_info, obj_srvc, net_id):
    voted = False
    schema = Schema([{'user_address': And(str),
                      'org_id': And(str),
                      'service_id': And(str),
                      'up_vote': bool,
                      'down_vote': bool,
                      'signature': And(str)
                      }])
    try:
        vote_info = schema.validate([vote_info])
        voted = obj_srvc.set_user_vote(vote_info[0], net_id=net_id)
    except Exception as err:
        print("Invalid Input ", err)
        return None
    if voted:
        return []
    return None


# Generate response JSON that API gateway expects from the lambda function
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
