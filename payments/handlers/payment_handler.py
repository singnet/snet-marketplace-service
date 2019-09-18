import json

from common.utils import make_response, generate_lambda_response
from payments.application.dapp_order_manager import OrderManager
from common.constant import StatusCode, HEADER_POST_RESPONSE


def initiate(event, context):
    order_id = event['pathParameters']["order_id"]
    payload = json.loads(event['body'])
    amount = payload["amount"]["amount"]
    currency = payload["amount"]["currency"]
    payment_method = payload["payment_method"]
    status, response = OrderManager().initiate_payment_against_order(order_id, amount, currency, payment_method)
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


def execute(event, context):
    order_id = event['pathParameters']["order_id"]
    payment_id = event['pathParameters']["payment_id"]
    payload = json.loads(event['body'])
    payment_method = payload["payment_method"]
    payment_details = payload["payment_details"]
    status, response = OrderManager().execute_payment_against_order(order_id, payment_id, payment_details, payment_method)
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
