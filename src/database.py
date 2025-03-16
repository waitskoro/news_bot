import psycopg2

class Database:
    def __init__(self):
        self.__conn = psycopg2.connect(dbname="postgres",
                                       user="postgres",
                                       password="1111",
                                       host="127.0.0.1")
        self.__cursor = self.__conn.cursor()