from functools import wraps

from common.logger import get_logger
from dapp_user.settings import settings
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session as SessionType
from sqlalchemy.orm import sessionmaker

logger = get_logger(__name__)

connection_string = (
    f"{settings.db.driver}://{settings.db.user}:{settings.db.password}"
    f"@{settings.db.host}:{settings.db.port}/{settings.db.name}"
)
engine = create_engine(connection_string, pool_pre_ping=True, echo=False)

Session = sessionmaker(bind=engine)
default_session = Session()


class BaseRepository:
    def __init__(self, session: SessionType | None = None):
        if session is not None:
            self.session = session
        else:
            self.session = default_session

    def __del__(self):
        self.session.close()

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
