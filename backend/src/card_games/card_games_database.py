from typing import Dict, Optional
import psycopg2


class CardGamesDatabase:

  # games_table {string} the name of the table to get the game from.
  def __init__(self, database, games_table, game_data_table):
    self._database = database
    self._games_table = games_table
    self._game_data_table = game_data_table

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
        "(player1, player2) VALUES(%s, %s) RETURNING id",
        (player1, player2))
    game_id = cur.fetchone()["id"]
    return game_id

  # Gets the latest turn in the given game.
  # game_id {string} the id of the game to fetch data for.
  # return {Object} an object representing the row of the game data.
  def get_latest_turn_in_game(self, cur, game_id) -> Optional[Dict]:
    cur.execute(
        "SELECT * from " + self._game_data_table +
        " where game_id = %s ORDER BY id DESC LIMIT 1",
        (game_id,))
    return cur.fetchone()

  # Gets the latest turn in the given game.
  # game_id {string} the id of the game to fetch data for.
  # return {Object} an object representing the row of the game data.
  def get_num_turns_in_game(self, cur, game_id) -> int:
    cur.execute(
        "SELECT count(*) as count from " + self._game_data_table +
        " where game_id = %s",
        (game_id,))
    return cur.fetchone()["count"]

  # Deletes the latest turn in the given game.
  # game_id {string} the id of the game to fetch data for.
  # return {Object} an object representing the row of the game data.
  def delete_latest_turn_in_game(self, cur, game_id) -> Optional[Dict]:
    cur.execute(
        "DELETE from " + self._game_data_table +
        " where id in (SELECT id from " + self._game_data_table +
        " WHERE game_id = %s ORDER BY id DESC LIMIT 1)",
        (game_id,))

  # Gets the latest game for the player.
  # player {string} the name of the player to get the latest game for.
  # return {Object} an object representing the row of the game data.
  def get_latest_game(self, cur, player) -> Optional[Dict]:
    cur.execute(
        "SELECT * from " + self._games_table + " join " + self._game_data_table + " on " +
        self._games_table + ".id = " + self._game_data_table + ".game_id" +
        " where player1 = %s or player2 = %s ORDER BY " +
        self._game_data_table + ".id DESC LIMIT 1",
        (player, player))
    return cur.fetchone()

  # Updates the game with the new game data.
  # game_id {number} the id of the game to update.
  # data {Object} the object of game data.
  def update_game(self, cur, game_id, data) -> int:
    cur.execute("INSERT INTO " + self._game_data_table + " (game_id, data) VALUES(%s, %s)",
                (game_id, psycopg2.extras.Json(data)))

  # Deletes the games with the given players.
  # player1 {string} the id of the player.
  # player2 {string} the id of the player.
  def delete_game(self, cur, player1, player2) -> int:
    cur.execute("DELETE FROM " + self._games_table + " CASCADE where player1 = %s or player1 = %s or player2 = %s or player2 = %s",
                (player1, player2, player1, player2))
