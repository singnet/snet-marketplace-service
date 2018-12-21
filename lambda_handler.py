import json
import traceback

from schema import Schema, And

from channel import Channel
from service import Service
from service_status import ServiceStatus

service_instance = Service()


def request_handler(event, context):
    print(event)
    if 'path' not in event:
        return get_response("400", "Bad Request")
    try:
        payload_dict = None
        path = event['path'].replace('/', '')
        payload = event['body']
        if payload is not None and len(payload) > 0:
            payload_dict = json.loads(payload)

        print("Processing [" + str(path) + "] with body [" + str(payload) + "]")

        data = None
        if "service" == path.lower():
            data = service_instance.get_curated_services()
        elif "fetch-profile" == path.lower():
            data = get_profile_details(payload_dict['user_address'])
        elif "fetch-vote" == path.lower():
            data = get_user_vote(payload_dict['user_address'])
        elif "vote" == path.lower():
            data = set_user_vote(payload_dict['vote'])
        elif "group-info" == path.lower():
            data = service_instance.get_group_info()
        elif "channel-info" == path.lower():
            channel_instance = Channel()
            data = channel_instance.get_channel_info(payload_dict['user_address'], payload_dict['service_id'], payload_dict['org_name'])
        elif "update-service-status" == path.lower():
            s = ServiceStatus(service_instance.repo)
            s.update_service_status()
            data = []

        if data is None:
            response = get_response("400", "Bad Request")
        else:
            response = get_response("200", data)
    except Exception as e:
        response = get_response(500, repr(e))
        traceback.print_exc()

    print(response)
    return response

def get_profile_details(user_address):
    if user_address is None or len(user_address) == 0:
        return []
    return service_instance.get_profile_details(user_address)


def set_user_vote(vote_info):
    schema = Schema([{'user_address': And(str),
                      'organization_name': And(str),
                      'service_name': And(str),
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


# Generate error message payload
def get_error_response(error):
    response = dict()
    response['message'] = error
    response['status'] = "failure"
    return response
