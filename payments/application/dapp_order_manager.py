import uuid

from payments.domain.factory.order_factory import create_order_from_repository_order, create_order
from payments.infrastructure.order_repositroy import OrderRepository


def make_response(response_status, response_body):
    return {
        "status": response_status,
        "body": response_body
    }


class DappOrderMangaer:
    def __init__(self):
        self.order_repository = OrderRepository()

    def create_order(self, amount, item_details, username):
        try:
            order = create_order(amount, item_details, username)
            self.order_repository.persist_order(order)
            response_body = {
                "order_id": order.get_order_id(),
                "item_details": order.get_item_details()
            }
            response_status = "success"
        except Exception as e:
            response_body = "Failed to create order"
            response_status = "failed"
            print(e)
        return make_response(response_status, response_body)

    def initiate_payment(self, order_id, amount, payment_method):
        try:
            order = create_order_from_repository_order(self.order_repository.get_order_by_order_id(order_id))
            payment_details = order.create_payment(payment_method)
            payment = payment_details["payment_object"]
            self.order_repository.persist_payment(order_id, payment)
            response_body = {
                "amount": payment.get_amount(),
                "payment_id": payment.get_payment_id(),
                "payment": payment_details["payment"],
                "order_id": order.get_order_id()
            }
            response_body["payment"]["payment_method"] = payment_method
            response_status = "success"
        except Exception as e:
            response_body = "Failed to initiate payment"
            response_status = "failed"
            print(e)
        return make_response(response_status, response_body)

    def execute_payment_for_order(self, order_id, payment_id, paid_payment_details, payment_method):
        try:
            order = create_order_from_repository_order(self.order_repository.get_order_by_order_id(order_id))
            payment = order.execute_payment(payment_id, paid_payment_details, payment_method)
            OrderRepository().update_payment_status(payment)
            response_body = {
                "payment_id": payment.get_payment_id(),
                "payment": payment.get_payment_details(),
                "order_id": order.get_order_id()
            }
            response_status = "success"
        except Exception as e:
            response_body = "Failed to execute payment"
            response_status = "failed"
            print(e)
        return make_response(response_status, response_body)
