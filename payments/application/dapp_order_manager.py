from common.logger import get_logger
from payments.domain.factory.order_factory import create_order_from_repository_order, create_order, get_order_details
from payments.infrastructure.order_repositroy import OrderRepository

logger = get_logger(__name__)


class OrderManager:
    def __init__(self):
        self.order_repository = OrderRepository()

    def create_order(self, amount, currency, item_details, username):
        try:
            order = create_order(amount, currency, item_details, username)
            self.order_repository.persist_order(order)
            response = {
                "order_id": order.get_order_id(),
                "item_details": order.get_item_details(),
                "amount": order.get_amount(),
                "currency": order.get_currency()
            }
            status = True
        except Exception as e:
            response = "Failed to create order"
            status = False
            logger.error(f"Failed to create order for,\n"
                         f"amount: {amount} {currency}\n"
                         f"item_details: {item_details}\n"
                         f"username: {username}")
            logger.error(e)
        return status, response

    def initiate_payment_against_order(self, order_id, amount, currency, payment_method):
        try:
            order = create_order_from_repository_order(self.order_repository.get_order_by_order_id(order_id))
            payment_details = order.create_payment(amount, currency, payment_method)
            payment = payment_details["payment_object"]
            self.order_repository.persist_payment(order, payment.get_payment_id())
            response = {
                "amount": payment.get_amount(),
                "currency": payment.get_currency(),
                "payment_id": payment.get_payment_id(),
                "payment": payment_details["payment"],
                "order_id": order.get_order_id()
            }
            response["payment"]["payment_method"] = payment_method
            status = True
        except Exception as e:
            response = "Failed to initiate payment"
            status = False
            logger.error(f"Failed to initiate payment for,\n"
                         f"order_id: {order_id}\n"
                         f"amount: {amount} {currency}\n"
                         f"payment_method: {payment_method}")
            logger.error(e)
        return status, response

    def execute_payment_against_order(self, order_id, payment_id, payment_details, payment_method):
        try:
            order = create_order_from_repository_order(self.order_repository.get_order_by_order_id(order_id))
            payment = order.execute_payment(payment_id, payment_details, payment_method)
            OrderRepository().update_payment_status(order, payment.get_payment_id())
            response = {
                "payment_id": payment.get_payment_id(),
                "payment": payment.get_payment_details(),
                "order_id": order.get_order_id()
            }
            status = True
        except Exception as e:
            response = "Failed to execute payment"
            status = False
            logger.error(e)
            logger.error(f"Failed to execute payment for,\n"
                         f"order_id: {order_id}\n"
                         f"payment_id: {payment_id}\n"
                         f"paid_payment_details: {payment_details}\n"
                         f"payment_method: {payment_method}")
        return status, response

    def get_order_details_for_user(self, username):
        try:
            orders = self.order_repository.get_order_by_username(username)
            response = get_order_details(orders)
            status = True
        except Exception as e:
            response = "Failed to get orders"
            status = False
            logger.error(e)
            logger.error(f"Failed to get order details for, username: {username}")
        return status, response

    def cancel_payment_against_order(self, order_id, payment_id):
        try:
            order = create_order_from_repository_order(self.order_repository.get_order_by_order_id(order_id))
            order.cancel_payment(payment_id)
            self.order_repository.update_payment_status(order, payment_id)
            response = "Success"
            status = True
        except Exception as e:
            response = "Failed to set payment failed"
            status = False
            logger.error(e)
            logger.error(f"Failed to set payment failed for payment_id: {payment_id}")
        return status, response
