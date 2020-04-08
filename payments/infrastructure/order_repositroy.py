from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from payments.config import DB_URL
from payments.infrastructure.models import Order, Payment

engine = create_engine(DB_URL, echo=False)
Session = sessionmaker(bind=engine)


class OrderRepository:

    def __init__(self):
        self.session = Session()

    def persist_order(self, order):
        order_model = Order(
            id=order.get_order_id(),
            username=order.get_username(),
            amount={
                "amount": order.get_amount(),
                "currency": order.get_currency()
            },
            item_details=order.get_item_details(),
            created_at=datetime.utcnow()
        )
        self.add_item(order_model)

    def add_item(self, item):
        try:
            self.session.add(item)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e

    def add_all_items(self, items):
        try:
            self.session.add_all(items)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e

    def get_order_by_order_id(self, order_id):
        order = self.session.query(Order).filter(Order.id == order_id).first()
        if order is None:
            raise Exception(f"No order found with id: {order_id}")
        return order

    def persist_payment(self, order, payment_id):
        payment = order.get_payment(payment_id)
        if payment is None:
            raise Exception(f"Payment not found in order instance for the {payment_id}")

        payment_model = Payment(
            payment_id=payment.get_payment_id(),
            amount={
                "amount": payment.get_amount(),
                "currency": payment.get_currency()
            },
            created_at=payment.get_created_at(),
            payment_details=payment.get_payment_details(),
            payment_status=payment.get_payment_status(),
            order_id=order.get_order_id()
        )
        self.add_item(payment_model)

    def update_payment_status(self, order, payment_id):
        payment = order.get_payment(payment_id)
        if payment is None:
            raise Exception(f"Payment not found in order instance for the {payment_id}")
        try:
            order_item = self.session.query(Order).filter(Order.id == order.get_order_id()).first()
            for payment_model in order_item.payments:
                if payment_model.payment_id == payment.get_payment_id():
                    payment_model.payment_status = payment.get_payment_status()
                    break
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e

    def get_order_by_username(self, username):
        orders = self.session.query(Order).filter(Order.username == username).all()
        return orders
