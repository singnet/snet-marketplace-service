import json

from common.constant import StatusCode
from common.utils import generate_lambda_response
from payments.application.dapp_order_manager import OrderManager


def create(event, context):
    payload = event["body"]
    item_details = json.loads(event['body'])
    amount = payload["amount"]["amount"]
    currency = payload["amount"]["currency"]
    username = payload["username"]

    status, response = OrderManager().create_order(amount, currency, item_details, username)
    if status:
        return generate_lambda_response(
            status_code=StatusCode.SUCCESS_POST_CODE,
            message=response
        )
    else:
        return generate_lambda_response(
            status_code=StatusCode.SERVER_ERROR_CODE,
            message=response
        )
