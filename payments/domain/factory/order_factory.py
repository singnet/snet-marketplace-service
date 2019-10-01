import uuid

from common.logger import get_logger
from payments.domain.order import Order
from payments.domain.payment import Payment
from payments.domain.paypal_payment import PaypalPayment

logger = get_logger(__name__)


class OrderFactory:
    @staticmethod
    def create_order_from_repository_order(order):
        payments = []
        for payment_info in order.payments:
            if ("payment_method" in payment_info.payment_details) and \
                    (payment_info.payment_details["payment_method"] == "paypal"):
                payment = PaypalPayment(
                    payment_id=payment_info.payment_id,
                    amount=payment_info.amount["amount"],
                    currency=payment_info.amount["currency"],
                    created_at=payment_info.created_at,
                    payment_status=payment_info.payment_status,
                    payment_details=payment_info.payment_details
                )
            else:
                payment = Payment(
                    payment_id=payment_info.payment_id,
                    amount=payment_info.amount["amount"],
                    currency=payment_info.amount["currency"],
                    created_at=payment_info.created_at,
                    payment_status=payment_info.payment_status,
                    payment_details=payment_info.payment_details
                )
            payments.append(payment)
        order = Order(
            order_id=order.id,
            amount=order.amount["amount"],
            currency=order.amount["currency"],
            item_details=order.item_details,
            username=order.username,
            payments=payments
        )
        return order

    @staticmethod
    def create_order(amount, currency, item_details, username):
        order_id = str(uuid.uuid1())
        order = Order(order_id=order_id, amount=amount, currency=currency,
                      item_details=item_details, username=username, payments=[])
        logger.info(f"Order created with {order_id}")
        return order

    @staticmethod
    def get_order_details(orders):
        order_details = []
        for order_item in orders:
            order = OrderFactory.create_order_details_from_repository(order_item)
            order_details.append(order)
        return {"orders": order_details}

    @staticmethod
    def create_order_details_from_repository(order_item):
        order = {
            "order_id": order_item.id,
            "price": {
                "amount": order_item.amount["amount"],
                "currency": order_item.amount["currency"]
            },
            "username": order_item.username,
            "created_at": order_item.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "item_details": order_item.item_details,
            "payments": []
        }
        for payment_item in order_item.payments:
            payment = {
                "payment_id": payment_item.payment_id,
                "price": {
                    "amount": payment_item.amount["amount"],
                    "currency": payment_item.amount["currency"]
                },
                "payment_details": payment_item.payment_details,
                "payment_status": payment_item.payment_status,
                "created_at": payment_item.created_at.strftime("%Y-%m-%d %H:%M:%S")
            }
            order["payments"].append(payment)
        return order
