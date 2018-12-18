import pymysql
import os

DB_HOST=os.environ['DB_HOST']
DB_USER=os.environ['DB_USER']
DB_PASSWORD=os.environ['DB_PASSWORD']
DB_NAME=os.environ['DB_NAME']
DB_PORT=int(os.environ['DB_PORT'])

class Repository:
    connection = None

    def __init__(self):
        self.connection = self.__get_connection()

    def execute(self, query, params=None):
        return self.__execute_query(query, params)

    def __get_connection(self):
        open = True
        if self.connection is not None:
            try:
                self.execute("select 1")
                open = False
            except Exception as e:
                open = True

        if open:
            self.connection = pymysql.connect(DB_HOST, user=DB_USER,
                                              passwd=DB_PASSWORD, db=DB_NAME, port=DB_PORT)
        return self.connection

    def __execute_query(self, query, params=None):
        result = None
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params)
                db_rows = cursor.fetchall()
                if cursor.description is not None:
                    field_name = [field[0] for field in cursor.description]
                    self.connection.commit()

                    result = list()
                    for values in db_rows:
                        row = dict(zip(field_name, values))
                        result.append(row)
                self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            print("DB Error in %s, error: %s" % (str(query), repr(e)))
        return result

    def bulk_query(self, query, params=None):
        try:
            with self.connection.cursor() as cursor:
                result = cursor.executemany(query, params)
                self.connection.commit()
                return result
        except Exception as err:
            self.connection.rollback()
            print("DB Error in %s, error: %s" % (str(query), repr(err)))
