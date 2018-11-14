from typing import List, Dict


class CodenamesDatabase:
    def __init__(self, database):
        self._database = database

    # Creates a game in the codenames_games table.
    def create_game(self, player1, player2) -> int:
        game_id = self._database.execute_commit_with_return(
            "INSERT INTO codenames_games(player1, player2, turn_number, turn_type, game_over, assassin_found) " +
            "VALUES(%s, %s, %s, %s, %s, %s) RETURNING id",
            (player1, player2, 0, 'give_hint', False, False))[0]
        return game_id

    def get_all_words(self) -> List[str]:
        wordMaps = self._database.execute_query("SELECT word from codenames_words", ())
        ret = []
        for wordMap in wordMaps:
            ret.append(wordMap["word"])
        return ret

    def initialize_words_for_game(self, game_id, words):
        for index, word in enumerate(words):
            self._database.execute_commit(
                "INSERT INTO codenames_games_to_words(game_id, word_index, word, word_status) VALUES(%s, %s, %s, %s)",
                (game_id, index, word, 'unchecked'))

    def initialize_locations_for_game(self, game_id, player1, player2, locations):
        for index, location in enumerate(locations):
            self._database.execute_commit(
                "INSERT INTO codenames_games_to_locations(game_id, player_owning_location, location_index, " +
                "location_type) VALUES(%s, %s, %s, %s)",
                (game_id, player1, index, location.player1_location_type))
            self._database.execute_commit(
                "INSERT INTO codenames_games_to_locations(game_id, player_owning_location, location_index, " +
                "location_type) VALUES(%s, %s, %s, %s)",
                (game_id, player2, index, location.player2_location_type))

    def get_latest_game(self, player) -> Dict:
        return self._database.execute_query(
            "SELECT * from codenames_games where player1 = %s or player2 = %s ORDER BY id DESC LIMIT 1",
            (player, player))[0]

    def get_turns_to_hints(self, game_id) -> List[Dict]:
        return self._database.execute_query(
            "SELECT * from codenames_turns_to_hints where game_id = %s ORDER BY turn_number",
            (game_id,))

    def get_turns_to_guesses(self, game_id) -> List[Dict]:
        return self._database.execute_query(
            "SELECT * from codenames_turns_to_guesses where game_id = %s ORDER BY turn_number, id",
            (game_id,))

    def get_words_for_game(self, game_id) -> List[Dict]:
        return self._database.execute_query(
            "SELECT * from codenames_games_to_words where game_id = %s ORDER BY word_index",
            (game_id,))

    def get_word_in_game(self, game_id, word) -> List[Dict]:
        return self._database.execute_query(
            "SELECT * from codenames_games_to_words where game_id = %s and word = %s",
            (game_id,word))[0]

    def get_locations_owned_by_player(self, game_id, player) -> List[Dict]:
        return self._database.execute_query(
            "SELECT * from codenames_games_to_locations where game_id = %s and player_owning_location = %s " +
            "ORDER BY location_index",
            (game_id, player))

    def get_location_at_index(self, game_id, player, location_index) -> List[Dict]:
        return self._database.execute_query(
            "SELECT * from codenames_games_to_locations where game_id = %s and player_owning_location = %s " +
            "and location_index = %s",
            (game_id, player, location_index))[0]

    def get_game(self, game_id) -> Dict:
        return self._database.execute_query(
            "SELECT * from codenames_games where id = %s", (game_id,))[0]

    def add_hint(self, game_id, turn_number, player, hint_word, hint_number):
        self._database.execute_commit(
          "INSERT INTO codenames_turns_to_hints(game_id, turn_number, player, hint_word, hint_number) " +
          "VALUES(%s, %s, %s, %s, %s)",
          (game_id, turn_number, player, hint_word, hint_number))

    def add_guess(self, game_id, turn_number, player, guessed_word, guess_outcome):
        self._database.execute_commit(
          "INSERT INTO codenames_turns_to_guesses(game_id, turn_number, player, guessed_word, guess_outcome) " +
          "VALUES(%s, %s, %s, %s, %s)",
          (game_id, turn_number, player, guessed_word, guess_outcome))

    def update_game_turn(self, game_id, turn_number, turn_type):
        self._database.execute_commit(
          "UPDATE codenames_games SET turn_number = %s, turn_type = %s where id = %s",
          (turn_number, turn_type, game_id))

    def update_word_status(self, game_id, word_index, word_status):
        self._database.execute_commit(
          "UPDATE codenames_games_to_words SET word_status = %s where game_id = %s and word_index = %s",
          (word_status, game_id, word_index))

    def get_num_found_agents_for_game(self, game_id):
        return self._database.execute_query(
            "SELECT COUNT(*) from codenames_games_to_words where word_status = %s and game_id = %s",
            ("agent_found", game_id))[0]

    def set_game_over(self, game_id, assassin_found):
        return self._database.execute_commit(
            "UPDATE codenames_games SET game_over = %s, assassin_found = %s where id = %s",
            (True, assassin_found, game_id))