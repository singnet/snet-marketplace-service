import os
from contextlib import contextmanager

from common.exceptions import BadRequestException
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
    f"{NETWORKS[NETWORK_ID]['db']['DB_PORT']}/{NETWORKS[NETWORK_ID]['db']['DB_NAME']}",
    echo=os.environ.get("LOG_LEVEL", "INFO") == "DEBUG",
)

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
    except BadRequestException as e:
        logger.exception("Bad request error during session scope")
        session.rollback()
        raise e
    except Exception:
        logger.exception("Unexpected error during session scope", exc_info=True)
        session.rollback()
        raise
    finally:
        session.close()
