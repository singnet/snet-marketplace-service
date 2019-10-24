class Repository(object):



    def __init__(self,connection):
        self.coonection= connection

    def begin_transaction(self):
        self.connection.begin_transaction()

    def commit_transaction(self):
        self.connection.commit_transaction()

    def rollback_transaction(self):
        self.connection.rollback_transaction()
