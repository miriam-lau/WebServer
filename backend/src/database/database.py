import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Tuple, List


class Database:
    HOST = "localhost"
    DATABASE = "james"
    USER = "james"
    PASSWORD = "password"

    def __init__(self):
        self.conn = psycopg2.connect(
            host=Database.HOST, database=Database.DATABASE, user=Database.USER, password=Database.PASSWORD)

    def execute_query(self, sql, values) -> List:
        cur = self.conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(sql, values)
        return cur.fetchall()

    def execute_commit(self, sql, values):
        cur = self.conn.cursor()
        cur.execute(sql, values)
        self.conn.commit()
        cur.close()

    def execute_commit_with_return(self, sql, values) -> Tuple:
        cur = self.conn.cursor()
        cur.execute(sql, values)
        ret = cur.fetchone()
        self.conn.commit()
        cur.close()
        return ret
