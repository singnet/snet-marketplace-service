from common.constant import StatusCode, ResponseStatus
from common.logger import get_logger
from common.repository import Repository
from common.utils import Utils, handle_exception_with_slack_notification, generate_lambda_response, make_response_body
from wallets.config import NETWORKS, NETWORK_ID, SLACK_HOOK
from wallets.service.wallet_service import WalletService

NETWORKS_NAME = dict((NETWORKS[netId]['name'], netId) for netId in NETWORKS.keys())
repo = Repository(net_id=NETWORK_ID, NETWORKS=NETWORKS)
utils = Utils()
logger = get_logger(__name__)
wallet_service = WalletService(repo=repo)


@handle_exception_with_slack_notification(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger)
def delete_user_wallet(event, context):
    query_parameters = event["queryStringParameters"]
    username = query_parameters["username"]
    wallet_service.remove_user_wallet(username)
    return generate_lambda_response(StatusCode.CREATED, make_response_body(
        ResponseStatus.SUCCESS, "OK", {}
    ), cors_enabled=False)

