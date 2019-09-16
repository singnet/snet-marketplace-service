from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from payments.domain.order_service import ObtainOrders, PersistOrders

engine = create_engine("DB_URL", echo=True)
Session = sessionmaker(bind=engine)
default_session = Session()


class OrderRepository(ObtainOrders, PersistOrders):
    def get_default_session(self, session=None):
        if not session:
            return default_session

        return session

    def get_order_by_order_id(self):
        pass

    def create_payment(self, order):
        pass

    def update_payment(self, payment):
        pass
