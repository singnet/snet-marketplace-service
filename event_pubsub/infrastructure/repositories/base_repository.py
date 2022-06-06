from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from event_pubsub.config import DB_DETAILS

driver = DB_DETAILS["driver"]
user = DB_DETAILS["user"]
password = DB_DETAILS["password"]
host = DB_DETAILS["host"]
port = DB_DETAILS["port"]
db_name = DB_DETAILS["name"]

connection_string = f"{driver}://{user}:{password}@{host}:{port}/{db_name}"
engine = create_engine(connection_string, pool_pre_ping=True)

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
            self.session.rollback()
            raise e
