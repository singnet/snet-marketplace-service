import json

from common.constant import StatusCode
from common.logger import get_logger
from common.utils import generate_lambda_response, validate_dict, Utils
from payments.application.dapp_order_manager import OrderManager
from payments.config import SLACK_HOOK

logger = get_logger(__name__)
utils=Utils()

def create(event, context):
    logger.info("Received request to create order")
    try:
        payload = json.loads(event['body'])
        if validate_dict(payload, ["price", "username"]):
            amount = payload["price"]["amount"]
            currency = payload["price"]["currency"]
            username = payload["username"]
            item_details = payload["item_details"]
            logger.info(f"Fetched values from request\n"
                        f"username: {username}\n"
                        f"amount: {amount} {currency}\n"
                        f"item_details: {item_details}")
            response = OrderManager().create_order(amount, currency, item_details, username)
            status_code = StatusCode.CREATED
        else:
            status_code = StatusCode.BAD_REQUEST
            response = "Bad Request"
            logger.error(response)
            logger.info(event)
    except Exception as e:
        response = "Failed to create order"
        logger.error(response)
        logger.info(event)
        logger.error(e)
        status_code = StatusCode.INTERNAL_SERVER_ERROR
    return generate_lambda_response(
        status_code=status_code,
        message=response
    )


def get_order_details_for_user(event, context):
    logger.info("Received request to get order details using username")
    try:
        if "username" in event["queryStringParameters"]:
            username = event["queryStringParameters"]["username"]
            logger.info(f"Fetched values from request\n"
                        f"username: {username}")
            response = OrderManager().get_order_details_for_user(username)
            status_code = StatusCode.OK
        else:
            status_code = StatusCode.BAD_REQUEST
            response = "Bad Request"
            logger.error(response)
            logger.info(event)
    except Exception as e:
        response = "Failed to fetch order details"
        logger.error(response)
        logger.info(event)
        logger.error(e)
        status_code = StatusCode.INTERNAL_SERVER_ERROR
    return generate_lambda_response(
        status_code=status_code,
        message=response
    )


def get_order_from_order_id(event, context):
    logger.info("Received request to get order using order id")
    try:
        if "order_id" in event["pathParameters"]:
            order_id = event["pathParameters"]["order_id"]
            logger.info(f"Fetched values from request\n"
                        f"order_id: {order_id}")
            response = OrderManager().get_order_from_order_id(order_id)
            status_code = StatusCode.OK
        else:
            status_code = StatusCode.BAD_REQUEST
            response = "Bad Request"
            logger.error(response)
            logger.info(event)
    except Exception as e:
        response = "Internal Server Error"
        logger.error(response)
        logger.info(event)
        logger.error(e)
        status_code = StatusCode.INTERNAL_SERVER_ERROR
    return generate_lambda_response(
        status_code=status_code,
        message=response
    )
