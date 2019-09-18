from enum import Enum

from payments.application.dapp_order_manager import DappOrderManager

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
        self.obj_transaction_history_dao = TransactionHistoryDAO(
            obj_repo=self.obj_repo)

    def initiate_order(self, user_data, payload_dict):
        """
            Initiate Order
                Step 1  Order Creation
                Step 2  Initiate Payment
                Step 3  Persist Transaction History
        """
        username = user_data["authorizer"]["claims"]["email"]
        amount = payload_dict["amount"]
        currency = payload_dict["currency"]
        order_type = payload_dict["order_type"]
        order_details = self.manage_create_order(
            username=username,
            item_details=payload_dict["item_details"],
            amount=amount,
            currency=currency,
        )
        order_id = order_details["order_id"]
        try:
            redirect_response = self.manage_initiate_payment(
                order_id=order_id,
                amount=amount,
                currency=currency,
                payment_method=payload_dict["payment_method"],
            )
            obj_transaction_history = TransactionHistory(
                username=username,
                order_id=order_id,
                type=order_type,
                payment_id=redirect_response["body"]["payment_id"],
                raw_payment_data=redirect_response["body"]["raw_payment_data"],
                status=Status.SUCCESS,
            )
            self.obj_transaction_history_dao.insert_transaction_history(
                obj_transaction_history=obj_transaction_history)
            return redirect_response
        except Exception as e:
            obj_transaction_history = TransactionHistory(
                username=username,
                order_id=order_id,
                type=order_type,
                status=Status.PAYMENT_INITIATION_FAILED,
            )
            self.obj_transaction_history_dao.insert_transaction_history(
                obj_transaction_history=obj_transaction_history)
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
        payment_id = payload_dict["payment_id"]
        payment_method = payload_dict["payment_method"]
        payment_details = payload_dict["payment_details"]
        status = Status.PAYMENT_EXECUTION_FAILED
        payment_executed = self.manage_execute_payment(
            order_id=order_id,
            payment_id=payment_id,
            payment_details=payment_details,
            payment_method=payment_method,
        )
        status = Status.PAYMENT_EXECUTED
        try:
            status = Status.ORDER_PROCESSING_FAILED
            data = self.manage_process_order(
                order_id=order_id,
                order_type=order_type,
                amount=payload_dict["amount"],
                currency=payload_dict["currency"],
            )
            status = Status.ORDER_PROCESSED
            obj_transaction_history = TransactionHistory(
                username=username,
                order_id=order_id,
                type=order_type,
                status=status,
                payment_id=payment_id,
                payment_method=payment_method,
                raw_payment_data=payment_details,
                transaction_hash=data["transaction_hash"],
            )
            self.obj_transaction_history_dao.insert_transaction_history(
                obj_transaction_history=obj_transaction_history)

        except Exception as e:
            obj_transaction_history = TransactionHistory(username=username,
                                                         order_id=order_id,
                                                         type=order_type,
                                                         status=status)
            self.obj_transaction_history_dao.insert_transaction_history(
                obj_transaction_history=obj_transaction_history)
            print(repr(e))
            raise e

    def manage_initiate_payment(self, username, order_id, amount, currency,
                                payment_method):
        obj_dapp_order_manager = DappOrderManager()
        initiate_payment_data = obj_dapp_order_manager.initiate_payment(
            order_id=order_id,
            amount=amount,
            currency=currency,
            payment_method=payment_method,
        )
        if initiate_payment_data["status"] == 301:
            return initiate_payment_data
        else:
            raise Exception("Error initiating payment for user %s", username)

    def manage_create_order(self, username, item_details, amount, currency):
        obj_dapp_order_manager = DappOrderManager()
        order_details = obj_dapp_order_manager.create_order(
            username=username,
            item_details=item_details,
            amount=amount,
            currency=currency,
        )
        if ["status"] == 200:
            return order_details["body"]
        else:
            raise Exception("Error creating order for user %s", username)

    def manage_execute_payment(self, username, order_id, payment_id,
                               payment_details, payment_method):
        obj_dapp_order_manager = DappOrderManager()  # make it global
        payment_executed = obj_dapp_order_manager.execute_payment_for_order(
            order_id=order_id,
            payment_id=payment_id,
            paid_payment_details=payment_details,
            payment_method=payment_method,
        )
        if payment_executed["status"] == 200:
            return payment_executed
        else:
            raise Exception(
                "Error executing payment for username %s aginst order_id %s",
                username,
                order_id,
            )

    def manage_process_order(self, order_id, order_type, amount, currency,
                             order_data):
        obj_wallets_service = WalletService(
            obj_repo=self.obj_repo)  # how to create object
        if order_type == OrderType.CREATE_WALLET_AND_CHANNEL:
            wallet_details = obj_wallets_service.create_and_register_wallet()
            receipient = self.get_receipient_address()
            create_channel_transaction_data = obj_wallets_service.open_channel_by_third_party(
                sender=wallet_details["address"],
                sender_private_key=wallet_details["private_key"],
                group_id=order_data["group_id"],
                amount=amount,
                currency=currency,
                recipient=receipient,
            )
            return create_channel_transaction_data
        elif order_type == OrderType.CREATE_CHANNEL:
            pass
        elif order_type == OrderType.FUND_CHANNEL:

            fund_channel_transaction_data = obj_wallets_service.add_funds_to_channel(
                order_id=order_id,
                channel_id=order_data["channel_id"],
                amount=amount,
                currency=currency,
            )
            return fund_channel_transaction_data
        else:
            raise Exception("Order type is not valid.")

    def get_receipient_address(self):
        return ""
