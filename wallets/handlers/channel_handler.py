import json
import traceback

from common.constant import StatusCode, ResponseStatus
from common.logger import get_logger
from common.repository import Repository
from common.utils import Utils, validate_dict, generate_lambda_response, make_response_body
from wallets.config import NETWORK_ID, NETWORKS, SLACK_HOOK
from wallets.error import Error
from wallets.service.wallet_service import WalletService

NETWORKS_NAME = dict((NETWORKS[netId]['name'], netId) for netId in NETWORKS.keys())
repo = Repository(net_id=NETWORK_ID, NETWORKS=NETWORKS)
utils = Utils()
logger = get_logger(__name__)
wallet_service = WalletService(obj_repo=repo)


def create_channel(event, context):
    logger.info("Received request to initiate order")
    try:
        payload = json.loads(event["body"])
        required_keys = ["order_id", "sender", "signature", "r", "s", "v", "current_block_no",
                         "group_id", "org_id", "amount", "currency", "recipient", "amount_in_cogs"]
        if validate_dict(payload, required_keys):
            logger.info(f"Payload for create channel: {payload}")
            response = wallet_service.open_channel_by_third_party(
                order_id=payload['order_id'], sender=payload['sender'], signature=payload['signature'],
                r=payload['r'], s=payload['s'], v=payload['v'], current_block_no=payload['current_block_no'],
                group_id=payload['group_id'], org_id=payload["org_id"], recipient=payload['recipient'],
                amount=payload['amount'], currency=payload['currency'],
                amount_in_cogs=payload['amount_in_cogs']
            )
            return generate_lambda_response(StatusCode.CREATED, make_response_body(
                ResponseStatus.SUCCESS, response, {}), cors_enabled=False)
        else:
            response = "Bad Request"
            logger.error(f"response: {response}\n"
                         f"event: {event}")
            return generate_lambda_response(StatusCode.BAD_REQUEST, make_response_body(
                ResponseStatus.FAILED, response, {}
            ), cors_enabled=False)
    except Exception as e:
        response = "Failed create channel"
        logger.error(f"response: {response}\n"
                     f"event: {event}\n"
                     f"error: {repr(e)}")
        utils.report_slack(1, str(repr(e)), SLACK_HOOK)
        traceback.print_exc()
        return generate_lambda_response(StatusCode.INTERNAL_SERVER_ERROR, make_response_body(
            ResponseStatus.FAILED, response, Error.undefined_error(repr(e))
        ), cors_enabled=False)


def record_create_channel_event(event, context):
    logger.info("Received request to initiate order")
    try:
        payload = json.loads(event["body"])
        required_keys = ["order_id", "sender", "signature", "r", "s", "v", "current_block_no",
                         "group_id", "org_id", "amount", "currency", "recipient", "amount_in_cogs"]
        if validate_dict(payload, required_keys):
            logger.info(f"Payload for create channel: {payload}")
            response = wallet_service.record_create_channel_event(payload)
            return generate_lambda_response(StatusCode.CREATED, make_response_body(
                ResponseStatus.SUCCESS, response, {}), cors_enabled=False)
        else:
            response = "Bad Request"
            logger.error(f"response: {response}\n"
                         f"event: {event}")
            return generate_lambda_response(StatusCode.BAD_REQUEST, make_response_body(
                ResponseStatus.FAILED, response, {}
            ), cors_enabled=False)
    except Exception as e:
        response = "Failed to record create channel event"
        logger.error(f"response: {response}\n"
                     f"event: {event}\n"
                     f"error: {repr(e)}")
        utils.report_slack(1, str(repr(e)), SLACK_HOOK)
        traceback.print_exc()
        return generate_lambda_response(StatusCode.INTERNAL_SERVER_ERROR, make_response_body(
            ResponseStatus.FAILED, response, Error.undefined_error(repr(e))
        ), cors_enabled=False)


if __name__ == "__main__":
    record_create_channel_event({
        "path": "/wallet/channel",
        "body": "{\"order_id\": \"b7d9ffa0-07a3-11ea-b3cf-9e57fd86be16\", \"sender\": \"0x4A3Beb90be90a28fd6a54B6AE449dd93A3E26dd0\", \"signature\": \"0x7be1502b09f5997339571f4885194417d6ca84ca65f98a9a2883d981d071ba6255bcc83399b93bc60d70d4b10e33db626eac0dafd863b91e00a6b4b2c3586eb61b\", \"r\": \"0x7be1502b09f5997339571f4885194417d6ca84ca65f98a9a2883d981d071ba62\", \"s\": \"0x55bcc83399b93bc60d70d4b10e33db626eac0dafd863b91e00a6b4b2c3586eb6\", \"v\": 27, \"group_id\": \"m5FKWq4hW0foGW5qSbzGSjgZRuKs7A1ZwbIrJ9e96rc=\", \"org_id\": \"snet\", \"amount\": 2, \"currency\": \"USD\", \"recipient\": \"0xfA8a01E837c30a3DA3Ea862e6dB5C6232C9b800A\", \"current_block_no\": 6780504, \"amount_in_cogs\": 4000}",
        "httpMethod": "POST"
    }, None)
