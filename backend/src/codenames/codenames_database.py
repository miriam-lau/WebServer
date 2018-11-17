from typing import List, Dict, Optional
from src.codenames.location import Location


class CodenamesDatabase:
    CODENAMES_GAMES_ID = "id"
    CODENAMES_GAMES_TURN_TYPE = "turn_type"
    CODENAMES_GAMES_TURN_NUMBER = "turn_number"
    CODENAMES_GAMES_GAME_OVER = "game_over"
    CODENAMES_GAMES_PLAYER1 = "player1"
    CODENAMES_GAMES_PLAYER2 = "player2"
    CODENAMES_GAMES_TIME_TOKENS_USED = "time_tokens_used"
    CODENAMES_GAMES_TURN_TYPE_GIVE_HINT = "give_hint"
    CODENAMES_GAMES_TURN_TYPE_GUESS = "guess"
    CODENAMES_GAMES_TO_WORDS_WORD_INDEX = "word_index"
    CODENAMES_GAMES_TO_WORDS_WORD_STATUS = "word_status"
    CODENAMES_GAMES_TO_LOCATIONS_LOCATION_TYPE = "location_type"
    CODENAMES_GAMES_TO_LOCATIONS_LOCATION_TYPE_AGENT = "agent"
    CODENAMES_TURNS_TO_GUESSES_GUESS_OUTCOME_AGENT_FOUND = "agent_found"
    CODENAMES_TURNS_TO_GUESSES_GUESS_OUTCOME_ASSASSIN_FOUND = "assassin_found"
    CODENAMES_TURNS_TO_GUESSES_GUESS_OUTCOME_HIT_BYSTANDER = "hit_bystander"
    CODENAMES_GAMES_TO_WORDS_WORD_STATUS_AGENT_FOUND = "agent_found"
    CODENAMES_GAMES_TO_WORDS_WORD_STATUS_PLAYER_1_HIT_BYSTANDER = "player_1_hit_bystander"
    CODENAMES_GAMES_TO_WORDS_WORD_STATUS_PLAYER_2_HIT_BYSTANDER = "player_2_hit_bystander"
    CODENAMES_GAMES_TO_WORDS_WORD_STATUS_BOTH_PLAYERS_HIT_BYSTANDERS = "both_players_hit_bystanders"
    CODENAMES_GAMES_TO_WORDS_WORD_STATUS_ASSASSIN_FOUND = "assassin_found"
    CODENAMES_GAMES_TO_WORDS_WORD_STATUS_UNCHECKED = "unchecked"

    def __init__(self, database):
        self._database = database

    def add_game(self, player1, player2) -> int:
        game_id = self._database.commit_single_row_with_return(
            "INSERT INTO codenames_games(player1, player2, turn_number, time_tokens_used, turn_type, game_over, " +
            "assassin_found) VALUES(%s, %s, %s, %s, %s, %s, %s) RETURNING id",
            (player1, player2, 0, 0, CodenamesDatabase.CODENAMES_GAMES_TURN_TYPE_GIVE_HINT, False, False))["id"]
        return game_id

    def update_game_turn(self, game_id, turn_number, turn_type):
        self._database.commit_single_row(
          "UPDATE codenames_games SET turn_number = %s, turn_type = %s where id = %s",
          (turn_number, turn_type, game_id))

    def update_game_time_tokens_used(self, game_id, time_tokens_used):
        self._database.commit_single_row(
          "UPDATE codenames_games SET time_tokens_used = %s where id = %s",
          (time_tokens_used, game_id))

    def update_game_over(self, game_id, assassin_found):
        return self._database.commit_single_row(
            "UPDATE codenames_games SET game_over = %s, assassin_found = %s where id = %s",
            (True, assassin_found, game_id))

    # Returned Dict has all fields of codenames_games
    def get_latest_game(self, player) -> Optional[Dict]:
        return self._database.query_single(
            "SELECT * from codenames_games where player1 = %s or player2 = %s ORDER BY id DESC LIMIT 1",
            (player, player))

    # Returned Dict has all fields of codenames_games
    def get_game(self, game_id) -> Optional[Dict]:
        return self._database.query_single(
            "SELECT * from codenames_games where id = %s", (game_id,))

    # Returned Dict has all fields of codenames_games_to_locations
    def get_locations_owned_by_player(self, game_id, player) -> List[Dict]:
        return self._database.query_multiple(
            "SELECT * from codenames_games_to_locations where game_id = %s and player_owning_location = %s " +
            "ORDER BY location_index",
            (game_id, player))

    # Returned Dict has all fields of codenames_games_to_locations
    def get_location_at_index(self, game_id, player, location_index) -> Optional[Dict]:
        return self._database.query_single(
            "SELECT * from codenames_games_to_locations where game_id = %s and player_owning_location = %s " +
            "and location_index = %s",
            (game_id, player, location_index))

    def initialize_locations_for_game(self, game_id, player1, player2, locations: List[Location]):
        for index, location in enumerate(locations):
            self._database.commit_single_row(
                "INSERT INTO codenames_games_to_locations(game_id, player_owning_location, location_index, " +
                "location_type) VALUES(%s, %s, %s, %s)",
                (game_id, player1, index, location.player1_location_type))
            self._database.commit_single_row(
                "INSERT INTO codenames_games_to_locations(game_id, player_owning_location, location_index, " +
                "location_type) VALUES(%s, %s, %s, %s)",
                (game_id, player2, index, location.player2_location_type))

    def initialize_words_for_game(self, game_id, words):
        for index, word in enumerate(words):
            self._database.commit_single_row(
                "INSERT INTO codenames_games_to_words(game_id, word_index, word, word_status) VALUES(%s, %s, %s, %s)",
                (game_id, index, word, "unchecked"))

    # Returned Dict has all fields of codenames_games_to_words
    def get_words_for_game(self, game_id) -> List[Dict]:
        return self._database.query_multiple(
            "SELECT * from codenames_games_to_words where game_id = %s ORDER BY word_index",
            (game_id,))

    # Returned Dict has all fields of codenames_games_to_words
    def get_word_in_game(self, game_id, word) -> Optional[Dict]:
        return self._database.query_single(
            "SELECT * from codenames_games_to_words where game_id = %s and word = %s",
            (game_id, word))

    def update_word_status(self, game_id, word_index, word_status):
        self._database.commit_single_row(
          "UPDATE codenames_games_to_words SET word_status = %s where game_id = %s and word_index = %s",
          (word_status, game_id, word_index))

    # Returned Dict has key "count"
    def get_num_found_agents_for_game(self, game_id) -> Optional[Dict]:
        return self._database.query_single(
            "SELECT COUNT(*) from codenames_games_to_words where word_status = %s and game_id = %s",
            ("agent_found", game_id))

    # Returned Dict has all fields of codenames_turns_to_guesses
    def get_turns_to_guesses(self, game_id) -> List[Dict]:
        return self._database.query_multiple(
            "SELECT * from codenames_turns_to_guesses where game_id = %s ORDER BY turn_number, id",
            (game_id,))

    def add_guess(self, game_id, turn_number, player, guessed_word, guess_outcome):
        self._database.commit_single_row(
          "INSERT INTO codenames_turns_to_guesses(game_id, turn_number, player, guessed_word, guess_outcome) " +
          "VALUES(%s, %s, %s, %s, %s)",
          (game_id, turn_number, player, guessed_word, guess_outcome))

    # Returned Dict has all fields of codenames_turns_to_hints
    def get_turns_to_hints(self, game_id) -> List[Dict]:
        return self._database.query_multiple(
            "SELECT * from codenames_turns_to_hints where game_id = %s ORDER BY turn_number",
            (game_id,))

    # Returned Dict has all fields of codenames_turns_to_hints
    def add_hint(self, game_id, turn_number, player, hint_word, hint_number):
        self._database.commit_single_row(
          "INSERT INTO codenames_turns_to_hints(game_id, turn_number, player, hint_word, hint_number) " +
          "VALUES(%s, %s, %s, %s, %s)",
          (game_id, turn_number, player, hint_word, hint_number))

    # Returned Dict has all fields of codenames_words
    def get_all_words(self) -> List[str]:
        word_maps = self._database.query_multiple("SELECT word from codenames_words", ())
        ret = []
        for word_map in word_maps:
            ret.append(word_map["word"])
        return ret
