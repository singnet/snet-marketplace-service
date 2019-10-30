import json
import traceback

from aws_xray_sdk.core import patch_all

from common.constant import StatusCode, ResponseStatus
from common.logger import get_logger
from common.repository import Repository
from common.utils import validate_dict, generate_lambda_response, make_response_body, Utils, format_error_message
from orchestrator.config import NETWORKS, NETWORK_ID, SLACK_HOOK
from orchestrator.errors import Error
from orchestrator.exceptions import PaymentInitiateFailed, ChannelCreationFailed
from orchestrator.services.order_service import OrderService

patch_all()

logger = get_logger(__name__)
utils = Utils()
repo = Repository(net_id=NETWORK_ID, NETWORKS=NETWORKS)
REQUIRED_KEYS_FOR_CURRENCY_TO_TOKEN_CONVERSION = ['pathParameters', 'queryStringParameters']


def initiate(event, context):
    logger.info("Received request to initiate order")
    try:
        username = event["requestContext"]["authorizer"]["claims"]["email"]
        payload = json.loads(event["body"])
        required_keys = ["price", "item_details", "payment_method"]
        if validate_dict(payload, required_keys):
            response = OrderService(obj_repo=repo).initiate_order(username, payload)
            status_code = StatusCode.CREATED
            status = ResponseStatus.SUCCESS
        else:
            status_code = StatusCode.BAD_REQUEST
            status = ResponseStatus.FAILED
            error = {}
            response = "Bad Request"
            logger.error(response)
            logger.info(event)
        error = {}

    except PaymentInitiateFailed:
        response = "Failed to initiate order"
        logger.error(response)
        logger.info(event)
        error = Error.PAYMENT_INITIATE_FAILED
        status = ResponseStatus.FAILED
        utils.report_slack(1, error, SLACK_HOOK)
        status_code = StatusCode.INTERNAL_SERVER_ERROR
        traceback.print_exc()

    except Exception as e:
        response = "Failed to initiate order"
        logger.error(response)
        logger.info(event)
        logger.error(e)
        error = Error.UNDEFINED_ERROR
        status = ResponseStatus.FAILED
        status_code = StatusCode.INTERNAL_SERVER_ERROR
        utils.report_slack(1, str(error), SLACK_HOOK)
        traceback.print_exc()
    return generate_lambda_response(status_code, make_response_body(
        status, response, error
    ), cors_enabled=True)


def execute(event, context):
    logger.info("Received request to execute order")
    try:
        username = event["requestContext"]["authorizer"]["claims"]["email"]
        payload = json.loads(event["body"])
        required_keys = ["order_id", "payment_id", "payment_details"]
        if validate_dict(payload, required_keys):
            response = OrderService(obj_repo=repo).execute_order(username, payload)
            status_code = StatusCode.CREATED
            status = ResponseStatus.SUCCESS
        else:
            status_code = StatusCode.BAD_REQUEST
            status = ResponseStatus.FAILED
            response = "Bad Request"
            logger.error(response)
            logger.info(event)
        error = {}
    except ChannelCreationFailed as e:
        response = e.get_wallet_details()
        logger.error(response)
        logger.info(event)
        error = Error.PAYMENT_INITIATE_FAILED
        status = ResponseStatus.FAILED
        status_code = StatusCode.INTERNAL_SERVER_ERROR
        utils.report_slack(1, str(error), SLACK_HOOK)

    except Exception as e:
        response = "Failed to execute order"
        logger.error(response)
        logger.info(event)
        logger.error(e)
        error = Error.UNDEFINED_ERROR
        status = ResponseStatus.FAILED
        status_code = StatusCode.INTERNAL_SERVER_ERROR
        utils.report_slack(1, str(error), SLACK_HOOK)
        traceback.print_exc()
    return generate_lambda_response(status_code, make_response_body(
        status, response, error
    ), cors_enabled=True)


def get(event, context):
    logger.info("Received request to get orders for username")
    try:
        username = event["requestContext"]["authorizer"]["claims"]["email"]
        order_id = None
        path_parameters = event["pathParameters"]
        if path_parameters is not None:
            order_id = path_parameters["order_id"]
        bad_request = False
        if order_id is None:
            logger.info(f"Getting all order details for user {username}")
            response = OrderService(obj_repo=repo).get_order_details_by_username(username)
        else:
            logger.info(f"Getting order details for order_id {order_id}")
            if order_id is not None:
                response = OrderService(obj_repo=repo).get_order_details_by_order_id(username=username,
                                                                                     order_id=order_id)
            else:
                bad_request = True

        error = {}
        if bad_request:
            status_code = StatusCode.BAD_REQUEST
            status = ResponseStatus.FAILED
            response = "Bad Request"
            logger.error(response)
            logger.info(event)
        else:
            status_code = StatusCode.CREATED
            status = ResponseStatus.SUCCESS

    except Exception as e:
        response = "Failed to get orders"
        error = Error.UNDEFINED_ERROR
        status = ResponseStatus.FAILED
        status_code = StatusCode.INTERNAL_SERVER_ERROR
        logger.error(response)
        logger.info(event)
        utils.report_slack(1, str(error), SLACK_HOOK)
        traceback.print_exc()
    return generate_lambda_response(status_code, make_response_body(
        status, response, error
    ), cors_enabled=True)


def cancel(event, context):
    logger.info("Received request for cancel order")
    try:
        path_parameters = event["pathParameters"]
        bad_request = False
        if path_parameters is None:
            bad_request = True
        else:
            order_id = path_parameters.get("order_id", None)
            if order_id is not None:
                response = OrderService(obj_repo=repo).cancel_order_for_given_order_id(order_id)
            else:
                bad_request = True
        error = {}
        if bad_request:
            status_code = StatusCode.BAD_REQUEST
            status = ResponseStatus.FAILED
            response = "Bad Request"
            logger.error(response)
            logger.info(event)
        else:
            status_code = StatusCode.CREATED
            status = ResponseStatus.SUCCESS

    except Exception as e:
        response = "Failed to cancel order"
        error = Error.UNDEFINED_ERROR
        status = ResponseStatus.FAILED
        status_code = StatusCode.INTERNAL_SERVER_ERROR
        logger.error(response)
        logger.info(event)
        utils.report_slack(1, error, SLACK_HOOK)
        traceback.print_exc()
    return generate_lambda_response(status_code, make_response_body(
        status, response, error
    ), cors_enabled=True)


def currency_to_token_conversion(event, context):
    try:
        valid_event = validate_dict(
            data_dict=event, required_keys=REQUIRED_KEYS_FOR_CURRENCY_TO_TOKEN_CONVERSION)
        if not valid_event:
            return generate_lambda_response(400, "Bad Request", cors_enabled=True)

        path_parameters = event["pathParameters"]
        query_string_parameters = event["queryStringParameters"]

        order_service = OrderService(obj_repo=repo)
        response_data = order_service.currency_to_token(currency=path_parameters["currency"],
                                                        amount=query_string_parameters["amount"])
        response = generate_lambda_response(200, {"status": "success", "data": response_data}, cors_enabled=True)
    except Exception as e:
        error_message = format_error_message(
            status="failed",
            error=repr(e),
            payload=path_parameters,
            net_id=NETWORK_ID,
            handler="cancel_order_handler"
        )
        utils.report_slack(1, error_message, SLACK_HOOK)
        response = generate_lambda_response(500, error_message, cors_enabled=True)
        traceback.print_exc()
    return response
