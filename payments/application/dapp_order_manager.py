from common.logger import get_logger
from payments.domain.factory.order_factory import OrderFactory
from payments.infrastructure.order_repositroy import OrderRepository

logger = get_logger(__name__)


class OrderManager:
    def __init__(self):
        self.order_repository = OrderRepository()

    def create_order(self, amount, currency, item_details, username):
        order = OrderFactory.create_order(amount, currency, item_details, username)

        self.order_repository.persist_order(order)
        logger.info(f"Order({order.get_order_id()}) created and persisted into database")

        response = {
            "order_id": order.get_order_id(),
            "item_details": order.get_item_details(),
            "price": {
                "amount": order.get_amount(),
                "currency": order.get_currency()
            }
        }
        return response

    def initiate_payment_against_order(self, order_id, amount, currency, payment_method):
        order = OrderFactory.create_order_from_repository_order(self.order_repository.get_order_by_order_id(order_id))

        payment_details = order.create_payment(amount, currency, payment_method)
        payment = payment_details["payment_object"]
        logger.info(f"Payment {payment.get_payment_id()} created against order {order.get_order_id()}")

        self.order_repository.persist_payment(order, payment.get_payment_id())
        logger.info(f"Payment persisted into the database")

        response = {
            "price": {
                "amount": payment.get_amount(),
                "currency": payment.get_currency()
            },
            "payment_id": payment.get_payment_id(),
            "payment": payment_details["payment"],
            "order_id": order.get_order_id()
        }
        response["payment"]["payment_method"] = payment_method

        return response

    def execute_payment_against_order(self, order_id, payment_id, payment_details, payment_method):
        order = OrderFactory.create_order_from_repository_order(self.order_repository.get_order_by_order_id(order_id))

        payment = order.execute_payment(payment_id, payment_details, payment_method)
        logger.info("Payment execution is complete")

        OrderRepository().update_payment_status(order, payment.get_payment_id())
        logger.info("Payment status updated in the database")

        response = {
            "payment_id": payment.get_payment_id(),
            "payment": payment.get_payment_details(),
            "order_id": order.get_order_id()
        }

        return response

    def get_order_details_for_user(self, username):
        orders = self.order_repository.get_order_by_username(username)
        logger.info(f"Fetched {len(orders)} orders from the database")

        response = OrderFactory.get_order_details(orders)
        logger.info(f"Order details created from factory")

        return response

    def cancel_payment_against_order(self, order_id, payment_id):
        order = OrderFactory.create_order_from_repository_order(self.order_repository.get_order_by_order_id(order_id))

        order.cancel_payment(payment_id)
        self.order_repository.update_payment_status(order, payment_id)

        response = "Success"
        return response

    def get_order_from_order_id(self, order_id):
        response = OrderFactory.create_order_details_from_repository(self.order_repository.get_order_by_order_id(order_id))
        return response
