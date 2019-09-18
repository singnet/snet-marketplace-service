import unittest
from datetime import datetime

from payments.application.dapp_order_manager import OrderManager
from payments.infrastructure.models import Order
from payments.infrastructure.order_repositroy import OrderRepository


class TestDappMananger(unittest.TestCase):

    repo = OrderRepository()
    dapp_order_manager = OrderManager()

    def test_create_order(self):
        response = self.dapp_order_manager.create_order(100, "USD", {"item": "item", "quantity": 2}, "user")
        assert "body" in response
        assert "headers" in response
        assert "statusCode" in response
        assert "order_id" in response["body"]
        assert "item_details" in response["body"]
        assert "amount" in response["body"]
        assert "currency" in response["body"]
        order_id = response["body"]["order_id"]
        print(response)
        self.repo.session.query(Order.id == order_id).delete()

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
        assert "body" in response
        assert "headers" in response
        assert "statusCode" in response
        assert "amount" in response["body"]
        assert "currency" in response["body"]
        assert "payment_id" in response["body"]
        assert "payment" in response["body"]
        assert "order_id" in response["body"]

    def test_execute_order(self):
        pass

    def test_order_details(self):
        username = "123"
        order_details = self.dapp_order_manager.get_order_details_for_user(username)
        assert "body" in order_details
        assert "headers" in order_details
        assert "statusCode" in order_details
        if order_details["statusCode"] == "success":
            assert "orders" in order_details["body"]


if __name__ == "__main__":
    unittest.main()
