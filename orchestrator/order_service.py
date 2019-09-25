import json
import boto3

from enum import Enum
from orchestrator.config import CREATE_ORDER_SERVICE_ARN, INITIATE_PAYMENT_SERVICE_ARN, EXECUTE_PAYMENT_SERVICE_ARN
from orchestrator.transaction_history import TransactionHistory
from orchestrator.transaction_history_data_access_object import TransactionHistoryDAO
from wallets.wallet_service import WalletService


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
        self.obj_repo = obj_repo
        self.obj_transaction_history_dao = TransactionHistoryDAO(obj_repo=self.obj_repo)
        self.lambda_client = boto3.client('lambda')

    def initiate_order(self, user_data, payload_dict):
        """
            Initiate Order
                Step 1  Order Creation
                Step 2  Initiate Payment
                Step 3  Persist Transaction History
        """
        username = user_data["authorizer"]["claims"]["email"]
        price = payload_dict["price"]
        order_type = payload_dict["order_type"]
        order_details = self.manage_create_order(username=username, item_details=payload_dict["item_details"],
                                                 price=price)
        order_id = order_details["order_id"]
        try:
            redirect_response = self.manage_initiate_payment(username=username, order_id=order_id, price=price,
                                                             payment_method=payload_dict["payment_method"])
            payment_data = json.loads(redirect_response["body"])
            payment_id = payment_data["payment_id"]
            raw_payment_data = json.dumps(payment_data["payment"])
            obj_transaction_history = TransactionHistory(username=username, order_id=order_id, order_type=order_type,
                                                         payment_id=payment_id, raw_payment_data=raw_payment_data,
                                                         status=Status.SUCCESS.value)
            self.obj_transaction_history_dao.insert_transaction_history(obj_transaction_history=obj_transaction_history)
            redirect_response["statusCode"] = 301
            return redirect_response
        except Exception as e:
            obj_transaction_history = TransactionHistory(username=username, order_id=order_id, order_type=order_type,
                                                         status=Status.PAYMENT_INITIATION_FAILED.value)
            self.obj_transaction_history_dao.insert_transaction_history(obj_transaction_history=obj_transaction_history)
            print(repr(e))
            raise e

    def execute_order(self, user_data, payload_dict):
        """
            Execute Order
                Step 1  Execute Payment
                Step 2  Get Receipient Address
                Step 3  Process Order
                Step 4  Update Transaction History
        """
        username = user_data["authorizer"]["claims"]["email"]
        order_id = payload_dict["order_id"]
        order_type = payload_dict["order_type"]
        item_details=payload_dict["item_details"]
        payment_id = payload_dict["payment_id"]
        payment_method = payload_dict["payment_method"]
        payment_details = payload_dict["payment_details"]
        price = payload_dict["price"]
        status = Status.PAYMENT_EXECUTION_FAILED.value
        payment_executed = self.manage_execute_payment(username=username, order_id=order_id, payment_id=payment_id,
                                                       payment_details=payment_details, payment_method=payment_method)
        status = Status.PAYMENT_EXECUTED.value
        try:
            status = Status.ORDER_PROCESSING_FAILED.value
            processed_order_data = self.manage_process_order(order_id=order_id, order_type=order_type, amount=price["amount"],
                                             currency=price["currency"], order_data=item_details)
            status = Status.ORDER_PROCESSED.value
            obj_transaction_history = TransactionHistory(username=username, order_id=order_id, order_type=order_type,
                                                         status=status, payment_id=payment_id, 
                                                         payment_method=payment_method, 
                                                         raw_payment_data=json.dumps(payment_details),
                                                         transaction_hash=processed_order_data["transaction_hash"])
            self.obj_transaction_history_dao.insert_transaction_history(obj_transaction_history=obj_transaction_history)
            return processed_order_data

        except Exception as e:
            obj_transaction_history = TransactionHistory(username=username, order_id=order_id, order_type=order_type,
                                                         status=status)
            self.obj_transaction_history_dao.insert_transaction_history(obj_transaction_history=obj_transaction_history)
            print(repr(e))
            raise e

    def manage_initiate_payment(self, username, order_id, price, payment_method):
        initiate_payment_event = {
           "pathParameters": {"order_id": order_id},
           "httpMethod":"POST",
           "body": json.dumps({"price": price, "payment_method": payment_method})
        }
        response = self.lambda_client.invoke(FunctionName=INITIATE_PAYMENT_SERVICE_ARN,
                                             InvocationType='RequestResponse',
                                             Payload=json.dumps(initiate_payment_event))
        initiate_payment_data = json.loads(response.get('Payload').read())
        if initiate_payment_data["statusCode"] == 201:
            return initiate_payment_data
        else:
            raise Exception("Error initiating payment for user %s", username)

    def manage_create_order(self, username, item_details, price):
        create_order_event = {
            "path": "/order/create",
            "httpMethod": "POST",
            "body": json.dumps({ "price": price, "item_details": item_details, "username": username})
        }
        response = self.lambda_client.invoke(FunctionName=CREATE_ORDER_SERVICE_ARN,
                                             InvocationType='RequestResponse',
                                             Payload=json.dumps(create_order_event))
        create_order_service_response = json.loads(response.get('Payload').read())
        print("create_order_service_response==", create_order_service_response)
        if create_order_service_response["statusCode"] == 201:
            return json.loads(create_order_service_response["body"])
        else:
            raise Exception("Error creating order for user %s", username)

    def manage_execute_payment(self, username, order_id, payment_id, payment_details, payment_method):
        execute_payment_event = {
             "pathParameters": {"order_id": order_id, "payment_id": payment_id},
             "body": json.dumps({"payment_method": payment_method, "payment_details": payment_details})
        }
        response = self.lambda_client.invoke(FunctionName=EXECUTE_PAYMENT_SERVICE_ARN,
                                             InvocationType='RequestResponse',
                                             Payload=json.dumps(execute_payment_event))
        payment_executed = json.loads(response.get('Payload').read())
        if payment_executed["statusCode"] == 201:
            return payment_executed
        else:
            raise Exception("Error executing payment for username %s against order_id %s", username, order_id)

    def manage_process_order(self, order_id, order_type, amount, currency, order_data):
        obj_wallets_service = WalletService(obj_repo=self.obj_repo)
        if order_type == OrderType.CREATE_WALLET_AND_CHANNEL.value:
            wallet_details = obj_wallets_service.create_and_register_wallet()
            receipient = order_data["receipient"]
            create_channel_transaction_data = obj_wallets_service.open_channel_by_third_party(order_id=order_id,
                sender=wallet_details["address"], sender_private_key=wallet_details["private_key"],
                group_id=order_data["group_id"], amount=amount, currency=currency, recipient=receipient)
            create_channel_transaction_data.update(wallet_details)
            return create_channel_transaction_data
        elif order_type == OrderType.CREATE_CHANNEL.value:
            pass
        elif order_type == OrderType.FUND_CHANNEL.value:
            fund_channel_transaction_data = obj_wallets_service.add_funds_to_channel(
                order_id=order_id, channel_id=order_data["channel_id"], amount=amount, currency=currency)
            return fund_channel_transaction_data
        else:
            raise Exception("Order type is not valid.")

    def get_receipient_address(self):
        return ""
