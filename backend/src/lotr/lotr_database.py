from typing import Dict, Optional
import psycopg2


class LotrDatabase:
  LOTR_GAMES_ID = "id"
  LOTR_GAMES_PLAYER1 = "player1"
  LOTR_GAMES_PLAYER2 = "player2"
  LOTR_GAMES_DATA = "data"

  def __init__(self, database):
    self._database = database

  def get_cursor(self):
    return self._database.get_cursor()

  def commit(self):
    self._database.commit()

  def rollback(self):
    self._database.rollback()

  @staticmethod
  def get_latest_deck(cur, player):
    cur.execute(
        "SELECT xml from lotr_most_recent_deck where player = %s LIMIT 1",
        (player,))
    result = cur.fetchone()
    if result is None:
      return None
    return result["xml"]
