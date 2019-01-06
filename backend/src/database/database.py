import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Tuple, List, Dict, Optional


# Note that the 'values' tuple must be a list so for single items, it must still contain a trailing comma
# e.g. (username,)
class Database:
  HOST = "192.168.86.100"
  PROD_DATABASE = "webserver"
  DEV_DATABASE = "webserverdevelopment"
  USER = "webserver"
  PASSWORD = "password"

  def __init__(self, is_production):
    database = Database.PROD_DATABASE if is_production else Database.DEV_DATABASE
    self.conn = psycopg2.connect(
        host=Database.HOST, database=database, user=Database.USER, password=Database.PASSWORD)

  def get_cursor(self):
    return self.conn.cursor(cursor_factory=RealDictCursor)

  def commit(self):
    self.conn.commit()

  def rollback(self):
    self.conn.rollback()
