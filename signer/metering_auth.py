import json

from web3.auto import w3
from common.repository import Repository
from signer.constant import StatusCode, StatusMessage

required_data = ['demon_id', 'message_data_', 'signature']


def extract_public_key(message_data, signature):
    public_key = w3.eth.account.recoverHash(message_data, signature=signature)
    return public_key


def make_response(status_code, body, header=None):
    return {
        "statusCode": status_code,
        "headers": header,
        "body": body
    }


def validate_request(required_keys, request_body):
    for key in required_keys:
        if key not in request_body:
            return False
    return True


def main(event, context):
    """TODO:
        - add appropriate table for demon data
        - add appropriate request method for lambda"""
    request_data = event['body']
    # request_data = event[''queryStringParameters']

    if validate_request(required_data, request_data):
        try:
            demon_id = request_data['demon_id']
            message_data = request_data['message_data']
            signature = request_data['signature']

            derived_public_key = extract_public_key(message_data, signature)
            public_key = Repository().execute('select public_key from table.demon_auth_keys')

            verification = (public_key == derived_public_key)

            return_value = make_response(
                status_code=StatusCode.SUCCESS_GET_CODE,
                body=json.dumps({"verification": verification})
            )

        except Exception as e:
            return_value = make_response(
                status_code=StatusCode.SERVER_ERROR_CODE,
                body=json.dumps({"error": StatusMessage.SERVER_ERROR_MSG})
            )

    else:
        return_value = make_response(
            status_code=StatusCode.BAD_PARAMETERS_CODE,
            body=json.dumps({"error": StatusMessage.BAD_PARAMETER})
        )

    return return_value
