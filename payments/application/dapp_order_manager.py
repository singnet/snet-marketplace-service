from common.constant import STATUS_CODE_SUCCESS, STATUS_CODE_FAILED, STATUS_CODE_REDIRECT
from common.utils import make_response
from common.logger import get_logger
from payments.domain.factory.order_factory import create_order_from_repository_order, create_order, get_order_details
from payments.infrastructure.order_repositroy import OrderRepository

logger = get_logger(__name__)


class DappOrderMangaer:
    def __init__(self):
        self.order_repository = OrderRepository()

    def create_order(self, amount, currency, item_details, username):
        try:
            order = create_order(amount, currency, item_details, username)
            self.order_repository.persist_order(order)
            response_body = {
                "order_id": order.get_order_id(),
                "item_details": order.get_item_details(),
                "amount": order.get_amount(),
                "currency": order.get_currency()
            }
            response_status = STATUS_CODE_SUCCESS
        except Exception as e:
            response_body = "Failed to create order"
            response_status = STATUS_CODE_FAILED
            logger.error(f"Failed to create order for,\n"
                         f"amount: {amount} {currency}\n"
                         f"item_details: {item_details}\n"
                         f"username: {username}")
            logger.error(e)
        return make_response(response_status, response_body)

    def initiate_payment_against_order(self, order_id, amount, currency, payment_method):
        try:
            order = create_order_from_repository_order(
                self.order_repository.get_order_by_order_id(order_id))
            payment_details = order.create_payment(
                amount, currency, payment_method)
            payment = payment_details["payment_object"]
            self.order_repository.persist_payment(
                order, payment.get_payment_id())
            response_body = {
                "amount": payment.get_amount(),
                "currency": payment.get_currency(),
                "payment_id": payment.get_payment_id(),
                "payment": payment_details["payment"],
                "order_id": order.get_order_id()
            }
            response_body["payment"]["payment_method"] = payment_method
            response_status = STATUS_CODE_REDIRECT
        except Exception as e:
            response_body = "Failed to initiate payment"
            response_status = STATUS_CODE_FAILED
            logger.error(f"Failed to initiate payment for,\n"
                         f"order_id: {order_id}\n"
                         f"amount: {amount} {currency}\n"
                         f"payment_method: {payment_method}")
            logger.error(e)
        return make_response(response_status, response_body)

    def execute_payment_against_order(self, order_id, payment_id, paid_payment_details, payment_method):
        try:
            order = create_order_from_repository_order(
                self.order_repository.get_order_by_order_id(order_id))
            payment = order.execute_payment(
                payment_id, paid_payment_details, payment_method)
            OrderRepository().update_payment_status(order, payment.get_payment_id())
            response_body = {
                "payment_id": payment.get_payment_id(),
                "payment": payment.get_payment_details(),
                "order_id": order.get_order_id()
            }
            response_status = STATUS_CODE_SUCCESS
        except Exception as e:
            response_body = "Failed to execute payment"
            response_status = STATUS_CODE_FAILED
            logger.error(e)
            logger.error(f"Failed to execute payment for,\n"
                         f"order_id: {order_id}\n"
                         f"payment_id: {payment_id}\n"
                         f"paid_payment_details: {paid_payment_details}\n"
                         f"payment_method: {payment_method}")
        return make_response(response_status, response_body)

    def get_order_details_for_user(self, username):
        try:
            orders = self.order_repository.get_order_by_username(username)
            response_body = get_order_details(orders)
            response_status = STATUS_CODE_SUCCESS
        except Exception as e:
            response_body = "Failed to get orders"
            response_status = STATUS_CODE_FAILED
            logger.error(e)
            logger.error(
                f"Failed to get order details for, username: {username}\n")
        return make_response(response_status, response_body)
