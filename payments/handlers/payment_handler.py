import json

from aws_xray_sdk.core import patch_all

from common.constant import StatusCode
from common.logger import get_logger
from common.utils import Utils, generate_lambda_response, validate_dict
from payments.application.dapp_order_manager import OrderManager
from payments.config import SLACK_HOOK

patch_all()

logger = get_logger(__name__)
utils = Utils()


def initiate(event, context):
    logger.info("Received request for initiate payment")
    try:
        payload = json.loads(event['body'])
        path_parameters = event["pathParameters"]
        if validate_dict(payload, ["price", "payment_method"]) \
            and validate_dict(path_parameters, ["order_id"]):
            order_id = path_parameters["order_id"]
            amount = payload["price"]["amount"]
            currency = payload["price"]["currency"]
            payment_method = payload["payment_method"]
            logger.info(f"Fetched values from request\n"
                        f"order_id: {order_id}\n"
                        f"amount: {amount} {currency}\n"
                        f"payment_method: {payment_method}")
            response = OrderManager().initiate_payment_against_order(order_id, amount, currency, payment_method)
            status_code = StatusCode.CREATED
        else:
            status_code = StatusCode.BAD_REQUEST
            response = "Bad Request"
            logger.error(response)
            logger.info(event)
    except Exception as e:
        logger.info(event)
        response = "Failed to initiate payment"
        logger.error(response)
        logger.error(e)
        status_code = StatusCode.INTERNAL_SERVER_ERROR
        utils.report_slack(f"got error : {response} \n {str(e)} \n for event : {event} ", SLACK_HOOK)
    return generate_lambda_response(
        status_code=status_code,
        message=response
    )


def execute(event, context):
    logger.info("Received request to execute payment")
    try:
        payload = json.loads(event['body'])
        path_parameters = event["pathParameters"]
        if validate_dict(payload, ["payment_method", "payment_details"]) \
            and validate_dict(path_parameters, ["order_id", "payment_id"]):
            order_id = path_parameters["order_id"]
            payment_id = path_parameters["payment_id"]
            payment_method = payload["payment_method"]
            payment_details = payload["payment_details"]
            logger.info(f"Fetched values from the request,"
                        f"order_id: {order_id}\n"
                        f"payment_id: {payment_id}\n"
                        f"payment_method: {payment_method}\n"
                        f"payment_details: {payment_details}")
            response = OrderManager().execute_payment_against_order(
                order_id, payment_id,
                payment_details, payment_method)
            status_code = StatusCode.CREATED
        else:
            status_code = StatusCode.BAD_REQUEST
            response = "Bad Request"
            logger.error(response)
            logger.info(event)
    except Exception as e:
        response = "Failed to execute payment"
        logger.error(response)
        logger.info(event)
        logger.error(e)
        status_code = StatusCode.INTERNAL_SERVER_ERROR
        utils.report_slack(f"got error : {response} \n {str(e)} \n for event : {event} ", SLACK_HOOK)
    return generate_lambda_response(
        status_code=status_code,
        message=response
    )


def cancel(event, context):
    logger.info("Received request to cancel payment")
    try:
        path_parameters = event["pathParameters"]
        if validate_dict(path_parameters, ["order_id", "payment_id"]):
            order_id = path_parameters["order_id"]
            payment_id = path_parameters["payment_id"]
            response = OrderManager().cancel_payment_against_order(order_id, payment_id)
            status_code = StatusCode.CREATED
        else:
            status_code = StatusCode.BAD_REQUEST
            response = "Bad Request"
            logger.error(response)
            logger.info(event)
    except Exception as e:
        response = "Failed to cancel payment"
        logger.error(response)
        logger.info(event)
        logger.error(e)
        status_code = StatusCode.INTERNAL_SERVER_ERROR
        utils.report_slack(f"got error : {response} \n {str(e)} \n for event : {event} ", SLACK_HOOK)
    return generate_lambda_response(
        status_code=status_code,
        message=response
    )
