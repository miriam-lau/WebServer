import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Tuple, List, Dict, Optional


# Note that the 'values' tuple must be a list so for single items, it must still contain a trailing comma
# e.g. (username,)
class Database:
    HOST = "localhost"
    DATABASE = "webserver"
    USER = "webserver"
    PASSWORD = "password"

    def __init__(self):
        self.conn = psycopg2.connect(
            host=Database.HOST, database=Database.DATABASE, user=Database.USER, password=Database.PASSWORD)

    def get_cursor(self):
        return self.conn.cursor(cursor_factory=RealDictCursor)

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()
