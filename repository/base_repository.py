from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('mysql+pymysql://root:test@localhost/marketplace', echo=True)

Session = sessionmaker(bind=engine)
default_session = Session()

class BaseRepository(object):



    def get_default_session(self,session=None):
        if not session:
         return default_session

        return session;

    def add_item(self,item,session=None):
        session=self.get_default_session(session)
        session.add(item)
        return item;



    def remove_item(self,item,session=None):
        pass

    def update_item(self,item,session=None):
        pass

