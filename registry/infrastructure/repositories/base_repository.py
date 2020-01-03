from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from registry.config import NETWORKS, NETWORK_ID

engine = create_engine(f"mysql+pymysql://{NETWORKS[NETWORK_ID]['db']['DB_USER']}:"
                       f"{NETWORKS[NETWORK_ID]['db']['DB_PASSWORD']}"
                       f"@{NETWORKS[NETWORK_ID]['db']['DB_HOST']}:"
                       f"{NETWORKS[NETWORK_ID]['db']['DB_PORT']}/{NETWORKS[NETWORK_ID]['db']['DB_NAME']}", echo=False)
Session = sessionmaker(bind=engine)


class BaseRepository:

    def __init__(self):
        self.session = Session()

    def add_item(self, item):
        try:
            self.session.add(item)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e

        self.session.commit()

    def add_all_items(self, items):
        try:
            self.session.add_all(items)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e
