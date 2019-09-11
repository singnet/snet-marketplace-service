import uuid

from payments.domain.factory.order_factory import create_order_from_repository_order, create_order
from payments.domain.order_manager import OrderManager
from payments.infrastructure.order_repositroy import OrderRepository


class DappOrderMangaer(OrderManager):
    def __init__(self):
        self.order_repository = OrderRepository()

    def create_order(self, amount, agi, username):
        item_details = {
            "item": 'AGI',
            "quantity": agi
        }
        order = create_order(amount, item_details, username)
        self.order_repository.persist_order(order)
        return order

    def initiate_payment(self, order_id, amount, payment_method):
        order = create_order_from_repository_order(self.order_repository.get_order_by_order_id(order_id))
        order.create_payment(amount, payment_method)

    def execute_payment_for_order(self, order_id, payment_id, payer_id, payment_gateway):
        order = create_order_from_repository_order(self.order_repository.get_order_by_order_id(order_id))
        order.execute_payment(payment_id)
        self.order_repository.update_order(order)


if __name__ == "__main__":
    dappmanager = DappOrderMangaer()
    # dappmanager.create_order(100.5, 2, "user")
    dappmanager.initiate_payment("1", 100.5, "paypal")
