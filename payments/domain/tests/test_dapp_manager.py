import unittest
from datetime import datetime

from payments.application.dapp_order_manager import OrderManager
from payments.infrastructure.models import Order, Payment
from payments.infrastructure.order_repositroy import OrderRepository


class TestDappMananger(unittest.TestCase):

    repo = OrderRepository()
    dapp_order_manager = OrderManager()

    def test_create_order(self):
        response = self.dapp_order_manager.create_order(100, "USD", {"item": "item", "quantity": 2}, "user")
        assert "order_id" in response
        assert "item_details" in response
        if "price" in response:
            assert "amount" in response["price"]
            assert "currency" in response["price"]
        else:
            assert False

    def test_initiate_order(self):
        self.repo.add_item(
            Order(
                id="order_test_123",
                item_details={
                    "item": "test_item",
                    "quantity": 2
                },
                amount={
                    "amount": 100,
                    "currency": "USD"
                },
                created_at=datetime.strptime("2002-12-21 00:00:00", "%Y-%m-%d %H:%M:%S"),
                username="user",
            )
        )
        response = self.dapp_order_manager.initiate_payment_against_order("order_test_123", 100, "USD", "paypal")
        if "price" in response:
            assert "amount" in response["price"]
            assert "currency" in response["price"]
        else:
            assert False
        assert "payment_id" in response
        assert "payment" in response
        assert "order_id" in response

    def test_execute_order(self):
        pass

    def test_order_details(self):
        self.repo.add_item(
            Order(
                id="order_test_123",
                item_details={
                    "item": "test_item",
                    "quantity": 2
                },
                amount={
                    "amount": 100,
                    "currency": "USD"
                },
                created_at=datetime.strptime("2002-12-21 00:00:00", "%Y-%m-%d %H:%M:%S"),
                username="user",
            )
        )
        username = "user"
        status, order_details = self.dapp_order_manager.get_order_details_for_user(username)
        if status:
            assert "orders" in order_details

    def tearDown(self):
        self.repo.session.query(Payment.order_id == "order_test_123").delete()
        self.repo.session.query(Order.id == "order_test_123").delete()
        self.repo.session.commit()


if __name__ == "__main__":
    unittest.main()
