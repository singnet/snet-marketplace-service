import base64
import decimal
import json
from enum import Enum
from urllib.parse import quote

import boto3
from web3 import Web3

from common.blockchain_util import BlockChainUtil
from common.boto_utils import BotoUtils
from common.constant import TransactionStatus, COGS_TO_AGI
from common.logger import get_logger
from common.utils import Utils
from orchestrator.config import CREATE_ORDER_SERVICE_ARN, INITIATE_PAYMENT_SERVICE_ARN, \
    EXECUTE_PAYMENT_SERVICE_ARN, WALLETS_SERVICE_ARN, ORDER_DETAILS_ORDER_ID_ARN, ORDER_DETAILS_BY_USERNAME_ARN, \
    REGION_NAME, SIGNER_ADDRESS, EXECUTOR_ADDRESS, NETWORKS, NETWORK_ID, SIGNER_SERVICE_ARN, \
    GET_GROUP_FOR_ORG_API_ARN, GET_ALL_ORG_API_ARN, USD_TO_COGS_CONVERSION_FACTOR
from orchestrator.dao.transaction_history_dao import TransactionHistoryDAO
from orchestrator.exceptions import PaymentInitiateFailed, ChannelCreationFailed, FundChannelFailed
from orchestrator.order_status import OrderStatus
from orchestrator.services.wallet_service import WalletService
from orchestrator.transaction_history import TransactionHistory

logger = get_logger(__name__)


class Status(Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    PAYMENT_INITIATED = "PAYMENT_INITIATED"
    PAYMENT_INITIATION_FAILED = "PAYMENT_INITIATION_FAILED"
    PAYMENT_EXECUTED = "PAYMENT_EXECUTED"
    PAYMENT_EXECUTION_FAILED = "PAYMENT_EXECUTION_FAILED"
    ORDER_PROCESSED = "ORDER_PROCESSED"
    ORDER_PROCESSING_FAILED = "ORDER_PROCESSING_FAILED"


class OrderType(Enum):
    CREATE_WALLET_AND_CHANNEL = "CREATE_WALLET_AND_CHANNEL"
    CREATE_CHANNEL = "CREATE_CHANNEL"
    FUND_CHANNEL = "FUND_CHANNEL"


class OrderService:
    def __init__(self, obj_repo):
        self.repo = obj_repo
        self.obj_transaction_history_dao = TransactionHistoryDAO(self.repo)
        self.lambda_client = boto3.client('lambda', region_name=REGION_NAME)
        self.boto_client = BotoUtils(REGION_NAME)
        self.wallet_service = WalletService()
        self.obj_blockchain_util = BlockChainUtil(
            provider_type="HTTP_PROVIDER",
            provider=NETWORKS[NETWORK_ID]['http_provider']
        )
        self.utils = Utils()

    def initiate_order(self, username, payload_dict):
        """
            Initiate Order
                Step 1  Order Creation
                Step 2  Initiate Payment
                Step 3  Persist Transaction History
        """
        price = payload_dict["price"]
        order_type = payload_dict["item_details"]["order_type"]
        item_details = payload_dict["item_details"]
        group_id = item_details["group_id"]
        org_id = item_details["org_id"]
        channel_id = ""
        amount_in_cogs = self.calculate_amount_in_cogs(amount=price["amount"], currency=price["currency"])
        if amount_in_cogs < 1:
            raise Exception("Amount in cogs should be greater than equal to 1")
        item_details["amount_in_cogs"] = amount_in_cogs

        if order_type == OrderType.CREATE_WALLET_AND_CHANNEL.value:
            item_details["wallet_address"] = ""
            recipient = self.get_payment_address_for_org(group_id=group_id, org_id=org_id)

        elif order_type == OrderType.CREATE_CHANNEL.value:
            recipient = self.get_payment_address_for_org(group_id=group_id, org_id=org_id)

        elif order_type == OrderType.FUND_CHANNEL.value:
            channel = self.get_channel_for_topup(username=username, group_id=group_id, org_id=org_id)
            if channel is None:
                raise Exception(f"Channel not found for the user: {username} with org: {org_id} group: {group_id}")
            recipient = channel["recipient"]
            channel_id = channel["channel_id"]
            item_details["wallet_address"] = channel["address"]

        else:
            raise Exception("Invalid order type")

        item_details["channel_id"] = channel_id
        item_details["recipient"] = recipient
        order_details = self.manage_create_order(
            username=username, item_details=item_details,
            price=price
        )
        order_id = order_details["order_id"]

        try:
            payment_data = self.manage_initiate_payment(
                username=username, order_id=order_id, price=price,
                payment_method=payload_dict["payment_method"]
            )

            payment_id = payment_data["payment_id"]
            raw_payment_data = json.dumps(payment_data["payment"])
            obj_transaction_history = TransactionHistory(
                username=username, order_id=order_id, order_type=order_type,
                payment_id=payment_id, raw_payment_data=raw_payment_data,
                status=Status.PAYMENT_INITIATED.value
            )
            self.obj_transaction_history_dao.insert_transaction_history(obj_transaction_history=obj_transaction_history)
            return payment_data
        except Exception as e:
            obj_transaction_history = TransactionHistory(
                username=username, order_id=order_id, order_type=order_type,
                status=Status.PAYMENT_INITIATION_FAILED.value
            )
            self.obj_transaction_history_dao.insert_transaction_history(obj_transaction_history=obj_transaction_history)
            print(repr(e))
            raise e

    def get_channel_for_topup(self, username, group_id, org_id):
        channel_details = self.wallet_service.get_channel_details(
            username=username, group_id=group_id, org_id=org_id
        )
        wallets = channel_details["wallets"]
        for wallet in wallets:
            if (wallet["type"] == "GENERAL") and len(wallet["channels"]) > 0:
                if wallet["channels"][0]["signer"] == SIGNER_ADDRESS:
                    wallet_address = wallet["address"]
                    channel = wallet["channels"][0]
                    channel["address"] = wallet_address
                    return channel
        return None

    def get_payment_address_for_org(self, org_id, group_id):

        group_details_event = {
            "path": f"/org/{org_id}/group/{quote(group_id, safe='')}",
            "pathParameters": {
                "orgId": org_id,
                "group_id": quote(group_id, safe='')
            },
            "httpMethod": "GET"
        }
        logger.info(f"get_group_for_org request: {org_id} and {group_id}")
        group_details_lambda_response = self.lambda_client.invoke(
            FunctionName=GET_GROUP_FOR_ORG_API_ARN,
            InvocationType='RequestResponse',
            Payload=json.dumps(group_details_event)
        )
        group_details_response = json.loads(group_details_lambda_response.get('Payload').read())
        logger.info(f"get_group_for_org response: {group_details_response}")
        if group_details_response["statusCode"] != 200:
            raise Exception(f"Failed to fetch group details for org_id:{org_id} "
                            f"group_id {group_id}")

        group_details_response_body = json.loads(group_details_response["body"])
        groups = group_details_response_body["data"]["groups"]
        if len(groups) == 0:
            raise Exception(f"Failed to find group {group_id} for org_id: {org_id}")
        return groups[0]["payment"]["payment_address"]

    def calculate_amount_in_cogs(self, amount, currency):
        if currency == "USD":
            amount_in_cogs = round(amount * USD_TO_COGS_CONVERSION_FACTOR)
            return amount_in_cogs
        else:
            raise Exception("Currency %s not supported.", currency)

    def execute_order(self, username, payload_dict):
        """
            Execute Order
                Step 1  Execute Payment
                Step 2  Get Receipient Address
                Step 3  Process Order
                Step 4  Update Transaction History
        """
        order_id = payload_dict["order_id"]
        payment_id = payload_dict["payment_id"]
        order = self.get_order_details_by_order_id(order_id, username)
        payment = None
        for payment_item in order["payments"]:
            if payment_item["payment_id"] == payment_id:
                payment = payment_item
                break

        if payment is None:
            raise Exception(f"Failed to fetch order details for order_id {order_id} \n"
                            f"payment_id {payment_id} \n"
                            f"username{username}")

        order_type = order["item_details"]["order_type"]
        item_details = order["item_details"]
        payment_method = payment["payment_details"]["payment_method"]
        paid_payment_details = payload_dict["payment_details"]
        price = payment["price"]
        status = Status.PAYMENT_EXECUTION_FAILED.value
        self.manage_execute_payment(
            username=username, order_id=order_id, payment_id=payment_id,
            payment_details=paid_payment_details, payment_method=payment_method
        )

        status = Status.PAYMENT_EXECUTED.value
        try:
            status = Status.ORDER_PROCESSING_FAILED.value
            amount_in_cogs = self.calculate_amount_in_cogs(amount=price["amount"], currency=price["currency"])
            if amount_in_cogs < 1:
                raise Exception("Amount in cogs should be greater than equal to 1")
            processed_order_data = self.manage_process_order(
                username=username,
                order_id=order_id, order_type=order_type,
                amount=price["amount"],
                currency=price["currency"], order_data=item_details,
                amount_in_cogs=amount_in_cogs
            )
            status = Status.ORDER_PROCESSED.value
            obj_transaction_history = TransactionHistory(
                username=username, order_id=order_id, order_type=order_type,
                status=status, payment_id=payment_id,
                payment_method=payment_method,
                raw_payment_data=json.dumps(paid_payment_details)
            )
            self.obj_transaction_history_dao.insert_transaction_history(obj_transaction_history=obj_transaction_history)
            processed_order_data["price"] = price
            processed_order_data["item_details"] = item_details
            return processed_order_data

        except Exception as e:
            obj_transaction_history = TransactionHistory(
                username=username, order_id=order_id,
                order_type=order_type, status=status
            )
            self.obj_transaction_history_dao.insert_transaction_history(obj_transaction_history=obj_transaction_history)
            print(repr(e))
            raise e

    def get_order_details_by_order_id(self, order_id, username):
        order_details_event = {
            "path": f"order/{order_id}",
            "pathParameters": {"order_id": order_id},
            "httpMethod": "GET"
        }

        logger.info(f"Requesting order details for order_id {order_id}")
        response = self.lambda_client.invoke(
            FunctionName=ORDER_DETAILS_ORDER_ID_ARN,
            InvocationType='RequestResponse',
            Payload=json.dumps(order_details_event)
        )
        order_details_response = json.loads(response.get('Payload').read())
        if order_details_response["statusCode"] != 200:
            raise Exception(f"Failed to fetch order details for order_id {order_id} username{username}")

        order_details_data = json.loads(order_details_response["body"])
        if order_details_data["username"] != username:
            raise Exception(f"Failed to fetch order details for order_id {order_id} username{username}")
        return order_details_data

    def manage_initiate_payment(self, username, order_id, price, payment_method):
        initiate_payment_event = {
            "pathParameters": {"order_id": order_id},
            "httpMethod": "POST",
            "body": json.dumps({"price": price, "payment_method": payment_method})
        }
        response = self.lambda_client.invoke(
            FunctionName=INITIATE_PAYMENT_SERVICE_ARN,
            InvocationType='RequestResponse',
            Payload=json.dumps(initiate_payment_event)
        )
        initiate_payment_data = json.loads(response.get('Payload').read())
        if initiate_payment_data["statusCode"] == 201:
            return json.loads(initiate_payment_data["body"])
        else:
            logger.error("Error initiating payment for user %s", username)
            raise PaymentInitiateFailed

    def manage_create_order(self, username, item_details, price):
        create_order_event = {
            "path": "/order/create",
            "httpMethod": "POST",
            "body": json.dumps({"price": price, "item_details": item_details, "username": username})
        }
        create_order_service_response = self.boto_client.invoke_lambda(
            lambda_function_arn=CREATE_ORDER_SERVICE_ARN,
            invocation_type='RequestResponse',
            payload=json.dumps(create_order_event)
        )
        logger.info(f"create_order_service_response: {create_order_service_response}")

        if create_order_service_response["statusCode"] == 201:
            return json.loads(create_order_service_response["body"])
        else:
            raise Exception(f"Error creating order for user {username}")

    def manage_execute_payment(self, username, order_id, payment_id, payment_details, payment_method):
        execute_payment_event = {
            "pathParameters": {"order_id": order_id, "payment_id": payment_id},
            "body": json.dumps({"payment_method": payment_method, "payment_details": payment_details})
        }
        response = self.lambda_client.invoke(
            FunctionName=EXECUTE_PAYMENT_SERVICE_ARN,
            InvocationType='RequestResponse',
            Payload=json.dumps(execute_payment_event)
        )
        payment_executed = json.loads(response.get('Payload').read())
        if payment_executed["statusCode"] == 201:
            return payment_executed
        else:
            raise Exception(f"Error executing payment for username {username} against order_id {order_id}")

    def manage_process_order(self, username, order_id, order_type, amount, currency, order_data, amount_in_cogs):
        logger.info(f"Order Data {order_data}")
        group_id = order_data["group_id"]
        org_id = order_data["org_id"]
        recipient = order_data["recipient"]
        channel_id = order_data["channel_id"]
        sender = order_data["wallet_address"]
        if order_type == OrderType.CREATE_WALLET_AND_CHANNEL.value or order_type == OrderType.CREATE_CHANNEL.value:

            if order_type == OrderType.CREATE_WALLET_AND_CHANNEL.value:
                wallet_create_payload = {
                    "path": "/wallet",
                    "body": json.dumps({"username": username}),
                    "httpMethod": "POST"
                }
                wallet_create_lambda_response = self.lambda_client.invoke(
                    FunctionName=WALLETS_SERVICE_ARN,
                    InvocationType='RequestResponse',
                    Payload=json.dumps(wallet_create_payload)
                )
                wallet_create_response = json.loads(wallet_create_lambda_response.get("Payload").read())
                if wallet_create_response["statusCode"] != 200:
                    raise Exception("Failed to create wallet")
                wallet_create_response_body = json.loads(wallet_create_response["body"])
                wallet_details = wallet_create_response_body["data"]
            else:



            try:
                current_block_no = self.obj_blockchain_util.get_current_block_no()
                # 1 block no is mined in 15 sec on average, setting expiration as 10 years
                expiration = current_block_no + (10 * 365 * 24 * 60 * 4)
                message_nonce = current_block_no
                self.EXECUTOR_WALLET_ADDRESS = self.boto_client.get_ssm_parameter(EXECUTOR_ADDRESS)
                group_id_in_hex = "0x" + base64.b64decode(group_id).hex()
                signature_details = self.generate_signature_for_open_channel_for_third_party(
                    recipient=recipient, group_id=group_id_in_hex,
                    amount_in_cogs=amount_in_cogs, expiration=expiration,
                    message_nonce=message_nonce, sender_private_key=wallet_details["private_key"],
                    executor_wallet_address=self.EXECUTOR_WALLET_ADDRESS
                )

                logger.info(f"Signature Details {signature_details}")
                open_channel_body = {
                    'order_id': order_id,
                    'sender': wallet_details["address"],
                    'signature': signature_details["signature"],
                    'r': signature_details["r"],
                    's': signature_details["s"],
                    'v': signature_details["v"],
                    'group_id': group_id,
                    'org_id': org_id,
                    'amount': amount,
                    'currency': currency,
                    'recipient': recipient,
                    'current_block_no': current_block_no,
                    'amount_in_cogs': amount_in_cogs
                }
                channel_details = self.wallet_service.create_channel(open_channel_body=open_channel_body)
                channel_details.update(wallet_details)
                return channel_details
            except Exception as e:
                logger.error("Failed to create channel")
                logger.error(repr(e))
                response = {
                    "transaction_hash": "",
                    "signature": "",
                    "amount_in_cogs": 0,
                    "price": {
                        "amount": amount,
                        "currency": currency
                    },
                    "item_details": order_data
                }
                response.update(wallet_details)
                raise ChannelCreationFailed("Failed to create channel", wallet_details=response)

        elif order_type == OrderType.CREATE_CHANNEL.value:
            try:
                logger.info(f"Order Data {order_data}")
                signature = order_data["signature"]
                v, r, s = Web3.toInt(hexstr="0x" + signature[-2:]), signature[:66], "0x" + signature[66:130]
                open_channel_body = {
                    'order_id': order_id, 'sender': order_data["wallet_address"],
                    'signature': order_data["signature"], 'r': r, 's': s, 'v': v,
                    'group_id': group_id, 'org_id': org_id, 'amount': amount, 'currency': currency,
                    'recipient': recipient, 'current_block_no': order_data["current_block_number"],
                    'amount_in_cogs': amount_in_cogs
                }
                channel_details = self.wallet_service.create_channel(open_channel_body=open_channel_body)
                logger.info(f"channel_details: {channel_details}")
                return channel_details
            except Exception as e:
                logger.error("Failed to create channel")
                print(repr(e))
                raise ChannelCreationFailed("Failed to create channel", wallet_details=order_data)

        elif order_type == OrderType.FUND_CHANNEL.value:

            try:
                fund_channel_body = {
                    'order_id': order_id,
                    'group_id': group_id,
                    'org_id': org_id,
                    'amount': amount,
                    'channel_id': channel_id,
                    'currency': currency,
                    'recipient': recipient,
                    'sender': sender,
                    'amount_in_cogs': amount_in_cogs
                }
                fund_channel_payload = {
                    "path": "/wallet/channel/deposit",
                    "body": json.dumps(fund_channel_body),
                    "httpMethod": "POST"
                }

                fund_channel_lambda_response = self.lambda_client.invoke(
                    FunctionName=WALLETS_SERVICE_ARN,
                    InvocationType='RequestResponse',
                    Payload=json.dumps(fund_channel_payload)
                )

                fund_channel_response = json.loads(fund_channel_lambda_response.get("Payload").read())
                if fund_channel_response["statusCode"] != 200:
                    raise Exception(f"Failed to add funds in channel for {fund_channel_body}")

                fund_channel_response_body = json.loads(fund_channel_response["body"])
                fund_channel_transaction_details = fund_channel_response_body["data"]
                return fund_channel_transaction_details
            except Exception as e:
                logger.error("Failed to fund channel")
                logger.error(repr(e))
                raise FundChannelFailed()
        else:
            raise Exception("Order type is not valid.")

    def get_order_details_by_username(self, username):
        order_details_event = {
            "path": f"/order",
            "queryStringParameters": {"username": username},
            "httpMethod": "GET"
        }

        logger.info(f"Requesting order details for username {username}")
        order_details_response = self.boto_client.invoke_lambda(
            lambda_function_arn=ORDER_DETAILS_BY_USERNAME_ARN,
            invocation_type='RequestResponse',
            payload=json.dumps(order_details_event)
        )
        if order_details_response["statusCode"] != 200:
            raise Exception(f"Failed to fetch order details for username{username}")

        org_id_name_mapping = self.get_organizations_from_contract()

        order_details_response_body = json.loads(order_details_response["body"])
        orders = order_details_response_body["orders"]

        for order in orders:
            order_id = order["order_id"]
            order["wallet_type"] = "GENERAL"
            if "org_id" in order["item_details"]:
                org_id = order["item_details"]["org_id"]
                if org_id in org_id_name_mapping:
                    order["item_details"]["organization_name"] = org_id_name_mapping[org_id]

            transaction_details_event = {
                "path": f"/wallet/channel/transactions",
                "queryStringParameters": {"order_id": order_id},
                "httpMethod": "GET"
            }
            transaction_details_lambda_response = self.lambda_client.invoke(
                FunctionName=WALLETS_SERVICE_ARN,
                InvocationType='RequestResponse',
                Payload=json.dumps(transaction_details_event)
            )
            transaction_details_response = json.loads(transaction_details_lambda_response.get('Payload').read())
            if transaction_details_response["statusCode"] != 200:
                raise Exception(f"Failed to fetch transaction details for username{order_id}")
            transaction_details_response_body = json.loads(transaction_details_response["body"])
            order["wallet_transactions"] = transaction_details_response_body["data"]["transactions"]
            order_status = TransactionStatus.SUCCESS
            for payment in order["payments"]:
                if payment["payment_status"] != TransactionStatus.SUCCESS:
                    order_status = payment["payment_status"]
                    break

            for wallet_transaction in order["wallet_transactions"]:
                if wallet_transaction["status"] != TransactionStatus.SUCCESS:
                    order_status = wallet_transaction["status"]
                    break

            order["order_status"] = order_status
        return {"orders": orders}

    def get_organizations_from_contract(self):
        org_details_event = {
            "path": f"/org",
            "httpMethod": "GET"
        }
        org_details_response = self.boto_client.invoke_lambda(
            lambda_function_arn=GET_ALL_ORG_API_ARN,
            invocation_type='RequestResponse',
            payload=json.dumps(org_details_event)
        )
        if org_details_response["statusCode"] != 200:
            raise Exception("Failed to get org details")

        org_details = json.loads(org_details_response["body"])["data"]
        org_id_name_mapping = {}
        for org in org_details:
            org_id_name_mapping[org["org_id"]] = org["org_name"]

        return org_id_name_mapping

    def generate_signature_for_open_channel_for_third_party(self, recipient, group_id, amount_in_cogs, expiration,
                                                            message_nonce, sender_private_key, executor_wallet_address):

        signature_for_open_channel_for_third_party_body = {
            'recipient': recipient,
            'group_id': group_id,
            'amount_in_cogs': amount_in_cogs,
            'expiration': expiration,
            'message_nonce': message_nonce,
            'signer_key': sender_private_key,
            'executor_wallet_address': executor_wallet_address
        }

        signature_for_open_channel_for_third_party_payload = {
            "path": "/signer/open-channel-for-third-party",
            "body": json.dumps(signature_for_open_channel_for_third_party_body),
            "httpMethod": "POST"
        }

        signature_for_open_channel_for_third_party_response = self.lambda_client.invoke(
            FunctionName=SIGNER_SERVICE_ARN,
            InvocationType='RequestResponse',
            Payload=json.dumps(signature_for_open_channel_for_third_party_payload)
        )

        signature_response = json.loads(signature_for_open_channel_for_third_party_response.get("Payload").read())
        if signature_response["statusCode"] != 200:
            raise Exception(f"Failed to create signature for {signature_for_open_channel_for_third_party_body}")
        signature_details = json.loads(signature_response["body"])
        return signature_details["data"]

    def cancel_order(self):
        logger.info("Start of UpdateTransactionStatus::manage_update_canceled_order_in_txn_history")
        list_of_order_id_for_expired_transaction = self.obj_transaction_history_dao.get_order_id_for_expired_transaction()
        logger.info(f"List of order_id to be updated with ORDER CANCELED: {list_of_order_id_for_expired_transaction}")
        update_transaction_status = self.obj_transaction_history_dao.update_transaction_status(
            list_of_order_id=list_of_order_id_for_expired_transaction, status=OrderStatus.ORDER_CANCELED.value)
        return update_transaction_status

    def cancel_order_for_given_order_id(self, order_id):
        logger.info("UpdateTransactionStatus::cancel_order_for_given_order_id: %s", order_id)
        transaction_data_dict = self.obj_transaction_history_dao.get_transaction_details_for_given_order_id(
            order_id=order_id)
        if transaction_data_dict["status"] == OrderStatus.ORDER_CANCELED.value:
            return f"Order with order_id {order_id} is already canceled."
        elif transaction_data_dict["status"] in [OrderStatus.PAYMENT_INITIATED.value,
                                                 OrderStatus.PAYMENT_INITIATION_FAILED.value,
                                                 OrderStatus.PAYMENT_EXECUTION_FAILED]:
            self.obj_transaction_history_dao.update_transaction_status(list_of_order_id=[order_id],
                                                                       status=OrderStatus.ORDER_CANCELED.value)
            return f"Order with order_id {order_id} is canceled successfully."
        else:
            return f"Unable to cancel order with order_id {order_id}"

    def currency_to_token(self, amount, currency):
        amount_in_cogs = self.calculate_amount_in_cogs(amount=decimal.Decimal(amount), currency=currency)
        conversion_data = {"base": currency, "amount": amount, "amount_in_cogs": str(amount_in_cogs),
                           "amount_in_agi": str(self.utils.cogs_to_agi(cogs=amount_in_cogs)),
                           f"{currency}/cogs": str(USD_TO_COGS_CONVERSION_FACTOR), "agi/cogs": str(COGS_TO_AGI)}
        logger.debug(f"currency_to_token::conversion_data {conversion_data}")
        return conversion_data
