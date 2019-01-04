from src.codenames.codenames_database import CodenamesDatabase
from src.codenames.location import Location
import random
from typing import List, Dict, Optional
import psycopg2
import yaml


class Codenames:
    NUM_AGENTS_FOR_VICTORY = 15
    CODENAMES_WORDS_FILE = "static/codenames/words.yaml"

    def __init__(self, database):
        self._codenames_database = CodenamesDatabase(database)

    # Returns both players in the game as a list with the order: [player1, player2].
    def get_players_in_game(self, game_id) -> List[str]:
        cur = self._codenames_database.get_cursor()

        try:
            game = CodenamesDatabase.get_game(cur, game_id)
            cur.close()
        except psycopg2.Error:
            self._codenames_database.rollback()
            cur.close()
            raise

        if game is None:
            return None
        return [game[CodenamesDatabase.CODENAMES_GAMES_PLAYER1], game[CodenamesDatabase.CODENAMES_GAMES_PLAYER2]]

    def create_game(self, player1, player2) -> int:
        cur = self._codenames_database.get_cursor()

        words = self._get_words_for_new_game()
        locations = Codenames._generate_locations()

        try:
            game_id = CodenamesDatabase.add_game(cur, player1, player2)
            CodenamesDatabase.initialize_words_for_game(cur, game_id, words)
            CodenamesDatabase.initialize_locations_for_game(cur, game_id, player1, player2, locations)

            self._codenames_database.commit()
            cur.close()
        except psycopg2.Error:
            self._codenames_database.rollback()
            cur.close()
            raise

        return game_id

    # Returns a dict with keys "game", "turns_to_hints", "turns_to_guesses", "words_for_game",
    # and "locations_owned_by_player". These correspond to the keys of the corresponding tables.
    def get_latest_game(self, player) -> Optional[Dict]:
        cur = self._codenames_database.get_cursor()

        try:
            game = CodenamesDatabase.get_latest_game(cur, player)
            if game is None:
                return None
            turns_to_hints = CodenamesDatabase.get_turns_to_hints(cur, game[CodenamesDatabase.CODENAMES_GAMES_ID])
            turns_to_guesses = CodenamesDatabase.get_turns_to_guesses(cur, game[CodenamesDatabase.CODENAMES_GAMES_ID])
            words_for_game = CodenamesDatabase.get_words_for_game(cur, game[CodenamesDatabase.CODENAMES_GAMES_ID])
            locations_owned_by_player = CodenamesDatabase.get_locations_owned_by_player(
                cur, game[CodenamesDatabase.CODENAMES_GAMES_ID], player)
            cur.close()
        except psycopg2.Error:
            self._codenames_database.rollback()
            cur.close()
            raise

        return {
            "game": game,
            "turns_to_hints": turns_to_hints,
            "turns_to_guesses": turns_to_guesses,
            "words_for_game": words_for_game,
            "locations_owned_by_player": locations_owned_by_player
        }

    def give_hint(self, game_id, player, hint_word, hint_number):
        cur = self._codenames_database.get_cursor()

        try:
            game = CodenamesDatabase.get_game(cur, game_id)
            Codenames._validate_player_turn(game, player)
            if not Codenames._is_current_player_turn(player, game):
                raise Exception("It is not that player's turn")
            if (game[CodenamesDatabase.CODENAMES_GAMES_TURN_TYPE] !=
                    CodenamesDatabase.CODENAMES_GAMES_TURN_TYPE_GIVE_HINT):
                raise Exception("It is not the time to give hints.")
            CodenamesDatabase.add_hint(
                cur, game_id, game[CodenamesDatabase.CODENAMES_GAMES_TURN_NUMBER], player, hint_word, hint_number)
            CodenamesDatabase.update_game_turn(
                cur, game_id, game[CodenamesDatabase.CODENAMES_GAMES_TURN_NUMBER] + 1,
                CodenamesDatabase.CODENAMES_GAMES_TURN_TYPE_GUESS)
            self._codenames_database.commit()
            cur.close()
        except psycopg2.Error:
            self._codenames_database.rollback()
            cur.close()
            raise

    def end_guesses(self, game_id, player):
        cur = self._codenames_database.get_cursor()

        try:
            game = CodenamesDatabase.get_game(cur, game_id)
            Codenames._validate_player_turn(game, player)
            if game[CodenamesDatabase.CODENAMES_GAMES_TURN_TYPE] != CodenamesDatabase.CODENAMES_GAMES_TURN_TYPE_GUESS:
                raise Exception("It is not the time to guess.")
            CodenamesDatabase.update_game_time_tokens_used(
                cur, game_id, game[CodenamesDatabase.CODENAMES_GAMES_TIME_TOKENS_USED] + 1)
            if self._player_has_hints_to_give(game_id, player):
                CodenamesDatabase.update_game_turn(
                    cur, game_id, game[CodenamesDatabase.CODENAMES_GAMES_TURN_NUMBER],
                    CodenamesDatabase.CODENAMES_GAMES_TURN_TYPE_GIVE_HINT)
            else:
                CodenamesDatabase.update_game_turn(
                    cur, game_id, game[CodenamesDatabase.CODENAMES_GAMES_TURN_NUMBER] + 1,
                    CodenamesDatabase.CODENAMES_GAMES_TURN_TYPE_GIVE_HINT)
            self._codenames_database.commit()
            cur.close()
        except psycopg2.Error:
            self._codenames_database.rollback()
            cur.close()
            raise

    # Returns true if the player in the game has hints remaining to give or if they have already completed their
    # location card.
    def _player_has_hints_to_give(self, game_id, player):
        cur = self._codenames_database.get_cursor()

        ret = False
        try:
            locations_owned_by_player = CodenamesDatabase.get_locations_owned_by_player(cur, game_id, player)
            words_in_game = CodenamesDatabase.get_words_for_game(cur, game_id)

            for (index, location) in enumerate(locations_owned_by_player):
                if (location[CodenamesDatabase.CODENAMES_GAMES_TO_LOCATIONS_LOCATION_TYPE] ==
                        CodenamesDatabase.CODENAMES_GAMES_TO_LOCATIONS_LOCATION_TYPE_AGENT):
                    if (words_in_game[index][CodenamesDatabase.CODENAMES_GAMES_TO_WORDS_WORD_STATUS] !=
                            CodenamesDatabase.CODENAMES_GAMES_TO_WORDS_WORD_STATUS_AGENT_FOUND):
                        ret = True
            cur.close()
        except psycopg2.Error:
            self._codenames_database.rollback()
            cur.close()
            raise

        return ret

    # Given a game object and a player who is trying to play a turn, raise an exception if it is not their turn.
    @staticmethod
    def _validate_player_turn(game, player):
        if game is None:
            raise Exception("Game with id (%s) does not exist." % game_id)
        if game[CodenamesDatabase.CODENAMES_GAMES_GAME_OVER]:
            raise Exception("Game is already over.")
        if not Codenames._is_current_player_turn(player, game):
            raise Exception("It is not that player's turn")

    # Given a game object and a player, return the name of the other player in the game.
    @staticmethod
    def _other_player(player, game) -> str:
        if game[CodenamesDatabase.CODENAMES_GAMES_PLAYER1] == player:
            return game[CodenamesDatabase.CODENAMES_GAMES_PLAYER2]
        return game[CodenamesDatabase.CODENAMES_GAMES_PLAYER1]

    def guess(self, game_id, player, guessed_word):
        cur = self._codenames_database.get_cursor()

        try:
            game = CodenamesDatabase.get_game(cur, game_id)
            Codenames._validate_player_turn(game, player)
            if game[CodenamesDatabase.CODENAMES_GAMES_TURN_TYPE] != CodenamesDatabase.CODENAMES_GAMES_TURN_TYPE_GUESS:
                raise Exception("It is not the time to guess.")

            is_player1_turn = game[CodenamesDatabase.CODENAMES_GAMES_PLAYER1] == player
            word_in_game = CodenamesDatabase.get_word_in_game(cur, game_id, guessed_word)
            if word_in_game is None:
                raise Exception("Guessed word not found in game.")
            if (word_in_game[CodenamesDatabase.CODENAMES_GAMES_TO_WORDS_WORD_STATUS] !=
                    CodenamesDatabase.CODENAMES_GAMES_TO_WORDS_WORD_STATUS_UNCHECKED):
                if (is_player1_turn and word_in_game["word_status"] !=
                        CodenamesDatabase.CODENAMES_GAMES_TO_WORDS_WORD_STATUS_PLAYER_2_HIT_BYSTANDER):
                    raise Exception("Invalid word status for player 1.")
                elif ((not is_player1_turn) and word_in_game["word_status"] !=
                      CodenamesDatabase.CODENAMES_GAMES_TO_WORDS_WORD_STATUS_PLAYER_1_HIT_BYSTANDER):
                    raise Exception("Invalid word status for player 2.")

            word_index = word_in_game[CodenamesDatabase.CODENAMES_GAMES_TO_WORDS_WORD_INDEX]
            other_player = Codenames._other_player(player, game)

            location_for_word = CodenamesDatabase.get_location_at_index(cur, game_id, other_player, word_index)
            if location_for_word is None:
                raise Exception("No location could be found corresponding to that word index")

            guess_outcome = ""
            new_word_status = ""

            if (location_for_word[CodenamesDatabase.CODENAMES_GAMES_TO_LOCATIONS_LOCATION_TYPE] ==
                    Location.LOCATION_TYPE_AGENT):
                guess_outcome = CodenamesDatabase.CODENAMES_TURNS_TO_GUESSES_GUESS_OUTCOME_AGENT_FOUND
                new_word_status = CodenamesDatabase.CODENAMES_GAMES_TO_WORDS_WORD_STATUS_AGENT_FOUND
                num_found_agents_dict = CodenamesDatabase.get_num_found_agents_for_game(cur, game_id)
                if num_found_agents_dict is None:
                    raise Exception("Num found agents is none.")
                num_found_agents = num_found_agents_dict["count"]
                # If the current number of agents found is 14 then the current success makes 15 agents found total.
                if num_found_agents == Codenames.NUM_AGENTS_FOR_VICTORY - 1:
                    CodenamesDatabase.update_game_over(cur, game_id, False)
            elif (location_for_word[CodenamesDatabase.CODENAMES_GAMES_TO_LOCATIONS_LOCATION_TYPE] ==
                  Location.LOCATION_TYPE_BYSTANDER):
                guess_outcome = CodenamesDatabase.CODENAMES_TURNS_TO_GUESSES_GUESS_OUTCOME_HIT_BYSTANDER
                if is_player1_turn:
                    if (word_in_game[CodenamesDatabase.CODENAMES_GAMES_TO_WORDS_WORD_STATUS] ==
                            CodenamesDatabase.CODENAMES_GAMES_TO_WORDS_WORD_STATUS_PLAYER_2_HIT_BYSTANDER):
                        new_word_status = (
                            CodenamesDatabase.CODENAMES_GAMES_TO_WORDS_WORD_STATUS_BOTH_PLAYERS_HIT_BYSTANDERS)
                    else:
                        new_word_status = CodenamesDatabase.CODENAMES_GAMES_TO_WORDS_WORD_STATUS_PLAYER_1_HIT_BYSTANDER
                else:
                    if (word_in_game[CodenamesDatabase.CODENAMES_GAMES_TO_WORDS_WORD_STATUS] ==
                            CodenamesDatabase.CODENAMES_GAMES_TO_WORDS_WORD_STATUS_PLAYER_1_HIT_BYSTANDER):
                        new_word_status = (
                            CodenamesDatabase.CODENAMES_GAMES_TO_WORDS_WORD_STATUS_BOTH_PLAYERS_HIT_BYSTANDERS)
                    else:
                        new_word_status = CodenamesDatabase.CODENAMES_GAMES_TO_WORDS_WORD_STATUS_PLAYER_2_HIT_BYSTANDER
                CodenamesDatabase.update_game_time_tokens_used(
                    cur, game_id, game[CodenamesDatabase.CODENAMES_GAMES_TIME_TOKENS_USED] + 1)
                if self._player_has_hints_to_give(game_id, player):
                    CodenamesDatabase.update_game_turn(
                        cur, game_id, game[CodenamesDatabase.CODENAMES_GAMES_TURN_NUMBER],
                        CodenamesDatabase.CODENAMES_GAMES_TURN_TYPE_GIVE_HINT)
                else:
                    CodenamesDatabase.update_game_turn(
                        cur, game_id, game[CodenamesDatabase.CODENAMES_GAMES_TURN_NUMBER] + 1,
                        CodenamesDatabase.CODENAMES_GAMES_TURN_TYPE_GIVE_HINT)
            elif (location_for_word[CodenamesDatabase.CODENAMES_GAMES_TO_LOCATIONS_LOCATION_TYPE] ==
                  Location.LOCATION_TYPE_ASSASSIN):
                guess_outcome = CodenamesDatabase.CODENAMES_TURNS_TO_GUESSES_GUESS_OUTCOME_ASSASSIN_FOUND
                new_word_status = CodenamesDatabase.CODENAMES_GAMES_TO_WORDS_WORD_STATUS_ASSASSIN_FOUND
                CodenamesDatabase.update_game_over(cur, game_id, True)
            else:
                raise Exception("Unknown location type")
            CodenamesDatabase.add_guess(
                cur, game_id, game[CodenamesDatabase.CODENAMES_GAMES_TURN_NUMBER], player, guessed_word, guess_outcome)
            CodenamesDatabase.update_word_status(cur, game_id, word_index, new_word_status)
            self._codenames_database.commit()
            cur.close()
        except psycopg2.Error:
            self._codenames_database.rollback()
            cur.close()
            raise

    @staticmethod
    def _is_current_player_turn(player, game):
        is_current_user_player1 = player == game[CodenamesDatabase.CODENAMES_GAMES_PLAYER1]
        is_player1_turn = game[CodenamesDatabase.CODENAMES_GAMES_TURN_NUMBER] % 2 == 0
        return is_current_user_player1 == is_player1_turn

    @staticmethod
    def _get_words_for_new_game() -> List[str]:
        with open(Codenames.CODENAMES_WORDS_FILE, 'r') as stream:
            try:
                words = yaml.load(stream)
            except yaml.YAMLError as exc:
                print(exc)
        random.shuffle(words)
        return words[:25]

    # Generates locations for a new game in a random order.
    @staticmethod
    def _generate_locations() -> List[Location]:
        locations = []
        # TODO: This is not the correct number
        for i in range(1):
            locations.append(Location(Location.LOCATION_TYPE_ASSASSIN, Location.LOCATION_TYPE_AGENT))
        for i in range(5):
            locations.append(Location(Location.LOCATION_TYPE_BYSTANDER, Location.LOCATION_TYPE_AGENT))
        for i in range(3):
            locations.append(Location(Location.LOCATION_TYPE_AGENT, Location.LOCATION_TYPE_AGENT))
        for i in range(5):
            locations.append(Location(Location.LOCATION_TYPE_AGENT, Location.LOCATION_TYPE_BYSTANDER))
        for i in range(1):
            locations.append(Location(Location.LOCATION_TYPE_AGENT, Location.LOCATION_TYPE_ASSASSIN))
        for i in range(1):
            locations.append(Location(Location.LOCATION_TYPE_BYSTANDER, Location.LOCATION_TYPE_ASSASSIN))
        for i in range(1):
            locations.append(Location(Location.LOCATION_TYPE_ASSASSIN, Location.LOCATION_TYPE_ASSASSIN))
        for i in range(7):
            locations.append(Location(Location.LOCATION_TYPE_BYSTANDER, Location.LOCATION_TYPE_BYSTANDER))
        for i in range(1):
            locations.append(Location(Location.LOCATION_TYPE_ASSASSIN, Location.LOCATION_TYPE_BYSTANDER))
        random.shuffle(locations)
        return locations
