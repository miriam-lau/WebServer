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

  # Returned Dict has all fields of lotr_games
  @staticmethod
  def get_game(cur, game_id) -> Optional[Dict]:
    cur.execute(
        "SELECT * from lotr_games where id = %s", (game_id,))
    return cur.fetchone()

  @staticmethod
  def add_game(cur, player1, player2, data, player1_deck_xml, player2_deck_xml) -> int:
      cur.execute(
        "INSERT INTO lotr_most_recent_deck (player, xml) VALUES(%s, %s) ON CONFLICT(player) DO UPDATE" +
        " SET xml = %s", (player1, player1_deck_xml, player1_deck_xml))
      cur.execute(
        "INSERT INTO lotr_most_recent_deck (player, xml) VALUES(%s, %s) ON CONFLICT(player) DO UPDATE" +
        " SET xml = %s", (player2, player2_deck_xml, player2_deck_xml))
      cur.execute(
          "INSERT INTO lotr_games(player1, player2, data) VALUES(%s, %s, %s) RETURNING id",
          (player1, player2, psycopg2.extras.Json(data)))
      game_id = cur.fetchone()["id"]
      return game_id

  # Returned Dict has all fields of lotr_games
  @staticmethod
  def get_latest_game(cur, player) -> Optional[Dict]:
    cur.execute(
        "SELECT * from lotr_games where player1 = %s or player2 = %s ORDER BY id DESC LIMIT 1",
        (player, player))
    return cur.fetchone()

  @staticmethod
  def get_latest_deck(cur, player):
    cur.execute(
        "SELECT xml from lotr_most_recent_deck where player = %s LIMIT 1",
        (player,))
    result = cur.fetchone()
    if result is None:
      return None
    return result["xml"]

  @staticmethod
  def update_game(cur, game_id, data) -> int:
    cur.execute("UPDATE lotr_games set data = %s where id = %s", (psycopg2.extras.Json(data), game_id))
