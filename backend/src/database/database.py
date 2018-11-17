import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Tuple, List, Dict, Optional


# Used to pass to the commit_multiple_rows function of Database.
class CommitStatement:
    def __init__(self, sql, values):
        self.sql = sql
        self.values = values


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
    def commit_multiple_rows(self, statements: List[CommitStatement]):
        try:
            cur = self.conn.cursor(cursor_factory=RealDictCursor)
            for statement in statements:
                cur.execute(statement.sql, statement.values)
            self.conn.commit()
            cur.close()
        except Exception as e:
            self.conn.rollback()
            cur.close()
            print(e)
            raise Exception("Commit exception")

    # Note that tuple must be a list so for single items, it must still contain a trailing comma
    # e.g. (username,)
    def commit_single_row(self, sql: str, values: Tuple):
        try:
            cur = self.conn.cursor(cursor_factory=RealDictCursor)
            cur.execute(sql, values)
            self.conn.commit()
            cur.close()
        except Exception as e:
            self.conn.rollback()
            cur.close()
            print(e)
            raise Exception("Commit exception")

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
            print(e)
            raise Exception("Commit exception")
