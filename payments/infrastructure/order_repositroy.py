from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from payments.infrastructure.models import Order, Payment
from payments.settings import DB_URL

engine = create_engine(DB_URL, echo=False)
Session = sessionmaker(bind=engine)


class OrderRepository:

    def __init__(self):
        self.session = Session()

    def persist_order(self, order):
        order_model = Order(
            id=order.get_order_id(),
            username=order.get_username(),
            amount=order.get_amount(),
            item_details=order.get_item_details(),
            created_at=datetime.now()
        )
        self.add_model(order_model)

    def add_model(self, item):
        try:
            self.session.add(item)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e

        self.session.commit()

    def add_all_model(self, items):
        try:
            self.session.add_all(items)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e

    def get_order_by_order_id(self, order_id):
        order = self.session.query(Order).filter(Order.id == order_id).first()
        payments = self.get_payments_by_order_id(order_id)
        return order, payments

    def get_payments_by_order_id(self, order_id):
        payments = self.session.query(Payment).filter(Payment.order_id == order_id).all()
        return payments

    def persist_payment(self, order_id, payment):
        payment_model = Payment(
            payment_id=payment.get_payment_id(),
            amount=payment.get_amount(),
            created_at=payment.get_created_at(),
            payment_details=payment.get_payment_details(),
            payment_status=payment.get_payment_status(),
            order_id=order_id
        )
        self.add_model(payment_model)

    def update_payment_status(self, payment):
        try:
            payment_model = self.session.query(Payment).filter(Payment.payment_id == payment.get_payment_id()).first()
            payment_model.payment_status = payment.get_payment_status()
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e
