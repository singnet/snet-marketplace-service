from functools import wraps
from typing import Callable, Any, TypeVar, List
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from common.logger import get_logger
from registry.config import DB_DETAILS

driver = DB_DETAILS["driver"]
user = DB_DETAILS["user"]
password = DB_DETAILS["password"]
host = DB_DETAILS["host"]
port = DB_DETAILS["port"]
db_name = DB_DETAILS["name"]

connection_string = f"{driver}://{user}:{password}@{host}:{port}/{db_name}"
engine = create_engine(connection_string, pool_pre_ping=True, echo=True)

Session = sessionmaker(bind=engine)
default_session = Session()
logger = get_logger("sqlalchemy.engine").setLevel("INFO")
get_logger("sqlalchemy.pool").setLevel("DEBUG")

T = TypeVar("T")

class BaseRepository:

    def __init__(self):
        self.session = default_session

    @staticmethod
    def write_ops(method: Callable) -> Callable:
        @wraps(method)
        def wrapper(self, *args, **kwargs) -> Callable[..., Any]:
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

    @write_ops
    def add_item(self, item: T):
        self.session.add(item)
        self.session.commit()

    @write_ops
    def add_all_items(self, items: List[T]):
        self.session.add_all(items)
        self.session.commit()
