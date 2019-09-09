import uuid

from payments.domain.factory.order_factory import create_order_from_repository_object, create_order
from payments.domain.order import Order
from payments.domain.order_manager import OrderManager
from payments.infrastructure.order_repositroy import OrderRepository


class DappOrderMangaer(OrderManager):
    def __init__(self):
        self.order_repository = OrderRepository()

    def initiate_order_and_payment(self, amount, payment_gateway, payment_details):
        order = create_order(amount, payment_gateway)
        self.create_payment(order, payment_details)
        self.order_repository.persist_order(order)

    def create_order(self, amount, payment_gateway):
        order = create_order(amount, payment_gateway)
        return order

    def create_payment(self, order, payment_details):
        order.add_payment(payment_details)

    def execute_payment_for_order(self, order_id, payment_id):
        order = create_order_from_repository_object(self.order_repository.get_order_by_order_id(order_id))
        order.execute_payment(payment_id)
        self.order_repository.update_order(order)
