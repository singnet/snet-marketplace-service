import json
from enum import Enum
from urllib.parse import quote

import boto3

from orchestrator.config import CONTRACT_API_ARN
from orchestrator.config import CREATE_ORDER_SERVICE_ARN
from orchestrator.config import EXECUTE_PAYMENT_SERVICE_ARN
from orchestrator.config import INITIATE_PAYMENT_SERVICE_ARN
from orchestrator.config import ORDER_DETAILS_BY_USERNAME_ARN
from orchestrator.config import ORDER_DETAILS_ORDER_ID_ARN
from orchestrator.config import WALLETS_SERVICE_ARN
from orchestrator.transaction_history import TransactionHistory
from orchestrator.transaction_history_data_access_object import TransactionHistoryDAO


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
        self.obj_transaction_history_dao = TransactionHistoryDAO(
            obj_repo=self.repo)
        self.lambda_client = boto3.client("lambda")

    def initiate_order(self, user_data, payload_dict):
        """
            Initiate Order
                Step 1  Order Creation
                Step 2  Initiate Payment
                Step 3  Persist Transaction History
        """
        username = user_data["authorizer"]["claims"]["email"]
        price = payload_dict["price"]
        order_type = payload_dict["item_details"]["order_type"]
        item_details = payload_dict["item_details"]
        group_id = item_details["group_id"]
        org_id = item_details["org_id"]

        recipient = self.get_payment_address_for_org(group_id=group_id,
                                                     org_id=org_id)
        item_details["recipient"] = recipient
        order_details = self.manage_create_order(username=username,
                                                 item_details=item_details,
                                                 price=price)
        order_id = order_details["order_id"]
        try:
            payment_data = self.manage_initiate_payment(
                username=username,
                order_id=order_id,
                price=price,
                payment_method=payload_dict["payment_method"],
            )
            payment_id = payment_data["payment_id"]
            raw_payment_data = json.dumps(payment_data["payment"])
            obj_transaction_history = TransactionHistory(
                username=username,
                order_id=order_id,
                order_type=order_type,
                payment_id=payment_id,
                raw_payment_data=raw_payment_data,
                status=Status.SUCCESS.value,
            )
            self.obj_transaction_history_dao.insert_transaction_history(
                obj_transaction_history=obj_transaction_history)
            return payment_data
        except Exception as e:
            obj_transaction_history = TransactionHistory(
                username=username,
                order_id=order_id,
                order_type=order_type,
                status=Status.PAYMENT_INITIATION_FAILED.value,
            )
            self.obj_transaction_history_dao.insert_transaction_history(
                obj_transaction_history=obj_transaction_history)
            print(repr(e))
            raise e

    def get_payment_address_for_org(self, org_id, group_id):

        group_details_event = {
            "path": f"/org/{org_id}/group/{quote(group_id, safe='')}",
            "pathParameters": {
                "org_id": org_id,
                "group_id": quote(group_id, safe="")
            },
            "httpMethod": "GET",
        }
        group_details_lambda_response = self.lambda_client.invoke(
            FunctionName=CONTRACT_API_ARN,
            InvocationType="RequestResponse",
            Payload=json.dumps(group_details_event),
        )
        group_details_response = json.loads(
            group_details_lambda_response.get("Payload").read())
        if group_details_response["statusCode"] != 200:
            raise Exception(
                f"Failed to fetch group details for org_id:{org_id} "
                f"group_id {group_id}")

        group_details_response_body = json.loads(
            group_details_response["body"])
        groups = group_details_response_body["data"]["groups"]
        if len(groups) == 0:
            raise Exception(
                f"Failed to find group {group_id} for org_id: {org_id}")
        return groups[0]["payment"]["payment_address"]

    def get_channel_transactions(self, username, recipient):

        channel_transactions_event = {
            "path": "/wallet/channel/transactions",
            "queryStringParameters": {
                "username": username,
                "recipient": recipient
            },
            "httpMethod": "GET",
        }

        channel_transactions_lambda_response = self.lambda_client.invoke(
            FunctionName=WALLETS_SERVICE_ARN,
            InvocationType="RequestResponse",
            Payload=json.dumps(channel_transactions_event),
        )
        channel_transactions_response = json.loads(
            channel_transactions_lambda_response.get("Payload").read())
        if channel_transactions_response["statusCode"] != 200:
            raise Exception(
                f"Failed to fetch wallet details for username: {username}")

        channel_transactions_response_body = json.loads(
            channel_transactions_response["body"])
        channel_transactions = channel_transactions_response_body["data"][
            "wallets"]
        return channel_transactions

    def get_channel_details(self, username, org_id, group_id):
        """ Method to get wallet details for a given username. """
        try:
            recipient = self.get_payment_address_for_org(group_id=group_id,
                                                         org_id=org_id)
            wallet_channel_transactions = self.get_channel_transactions(
                username, recipient)
            wallet_response = {
                "username": username,
                "org_id": org_id,
                "group_id": group_id,
                "recipient": recipient,
                "wallets": wallet_channel_transactions,
            }
            for wallet in wallet_response["wallets"]:
                user_address = wallet["address"]
                wallet["channels"] = self.get_channels_from_contract(
                    user_address=user_address,
                    org_id=org_id,
                    group_id=group_id)
            return wallet_response
        except Exception as e:
            print(repr(e))
            raise e

    def get_channels_from_contract(self, user_address, org_id, group_id):
        event = {
            "requestContext": {
                "stage": "ropsten"
            },
            "httpMethod": "GET",
            "path": "/channel",
            "queryStringParameters": {
                "user_address": user_address,
                "org_id": org_id,
                "group_id": group_id,
            },
        }
        channel_details_lambda_response = self.lambda_client.invoke(
            FunctionName=CONTRACT_API_ARN,
            InvocationType="RequestResponse",
            Payload=json.dumps(event),
        )
        channel_details_response = json.loads(
            channel_details_lambda_response.get("Payload").read())
        if channel_details_response["statusCode"] != 200:
            raise Exception(
                f"Failed to get channel details from contract API username: {user_address} "
                f"group_id: {group_id} "
                f"org_id: {org_id}")
        channel_details = json.loads(channel_details_response["body"])["data"]
        return channel_details["channels"]

    def execute_order(self, user_data, payload_dict):
        """
            Execute Order
                Step 1  Execute Payment
                Step 2  Get Receipient Address
                Step 3  Process Order
                Step 4  Update Transaction History
        """
        order_id = payload_dict["order_id"]
        payment_id = payload_dict["payment_id"]
        username = user_data["authorizer"]["claims"]["email"]
        order = self.get_order_details_by_order_id(order_id, username)
        payment = None
        for payment_item in order["payments"]:
            if payment_item["payment_id"] == payment_id:
                payment = payment_item
                break

        if payment is None:
            raise Exception(
                f"Failed to fetch order details for order_id {order_id} \n"
                f"payment_id {payment_id} \n"
                f"username{username}")

        order_type = order["item_details"]["order_type"]
        item_details = order["item_details"]
        payment_method = payment["payment_details"]["payment_method"]
        paid_payment_details = payload_dict["payment_details"]
        price = payment["price"]
        status = Status.PAYMENT_EXECUTION_FAILED.value
        self.manage_execute_payment(
            username=username,
            order_id=order_id,
            payment_id=payment_id,
            payment_details=paid_payment_details,
            payment_method=payment_method,
        )
        status = Status.PAYMENT_EXECUTED.value
        try:
            status = Status.ORDER_PROCESSING_FAILED.value
            processed_order_data = self.manage_process_order(
                username=username,
                order_id=order_id,
                order_type=order_type,
                amount=price["amount"],
                currency=price["currency"],
                order_data=item_details,
            )
            status = Status.ORDER_PROCESSED.value
            obj_transaction_history = TransactionHistory(
                username=username,
                order_id=order_id,
                order_type=order_type,
                status=status,
                payment_id=payment_id,
                payment_method=payment_method,
                raw_payment_data=json.dumps(paid_payment_details),
                transaction_hash=processed_order_data["transaction_hash"],
            )
            self.obj_transaction_history_dao.insert_transaction_history(
                obj_transaction_history=obj_transaction_history)
            processed_order_data["price"] = price
            processed_order_data["item_details"] = item_details
            return processed_order_data

        except Exception as e:
            obj_transaction_history = TransactionHistory(
                username=username,
                order_id=order_id,
                order_type=order_type,
                status=status,
            )
            self.obj_transaction_history_dao.insert_transaction_history(
                obj_transaction_history=obj_transaction_history)
            print(repr(e))
            raise e

    def get_order_details_by_username(self, username):
        order_details_event = {
            "path": f"/order",
            "queryStringParameters": {
                "username": username
            },
            "httpMethod": "GET",
        }

        order_details_lambda_response = self.lambda_client.invoke(
            FunctionName=ORDER_DETAILS_BY_USERNAME_ARN,
            InvocationType="RequestResponse",
            Payload=json.dumps(order_details_event),
        )
        order_details_response = json.loads(
            order_details_lambda_response.get("Payload").read())
        if order_details_response["statusCode"] != 200:
            raise Exception(
                f"Failed to fetch order details for username{username}")

        order_details_response_body = json.loads(
            order_details_response["body"])
        orders = order_details_response_body["orders"]

        for order in orders:
            order_id = order["order_id"]
            transaction_details_event = {
                "path": f"/wallet/channel/transactions",
                "queryStringParameters": {
                    "order_id": order_id
                },
                "httpMethod": "GET",
            }
            transaction_details_lambda_response = self.lambda_client.invoke(
                FunctionName=WALLETS_SERVICE_ARN,
                InvocationType="RequestResponse",
                Payload=json.dumps(transaction_details_event),
            )
            transaction_details_response = json.loads(
                transaction_details_lambda_response.get("Payload").read())
            if transaction_details_response["statusCode"] != 200:
                raise Exception(
                    f"Failed to fetch transaction details for username{order_id}"
                )
            transaction_details_response_body = json.loads(
                transaction_details_response["body"])
            order["wallet_transactions"] = transaction_details_response_body[
                "data"]["transactions"]

        return {"orders": orders}

    def get_order_details_by_order_id(self, order_id, username):
        order_details_event = {
            "path": f"order/{order_id}",
            "pathParameters": {
                "order_id": order_id
            },
            "httpMethod": "GET",
        }
        response = self.lambda_client.invoke(
            FunctionName=ORDER_DETAILS_ORDER_ID_ARN,
            InvocationType="RequestResponse",
            Payload=json.dumps(order_details_event),
        )
        order_details_response = json.loads(response.get("Payload").read())
        if order_details_response["statusCode"] != 200:
            raise Exception(
                f"Failed to fetch order details for order_id {order_id} username{username}"
            )

        order_details_data = json.loads(order_details_response["body"])
        if order_details_data["username"] != username:
            raise Exception(
                f"Failed to fetch order details for order_id {order_id} username{username}"
            )
        return order_details_data

    def manage_initiate_payment(self, username, order_id, price,
                                payment_method):
        initiate_payment_event = {
            "pathParameters": {
                "order_id": order_id
            },
            "httpMethod": "POST",
            "body": json.dumps({
                "price": price,
                "payment_method": payment_method
            }),
        }
        response = self.lambda_client.invoke(
            FunctionName=INITIATE_PAYMENT_SERVICE_ARN,
            InvocationType="RequestResponse",
            Payload=json.dumps(initiate_payment_event),
        )
        initiate_payment_data = json.loads(response.get("Payload").read())
        if initiate_payment_data["statusCode"] == 201:
            return json.loads(initiate_payment_data["body"])
        else:
            raise Exception("Error initiating payment for user %s", username)

    def manage_create_order(self, username, item_details, price):
        create_order_event = {
            "path":
            "/order/create",
            "httpMethod":
            "POST",
            "body":
            json.dumps({
                "price": price,
                "item_details": item_details,
                "username": username
            }),
        }
        response = self.lambda_client.invoke(
            FunctionName=CREATE_ORDER_SERVICE_ARN,
            InvocationType="RequestResponse",
            Payload=json.dumps(create_order_event),
        )
        create_order_service_response = json.loads(
            response.get("Payload").read())
        print("create_order_service_response==", create_order_service_response)
        if create_order_service_response["statusCode"] == 201:
            return json.loads(create_order_service_response["body"])
        else:
            raise Exception(f"Error creating order for user {username}")

    def manage_execute_payment(self, username, order_id, payment_id,
                               payment_details, payment_method):
        execute_payment_event = {
            "pathParameters": {
                "order_id": order_id,
                "payment_id": payment_id
            },
            "body":
            json.dumps({
                "payment_method": payment_method,
                "payment_details": payment_details
            }),
        }
        response = self.lambda_client.invoke(
            FunctionName=EXECUTE_PAYMENT_SERVICE_ARN,
            InvocationType="RequestResponse",
            Payload=json.dumps(execute_payment_event),
        )
        payment_executed = json.loads(response.get("Payload").read())
        if payment_executed["statusCode"] == 201:
            return payment_executed
        else:
            raise Exception(
                f"Error executing payment for username {username} against order_id {order_id}"
            )

    def manage_process_order(self, username, order_id, order_type, amount,
                             currency, order_data):
        if order_type == OrderType.CREATE_WALLET_AND_CHANNEL.value:
            wallet_create_payload = {
                "path": "/wallet",
                "body": json.dumps({"username": username}),
                "httpMethod": "POST",
            }
            wallet_create_lambda_response = self.lambda_client.invoke(
                FunctionName=WALLETS_SERVICE_ARN,
                InvocationType="RequestResponse",
                Payload=json.dumps(wallet_create_payload),
            )
            wallet_create_response = json.loads(
                wallet_create_lambda_response.get("Payload").read())
            if wallet_create_response["statusCode"] != 200:
                raise Exception("Failed to create wallet")
            wallet_create_response_body = json.loads(
                wallet_create_response["body"])
            wallet_details = wallet_create_response_body["data"]
            recipient = order_data["recipient"]

            open_channel_body = {
                "order_id": order_id,
                "sender": wallet_details["address"],
                "sender_private_key": wallet_details["private_key"],
                "group_id": order_data["group_id"],
                "amount": amount,
                "currency": currency,
                "recipient": recipient,
            }

            create_channel_transaction_payload = {
                "path": "/wallet/channel",
                "body": json.dumps(open_channel_body),
                "httpMethod": "POST",
            }

            create_channel_lambda_response = self.lambda_client.invoke(
                FunctionName=WALLETS_SERVICE_ARN,
                InvocationType="RequestResponse",
                Payload=json.dumps(create_channel_transaction_payload),
            )

            create_channel_response = json.loads(
                create_channel_lambda_response["Payload"].read())
            if create_channel_response["statusCode"] != 200:
                raise Exception(
                    f"Failed to create channel for {open_channel_body}")

            create_channel_response_body = json.loads(
                create_channel_response["body"])
            channel_details = create_channel_response_body["data"]

            channel_details.update(wallet_details)
            return channel_details
        elif order_type == OrderType.CREATE_CHANNEL.value:
            pass
        elif order_type == OrderType.FUND_CHANNEL.value:
            fund_channel_body = {
                "order_id": order_id,
                "amount": amount,
                "currency": currency,
            }
            fund_channel_payload = {
                "path": "/wallet/channel/deposit",
                "body": json.dumps(fund_channel_body),
                "httpMethod": "POST",
            }

            fund_channel_lambda_response = self.lambda_client.invoke(
                FunctionName=WALLETS_SERVICE_ARN,
                InvocationType="RequestResponse",
                Payload=json.dumps(fund_channel_payload),
            )

            fund_channel_response = json.loads(
                fund_channel_lambda_response.get("Payload").read())
            if fund_channel_response["statusCode"] != 200:
                raise Exception(
                    f"Failed to add funds in channel for {fund_channel_body}")

            fund_channel_response_body = fund_channel_response["body"]
            fund_channel_transaction_details = fund_channel_response_body[
                "data"]
            return fund_channel_transaction_details
        else:
            raise Exception("Order type is not valid.")

    def get_receipient_address(self):
        return ""
