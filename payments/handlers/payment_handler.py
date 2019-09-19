import json

from common.logger import get_logger
from common.utils import generate_lambda_response, validate_dict
from payments.application.dapp_order_manager import OrderManager
from common.constant import StatusCode

logger = get_logger(__name__)


def initiate(event, context):
    try:
        payload = json.loads(event['body'])
        path_parameters = json.loads(event["pathParameters"])
        if validate_dict(payload, ["amount", "payment_method"]) \
                and validate_dict(path_parameters, ["order_id"]):
            order_id = path_parameters["order_id"]
            amount = payload["amount"]["amount"]
            currency = payload["amount"]["currency"]
            payment_method = payload["payment_method"]
            status, response = OrderManager().initiate_payment_against_order(order_id, amount, currency, payment_method)
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
    except Exception as e:
        logger(e)
        return generate_lambda_response(
            status_code=StatusCode.INTERNAL_SERVER_ERROR,
            message="Internal Server Error"
        )


def execute(event, context):
    try:
        payload = json.loads(event['body'])
        path_parameters = json.loads(event["pathParameters"])
        if validate_dict(payload, ["payment_method", "payment_details"]) \
                and validate_dict(path_parameters, ["order_id", "payment_id"]):
            order_id = path_parameters["order_id"]
            payment_id = path_parameters["payment_id"]
            payment_method = payload["payment_method"]
            payment_details = payload["payment_details"]
            status, response = OrderManager().execute_payment_against_order(order_id, payment_id, payment_details, payment_method)
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
    except Exception as e:
        logger(e)
        return generate_lambda_response(
            status_code=StatusCode.INTERNAL_SERVER_ERROR,
            message="Internal Server Error"
    )


def cancel(event, context):
    try:
        path_parameters = json.loads(event["pathParameters"])
        if validate_dict(path_parameters, ["order_id", "payment_id"]):
            order_id = path_parameters["order_id"]
            payment_id = path_parameters["payment_id"]
            status, response = OrderManager().cancel_payment_against_order(order_id, payment_id)
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
    except Exception as e:
        logger(e)
        return generate_lambda_response(
            status_code=StatusCode.INTERNAL_SERVER_ERROR,
            message="Internal Server Error"
        )
