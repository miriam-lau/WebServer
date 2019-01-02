from typing import Dict, Optional
import psycopg2

class DominionDatabase:
    DOMINION_GAMES_ID = "id"
    DOMINION_GAMES_PLAYER1 = "player1"
    DOMINION_GAMES_PLAYER2 = "player2"
    DOMINION_GAMES_DATA = "data"

    def __init__(self, database):
        self._database = database

    def get_cursor(self):
        return self._database.get_cursor()

    def commit(self):
        self._database.commit()

    def rollback(self):
        self._database.rollback()

    # Returned Dict has all fields of dominion_games
    @staticmethod
    def get_game(cur, game_id) -> Optional[Dict]:
        cur.execute(
            "SELECT * from dominion_games where id = %s", (game_id,))
        return cur.fetchone()

    @staticmethod
    def add_game(cur, player1, player2, data) -> int:
        cur.execute(
            "INSERT INTO dominion_games(player1, player2, data) VALUES(%s, %s, %s) RETURNING id",
            (player1, player2, psycopg2.extras.Json(data)))
        game_id = cur.fetchone()["id"]
        return game_id

    # Returned Dict has all fields of dominion_games
    @staticmethod
    def get_latest_game(cur, player) -> Optional[Dict]:
        cur.execute(
            "SELECT * from dominion_games where player1 = %s or player2 = %s ORDER BY id DESC LIMIT 1",
            (player, player))
        return cur.fetchone()

    @staticmethod
    def update_game(cur, game_id, data) -> int:
        cur.execute("UPDATE dominion_games set data = %s where id = %s", (psycopg2.extras.Json(data), game_id))
