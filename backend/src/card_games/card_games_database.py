from typing import Dict, Optional
import psycopg2


class CardGamesDatabase:

  # games_table {string} the name of the table to get the game from.
  def __init__(self, database, games_table):
    self._database = database
    self._games_table = games_table

  def get_cursor(self):
    return self._database.get_cursor()

  def commit(self):
    self._database.commit()

  def rollback(self):
    self._database.rollback()

  # Gets the game.
  # game_id {string} the id of the game to get.
  # return {Object} an object representing the row of the game data.
  def get_game(self, cur, game_id) -> Optional[Dict]:
    cur.execute(
        "SELECT * from " + self._games_table + " where id = %s", (game_id,))
    return cur.fetchone()

  # Adds a game.
  # player1 {string} the name of the first player.
  # player2 {string} the name of the second player.
  # return {number} the game id.
  def add_game(self, cur, player1, player2) -> int:
    cur.execute(
        "INSERT INTO " + self._games_table +
        "(player1, player2, data) VALUES(%s, %s, %s) RETURNING id",
        (player1, player2, psycopg2.extras.Json({})))
    game_id = cur.fetchone()["id"]
    return game_id

  # Gets the latest game for the player.
  # player {string} the name of the player to get the latest game for.
  # return {Object} an object representing the row of the game data.
  def get_latest_game(self, cur, player) -> Optional[Dict]:
    cur.execute(
        "SELECT * from " + self._games_table +
        " where player1 = %s or player2 = %s ORDER BY id DESC LIMIT 1",
        (player, player))
    return cur.fetchone()

  # Updates the game with the new game data.
  # game_id {number} the id of the game to update.
  # data {Object} the object of game data.
  def update_game(self, cur, game_id, data) -> int:
    cur.execute("UPDATE " + self._games_table + " set data = %s where id = %s",
                (psycopg2.extras.Json(data), game_id))
