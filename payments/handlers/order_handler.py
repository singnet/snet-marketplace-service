import json

from common.constant import StatusCode
from common.utils import generate_lambda_response, validate_dict
from payments.application.dapp_order_manager import OrderManager


def create(event, context):
    payload = event["body"]
    item_details = json.loads(event['body'])
    if validate_dict(payload, ["amount", "username"]):
        amount = payload["amount"]["amount"]
        currency = payload["amount"]["currency"]
        username = payload["username"]

        status, response = OrderManager().create_order(amount, currency, item_details, username)
        if status:
            return generate_lambda_response(
                status_code=StatusCode.CREATED,
                message=response
            )
        else:
            return generate_lambda_response(
                status_code=StatusCode.INTERNAL_SERVER_ERROR,
                message=response
            )
    else:
        return generate_lambda_response(
            status_code=StatusCode.BAD_REQUEST,
            message="Bad Request"
        )
