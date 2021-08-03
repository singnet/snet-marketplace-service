import pymysql


class Repository:
    connection = None

    def __init__(self, NETWORKS, NETWORK_ID):
        self.DB_HOST = NETWORKS[NETWORK_ID]['db']['DB_HOST']
        self.DB_USER = NETWORKS[NETWORK_ID]['db']['DB_USER']
        self.DB_PASSWORD = NETWORKS[NETWORK_ID]['db']['DB_PASSWORD']
        self.DB_NAME = NETWORKS[NETWORK_ID]['db']['DB_NAME']
        self.DB_PORT = 3306
        self.connection = self.__get_connection()
        self.auto_commit = True

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
            self.connection = pymysql.connect(self.DB_HOST, user=self.DB_USER,
                                              passwd=self.DB_PASSWORD, db=self.DB_NAME, port=self.DB_PORT)
        return self.connection

    def __execute_query(self, query, params=None):
        result = list()
        try:
            with self.connection.cursor() as cursor:
                qry_resp = cursor.execute(query, params)
                db_rows = cursor.fetchall()
                if cursor.description is not None:
                    field_name = [field[0] for field in cursor.description]
                    for values in db_rows:
                        row = dict(zip(field_name, values))
                        result.append(row)
                else:
                    result.append(qry_resp)
                    result.append({'last_row_id': cursor.lastrowid})
                if self.auto_commit:
                    self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            print("DB Error in %s, error: %s" % (str(query), repr(e)))
            raise e
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

    def begin_transaction(self):
        self.connection.begin()

    def commit_transaction(self):
        self.connection.commit()

    def rollback_transaction(self):
        self.connection.rollback()
