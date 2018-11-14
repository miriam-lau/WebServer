import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Tuple, List, Dict, Optional


# Note that the 'values' tuple must be a list so for single items, it must still contain a trailing comma
# e.g. (username,)
class Database:
    HOST = "localhost"
    DATABASE = "james"
    USER = "james"
    PASSWORD = "password"

    def __init__(self):
        self.conn = psycopg2.connect(
            host=Database.HOST, database=Database.DATABASE, user=Database.USER, password=Database.PASSWORD)

    # Used for select statements.
    # Note that tuple must be a list so for single items, it must still contain a trailing comma
    # e.g. (username,)
    def query_multiple(self, sql: str, values: Tuple) -> List[Dict]:
        cur = self.conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(sql, values)
        return cur.fetchall()

    # Used for select statements.
    def query_single(self, sql: str, values: Tuple) -> Optional[Dict]:
        cur = self.conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(sql, values)
        return cur.fetchone()

    # Note that tuple must be a list so for single items, it must still contain a trailing comma
    # e.g. (username,)
    def commit(self, sql: str, values: Tuple):
        try:
            cur = self.conn.cursor(cursor_factory=RealDictCursor)
            cur.execute(sql, values)
            self.conn.commit()
            cur.close()
        except Exception as e:
            self.conn.rollback()
            cur.close()
            raise Exception("Commit exception") from e

    # Note that tuple must be a list so for single items, it must still contain a trailing comma
    # e.g. (username,)
    def commit_single_row_with_return(self, sql: str, values: Tuple) -> Dict:
        try:
            cur = self.conn.cursor(cursor_factory=RealDictCursor)
            cur.execute(sql, values)
            ret = cur.fetchone()
            self.conn.commit()
            cur.close()
            return ret
        except Excpetion as e:
            self.conn.rollback()
            cur.close()
            raise Exception("Commit exception") from e