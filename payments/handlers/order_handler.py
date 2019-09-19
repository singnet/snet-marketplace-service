import json

from common.constant import StatusCode
from common.utils import generate_lambda_response, validate_dict
from payments.application.dapp_order_manager import OrderManager


def create(event, context):
    payload = json.loads(event['body'])
    if validate_dict(payload, ["price", "username"]):
        amount = payload["price"]["amount"]
        currency = payload["price"]["currency"]
        username = payload["username"]
        item_details = payload["item_details"]
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
