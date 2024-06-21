from functools import wraps
from common.logger import get_logger
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

from contract_api.config import NETWORKS, NETWORK_ID

engine = create_engine(
    f"{NETWORKS[NETWORK_ID]['db']['DB_DRIVER']}://{NETWORKS[NETWORK_ID]['db']['DB_USER']}:"
    f"{NETWORKS[NETWORK_ID]['db']['DB_PASSWORD']}"
    f"@{NETWORKS[NETWORK_ID]['db']['DB_HOST']}:"
    f"{NETWORKS[NETWORK_ID]['db']['DB_PORT']}/{NETWORKS[NETWORK_ID]['db']['DB_NAME']}", echo=False)
logger = get_logger(__name__)
Session = sessionmaker(bind=engine)
default_session = Session()


class BaseRepository:

    def __init__(self):
        self.session = default_session

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
            self.session.commit()
            raise e

    @staticmethod
    def write_ops(method):
        @wraps(method)
        def wrapper(self, *args, **kwargs):
            try:
                return method(self, *args, **kwargs)
            except SQLAlchemyError as e:
                logger.exception("Database error on write operations", exc_info=True)
                self.session.rollback()
                raise e
            except Exception as e:
                self.session.rollback()
                raise e
        return wrapper
