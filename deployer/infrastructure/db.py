from functools import wraps
from typing import Callable

from common.logger import get_logger
from deployer.config import NETWORKS, NETWORK_ID
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

logger = get_logger(__name__)

engine = create_engine(
    f"{NETWORKS[NETWORK_ID]['db']['DB_DRIVER']}://{NETWORKS[NETWORK_ID]['db']['DB_USER']}:"
    f"{NETWORKS[NETWORK_ID]['db']['DB_PASSWORD']}"
    f"@{NETWORKS[NETWORK_ID]['db']['DB_HOST']}:"
    f"{NETWORKS[NETWORK_ID]['db']['DB_PORT']}/{NETWORKS[NETWORK_ID]['db']['DB_NAME']}", echo=True)

DefaultSessionFactory = sessionmaker(bind=engine)


class BaseRepository:
    def __init__(self):
        self.session = None


def in_session(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        session = DefaultSessionFactory()
        try:
            for _, attr_value in self.__dict__.items():
                if isinstance(attr_value, BaseRepository):
                    attr_value.session = session
            result = func(self, *args, **kwargs)
            session.commit()
            return result
        except SQLAlchemyError:
            logger.exception("Database error during session scope", exc_info=True)
            session.rollback()
            raise
        except Exception:
            logger.exception("Unexpected error during session scope", exc_info=True)
            session.rollback()
            raise
        finally:
            for _, attr_value in self.__dict__.items():
                if isinstance(attr_value, BaseRepository):
                    attr_value.session = None
            session.close()
    return wrapper