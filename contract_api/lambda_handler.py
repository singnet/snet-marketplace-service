import json
import re
import traceback

from contract_events_service.channel import Channel
from schema import Schema, And
from contract_events_service.service import Service
from contract_events_service.service_status import ServiceStatus
from common.constant import NETWORKS

NETWORKS_NAME = dict((NETWORKS[netId]['name'], netId) for netId in NETWORKS.keys())
service_instance = None
route_path = {}


def request_handler(event, context):
    print(event)
    if 'path' not in event:
        return get_response("400", "Bad Request")
    try:
        payload_dict = None
        path = event['path'].lower()
        payload = event['body']
        if payload is not None and len(payload) > 0:
            payload_dict = json.loads(payload)

        print("Processing [" + str(path) + "] with body [" + str(payload) + "]")
        netId = NETWORKS_NAME["Kovan"]
        service_instance = Service(netId)
        data = None
        if "/service" == path:
            data = service_instance.get_curated_services()
        elif "/fetch-profile" == path:
            data = get_profile_details(user_address=payload_dict['user_address'])
        elif "/fetch-vote" == path:
            data = get_user_vote(payload_dict['user_address'])
        elif "/vote" == path:
            data = set_user_vote(payload_dict['vote'])
        elif "/group-info" == path:
            data = service_instance.get_group_info()
        elif "/channel-info" == path:
            channel_instance = Channel(netId)
            data = channel_instance.get_channel_info(payload_dict['user_address'], payload_dict['service_id'],
                                                     payload_dict['org_id'])
        elif "/organizations" == path:
            data = {"organizations": []}
        elif re.match("^(/organizations)[/][[a-z0-9]+$", path):
            data = []
        elif re.match("^(/organizations)[/][a-zA-Z0-9]{1,}[/](services)$", path):
            data = {"services": []}
        elif re.match("^(/organizations)[/][a-zA-Z0-9]{1,}[/](services)[/][a-z0-9]+$", path):
            data = {"service_id": 1}
        elif re.match("^(/tags)[/][[a-z0-9]+$", path):
            data = {"services": []}
        elif "update-service-status" == path:
            print('update service status')
            s = ServiceStatus(service_instance.repo)
            s.update_service_status()
            data = {}

        if data is None:
            response = get_response("400", {"status": "failed", "error": "Bad Request"})
        else:
            response = get_response("200", {"status": "success", "data": data})
    except Exception as e:
        response = get_response(500, {"status": "failed",
                                      "error": repr(e)})
        traceback.print_exc()

    print(response)
    return response

def get_profile_details(user_address):
    if user_address is None or len(user_address) == 0:
        return []
    return service_instance.get_profile_details(user_address)


def set_user_vote(vote_info):
    schema = Schema([{'user_address': And(str),
                      'org_id': And(str),
                      'service_id': And(str),
                      'up_vote': bool,
                      'down_vote': bool
                      }])
    try:
        vote_info = schema.validate([vote_info])
    except Exception as err:
        print("Invalid Input ", err)
        return {'Success': False}
    return {'Success': service_instance.set_user_vote(vote_info[0])}


def get_user_vote(user_address):
    if user_address is None or len(user_address) == 0:
        return []
    return service_instance.get_user_vote(user_address)

def get_curated_services_by_tag():
    return service_instance.get_curated_services()


# Generate response JSON that API gateway expects from the lambda function
def get_response(status_code, message):
    return {
        'statusCode': status_code,
        'body': json.dumps(message),
        'headers': {
            'Content-Type': 'application/json',
            "X-Requested-With": '*',
            "Access-Control-Allow-Headers": 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,x-requested-with',
            "Access-Control-Allow-Origin": '*',
            "Access-Control-Allow-Methods": ''
                                            'GET,OPTIONS,POST'
        }
    }
