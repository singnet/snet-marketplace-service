import json

from common.boto_utils import BotoUtils
from common.logger import get_logger
from orchestrator.config import GET_CHANNEL_API_OLD_ARN
from orchestrator.config import REGION_NAME
from orchestrator.config import WALLETS_SERVICE_ARN

logger = get_logger(__name__)


class WalletService:
    def __init__(self):
        self.boto_client = BotoUtils(REGION_NAME)

    def create_channel(self, open_channel_body):
        create_channel_transaction_payload = {
            "path": "/wallet/channel",
            "body": json.dumps(open_channel_body),
            "httpMethod": "POST",
        }

        create_channel_response = self.boto_client.invoke_lambda(
            lambda_function_arn=WALLETS_SERVICE_ARN,
            invocation_type="RequestResponse",
            payload=json.dumps(create_channel_transaction_payload),
        )

        logger.info(f"create_channel_response {create_channel_response}")
        if create_channel_response["statusCode"] != 200:
            raise Exception(f"Failed to create channel")

        create_channel_response_body = json.loads(create_channel_response["body"])
        channel_details = create_channel_response_body["data"]
        return channel_details

    def get_channel_details(self, username, org_id, group_id):
        """ Method to get wallet details for a given username. """
        try:
            wallet_channel_transactions = self.get_channel_transactions(
                username=username, org_id=org_id, group_id=group_id
            )
            wallet_response = {
                "username": username,
                "org_id": org_id,
                "group_id": group_id,
                "wallets": wallet_channel_transactions,
            }
            for wallet in wallet_response["wallets"]:
                user_address = wallet["address"]
                wallet["channels"] = self.get_channels_from_contract(
                    user_address=user_address, org_id=org_id, group_id=group_id
                )
            return wallet_response
        except Exception as e:
            print(repr(e))
            raise e

    def get_channel_transactions(self, username, org_id, group_id):

        channel_transactions_event = {
            "path": "/wallet/channel/transactions",
            "queryStringParameters": {
                "username": username,
                "group_id": group_id,
                "org_id": org_id,
            },
            "httpMethod": "GET",
        }

        channel_transactions_response = self.boto_client.invoke_lambda(
            lambda_function_arn=WALLETS_SERVICE_ARN,
            invocation_type="RequestResponse",
            payload=json.dumps(channel_transactions_event),
        )
        if channel_transactions_response["statusCode"] != 200:
            raise Exception(f"Failed to fetch wallet details for username: {username}")

        channel_transactions_response_body = json.loads(
            channel_transactions_response["body"]
        )
        channel_transactions = channel_transactions_response_body["data"]["wallets"]
        return channel_transactions

    def get_channels_from_contract(self, user_address, org_id, group_id):
        event = {
            "httpMethod": "GET",
            "path": "/channel",
            "queryStringParameters": {
                "user_address": user_address,
                "org_id": org_id,
                "group_id": group_id,
            },
        }

        channel_details_response = self.boto_client.invoke_lambda(
            lambda_function_arn=GET_CHANNEL_API_OLD_ARN,
            invocation_type="RequestResponse",
            payload=json.dumps(event),
        )

        if "statusCode" not in channel_details_response:
            logger.error(f"contract API boto call failed {channel_details_response}")
            raise Exception(f"Failed to get channel details from contract API {event}")

        if channel_details_response["statusCode"] != 200:
            raise Exception(
                f"Failed to get channel details from contract API username: {user_address} "
                f"group_id: {group_id} "
                f"org_id: {org_id}"
            )

        channel_details = json.loads(channel_details_response["body"])["data"]
        return channel_details["channels"]

    def get_wallets(self, username):
        get_wallet_event = {
            "path": "/wallet",
            "queryStringParameters": {"username": username},
            "httpMethod": "GET",
        }
        get_wallet_response = self.boto_client.invoke_lambda(
            lambda_function_arn=WALLETS_SERVICE_ARN,
            invocation_type="RequestResponse",
            payload=json.dumps(get_wallet_event),
        )
        status = get_wallet_response["statusCode"]
        if status != 200:
            raise Exception("Unable to get wallets for username %s", username)
        wallets = json.loads(get_wallet_response["body"])["data"]
        return wallets

    def register_wallet(self, username, wallet_details):
        register_wallet_body = {
            "address": wallet_details["address"],
            "type": wallet_details["type"],
            "username": username,
        }
        register_wallet_payload = {
            "path": "/wallet/register",
            "body": json.dumps(register_wallet_body),
            "httpMethod": "POST",
        }
        raw_response = self.boto_client.invoke_lambda(
            lambda_function_arn=WALLETS_SERVICE_ARN,
            invocation_type="RequestResponse",
            payload=json.dumps(register_wallet_payload),
        )
        status = raw_response["statusCode"]
        if int(status) != 200:
            raise Exception("Unable to register wallet for username %s", username)
        return json.loads(raw_response["body"])["data"]

    def set_default_wallet(self, username, address):
        set_default_wallet_body = {"address": address, "username": username}
        set_default_wallet_payload = {
            "path": "/wallet/status",
            "body": json.dumps(set_default_wallet_body),
            "httpMethod": "POST",
        }
        response = self.boto_client.invoke_lambda(
            lambda_function_arn=WALLETS_SERVICE_ARN,
            invocation_type="RequestResponse",
            payload=json.dumps(set_default_wallet_payload),
        )
        return json.loads(response["body"])["data"]

    def get_default_wallet(self, username):
        wallets = self.get_wallets(username)["wallets"]
        default_wallet = None
        for wallet in wallets:
            if wallet["is_default"] == 1 and wallet["type"] == "GENERAL":
                default_wallet = wallet

        if default_wallet is None:
            raise Exception("No active paypal wallet")

        return default_wallet
