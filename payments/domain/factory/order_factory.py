import uuid

from payments.domain.order import Order
from payments.domain.payment import Payment


def create_order_from_repository_order(order_payments):
    order_model = order_payments[0]
    payment_models = order_payments[1]
    payments = []
    for payment_info in payment_models:
        payment = Payment(
            payment_id=payment_info.payment_id,
            amount=payment_info.amount,
            created_at=payment_info.created_at,
            payment_status=payment_info.payment_status,
            payment_details=payment_info.payment_details
        )
        payments.append(payment)
    order = Order(
        order_id=order_model.id,
        amount=order_model.amount,
        item_details=order_model.item_details,
        username=order_model.username,
        payments=payments
    )
    return order


def create_order(amount, item_details, username):
    order_id = str(uuid.uuid1())
    order = Order(order_id=order_id, amount=amount, item_details=item_details, username=username)
    return order
