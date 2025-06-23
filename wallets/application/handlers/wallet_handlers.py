import json

from common.constant import ResponseStatus
from common.exception_handler import exception_handler
from common.logger import get_logger
from common.utils import generate_lambda_response, make_response_body
from common.exceptions import BadRequestException
from wallets.application.service.wallet_service import WalletService

logger = get_logger(__name__)
wallet_service = WalletService()
EXCEPTIONS = (BadRequestException, )


@exception_handler(logger=logger)
def remove_user_wallet(event, context):
    logger.info(f"Received request to remove user wallet: {event}")
    try:
        body = event.get('body', None)
        assert body is not None, "Body not found"
        payload_dict = json.loads(body)
        assert payload_dict.get('username', None) is not None, "'username' field in the request body not found"
    except AssertionError as e:
        raise BadRequestException(str(e))

    wallet_service.remove_user_wallet(username = payload_dict["username"])
    response = generate_lambda_response(200, make_response_body(ResponseStatus.SUCCESS, "OK", {}))

    return response

@exception_handler(logger=logger, EXCEPTIONS=EXCEPTIONS)
def create_and_register_wallet(event, context):
    logger.info(f"Received request to create and register wallet: {event}")
    try:
        body = event.get('body', None)
        assert body is not None, "Body not found"
        payload_dict = json.loads(body)
        assert payload_dict.get('username', None) is not None, "'username' field in the request body not found"
    except AssertionError as e:
        raise BadRequestException(str(e))

    response_data = wallet_service.create_and_register_wallet(username=payload_dict['username'])
    response = generate_lambda_response(200, {"status": ResponseStatus.SUCCESS, "data": response_data})

    return response


@exception_handler(logger=logger, EXCEPTIONS=EXCEPTIONS)
def get_wallets(event, context):
    logger.info(f"Received request to get wallets: {event}")
    try:
        body = event.get('body', None)
        assert body is not None, "Body not found"
        payload_dict = json.loads(body)
        assert payload_dict.get('username', None) is not None, "'username' field in the request body not found"
    except AssertionError as e:
        raise BadRequestException(str(e))

    response_data = wallet_service.get_wallet_details(username = payload_dict['username'])
    response = generate_lambda_response(200, {"status": ResponseStatus.SUCCESS, "data": response_data})

    return response


@exception_handler(logger=logger, EXCEPTIONS=EXCEPTIONS)
def register_wallet(event, context):
    logger.info(f"Received request to register wallet: {event}")
    try:
        body = event.get('body', None)
        assert body is not None, "Body not found"
        payload_dict = json.loads(body)
        assert payload_dict.get('username', None) is not None, "'username' field in the request body not found"
        assert payload_dict.get('address', None) is not None, "'address' field in the request body not found"
        assert payload_dict.get('type', None) is not None, "'type' field in the request body not found"
    except AssertionError as e:
        raise BadRequestException(str(e))

    status = 1 # ACTIVE by default
    response_data = wallet_service.register_wallet(
        payload_dict["address"],
        payload_dict["type"],
        status,
        payload_dict['username']
    )
    response = generate_lambda_response(200, {"status": ResponseStatus.SUCCESS, "data": response_data})

    return response


@exception_handler(logger=logger, EXCEPTIONS=EXCEPTIONS)
def set_default_wallet(event, context):
    logger.info(f"Received request to set default wallet: {event}")
    try:
        body = event.get('body', None)
        assert body is not None, "Body not found"
        payload_dict = json.loads(body)
        assert payload_dict.get('username', None) is not None, "'username' field in the request body not found"
        assert payload_dict.get('address', None) is not None, "'address' field in the request body not found"
    except AssertionError as e:
        raise BadRequestException(str(e))

    wallet_service.set_default_wallet(payload_dict["username"], payload_dict["address"])
    response = generate_lambda_response(200, {"status": ResponseStatus.SUCCESS, "data": "OK"})

    return response
