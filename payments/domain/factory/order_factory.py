import uuid

from payments.domain.order import Order
from payments.domain.order import PayPalOrder


def create_order_from_repository_object(persisted_order, payment_gateway):
    if payment_gateway == "paypal":
        # recreate order from persisted order
        return PayPalOrder()
    return Order()


def create_order(amount, payment_gateway):
    if payment_gateway == "paypal":
        order_id = uuid()
        return PayPalOrder()
    return Order()
