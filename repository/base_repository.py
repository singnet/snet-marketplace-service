import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from common.constant import NETWORKS

net_id= int(os.environ.get('NETWORK_ID', '3'))
engine = create_engine('mysql+pymysql://'+NETWORKS[net_id]['db']['DB_USER']+':'+NETWORKS[net_id]['db']['DB_PASSWORD']+'@'+NETWORKS[net_id]['db']['DB_HOST']+'/'+NETWORKS[net_id]['db']['DB_NAME'], echo=True)

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

