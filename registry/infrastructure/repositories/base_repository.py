from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from payments.config import DB_URL

engine = create_engine(DB_URL, echo=False)
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
