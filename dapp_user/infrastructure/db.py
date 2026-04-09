from contextlib import contextmanager

from common.logger import get_logger
from dapp_user.settings import settings
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

logger = get_logger(__name__)

connection_string = (
    f"{settings.db.driver}://{settings.db.user}:{settings.db.password}"
    f"@{settings.db.host}:{settings.db.port}/{settings.db.name}"
)
engine = create_engine(connection_string, pool_pre_ping=True, echo=False)

DefaultSessionFactory = sessionmaker(bind=engine)


@contextmanager
def session_scope(session_factory):
    session = session_factory()
    try:
        yield session
        session.commit()
    except SQLAlchemyError:
        logger.exception("Database error during session scope", exc_info=True)
        session.rollback()
        raise
    except Exception:
        logger.exception("Unexpected error during session scope", exc_info=True)
        session.rollback()
        raise
    finally:
        session.close()
