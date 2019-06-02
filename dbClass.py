import psycopg2


class dbParam:
    def __init__(self, dbName, dbUser, password, host):
        self.dbName = dbName
        self.dbUser = dbUser
        self.password = password
        self.host = host

    def getConn(self):
        conn = psycopg2.connect(dbname=self.dbName,
                                user=self.dbUser,
                                password=self.password,
                                host=self.host)
        conn.autocommit = True
        return conn
