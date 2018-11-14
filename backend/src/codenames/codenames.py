from src.codenames.codenames_database import CodenamesDatabase
from src.codenames.location import Location
import random
from typing import List, Dict, Optional


class Codenames:
    NUM_AGENTS_FOR_VICTORY = 15

    def __init__(self, database):
        self._codenames_database = CodenamesDatabase(database)

    def get_players_in_game(self, game_id) -> List[str]:
        game = self._codenames_database.get_game(game_id)
        if game is None:
            return None
        return [game[CodenamesDatabase.CODENAMES_GAMES_PLAYER1], game[CodenamesDatabase.CODENAMES_GAMES_PLAYER2]]

    def create_game(self, player1, player2) -> int:
        game_id = self._codenames_database.add_game(player1, player2)

        words = self._get_words_for_new_game()
        self._codenames_database.initialize_words_for_game(game_id, words)

        locations = Codenames._generate_locations()
        self._codenames_database.initialize_locations_for_game(game_id, player1, player2, locations)
        return game_id

    # Returns a dict with keys "game", "turns_to_hints", "turns_to_guesses", "words_for_game",
    # and "locations_owned_by_player". These correspond to the keys of the corresponding tables.
    def get_latest_game(self, player) -> Optional[Dict]:
        game = self._codenames_database.get_latest_game(player)
        if game is None:
            return None
        turns_to_hints = self._codenames_database.get_turns_to_hints(game[CodenamesDatabase.CODENAMES_GAMES_ID])
        turns_to_guesses = self._codenames_database.get_turns_to_guesses(game[CodenamesDatabase.CODENAMES_GAMES_ID])
        words_for_game = self._codenames_database.get_words_for_game(game[CodenamesDatabase.CODENAMES_GAMES_ID])
        locations_owned_by_player = self._codenames_database.get_locations_owned_by_player(
            game[CodenamesDatabase.CODENAMES_GAMES_ID], player)
        return {
            "game": game,
            "turns_to_hints": turns_to_hints,
            "turns_to_guesses": turns_to_guesses,
            "words_for_game": words_for_game,
            "locations_owned_by_player": locations_owned_by_player
        }

    def give_hint(self, game_id, player, hint_word, hint_number):
        game = self._codenames_database.get_game(game_id)
        Codenames._validate_player_turn(game, player)
        if not Codenames._is_current_player_turn(player, game):
            raise Exception("It is not that player's turn")
        if game[CodenamesDatabase.CODENAMES_GAMES_TURN_TYPE] != CodenamesDatabase.CODENAMES_GAMES_TURN_TYPE_GIVE_HINT:
            raise Exception("It is not the time to give hints.")
        self._codenames_database.add_hint(
            game_id, game[CodenamesDatabase.CODENAMES_GAMES_TURN_NUMBER], player, hint_word, hint_number)
        self._codenames_database.update_game_turn(
            game_id, game[CodenamesDatabase.CODENAMES_GAMES_TURN_NUMBER] + 1,
            CodenamesDatabase.CODENAMES_GAMES_TURN_TYPE_GUESS)

    def end_guesses(self, game_id, player):
        game = self._codenames_database.get_game(game_id)
        Codenames._validate_player_turn(game, player)
        if game[CodenamesDatabase.CODENAMES_GAMES_TURN_TYPE] != CodenamesDatabase.CODENAMES_GAMES_TURN_TYPE_GUESS:
            raise Exception("It is not the time to guess.")
        self._codenames_database.update_game_turn(
            game_id, game[CodenamesDatabase.CODENAMES_GAMES_TURN_NUMBER],
            CodenamesDatabase.CODENAMES_GAMES_TURN_TYPE_GIVE_HINT)

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
        game = self._codenames_database.get_game(game_id)
        Codenames._validate_player_turn(game, player)
        if game[CodenamesDatabase.CODENAMES_GAMES_TURN_TYPE] != CodenamesDatabase.CODENAMES_GAMES_TURN_TYPE_GUESS:
            raise Exception("It is not the time to guess.")

        is_player1_turn = game[CodenamesDatabase.CODENAMES_GAMES_PLAYER1] == player
        word_in_game = self._codenames_database.get_word_in_game(game_id, guessed_word)
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

        location_for_word = self._codenames_database.get_location_at_index(game_id, other_player, word_index)
        if location_for_word is None:
            raise Exception("No location could be found corresponding to that word index")

        guess_outcome = ""
        new_word_status = ""

        if (location_for_word[CodenamesDatabase.CODENAMES_GAMES_TO_LOCATIONS_LOCATION_TYPE] ==
                Location.LOCATION_TYPE_AGENT):
            guess_outcome = CodenamesDatabase.CODENAMES_TURNS_TO_GUESSES_GUESS_OUTCOME_AGENT_FOUND
            new_word_status = CodenamesDatabase.CODENAMES_GAMES_TO_WORDS_WORD_STATUS_AGENT_FOUND
            num_found_agents_dict = self._codenames_database.get_num_found_agents_for_game(game_id)
            if num_found_agents_dict is None:
                raise Exception("Num found agents is none.")
            num_found_agents = num_found_agents_dict["count"]
            # If the current number of agents found is 14 then the current success makes 15 agents found total.
            if num_found_agents == Codenames.NUM_AGENTS_FOR_VICTORY - 1:
                self._codenames_database.update_game_over(game_id, False)
        elif (location_for_word[CodenamesDatabase.CODENAMES_GAMES_TO_LOCATIONS_LOCATION_TYPE] ==
              Location.LOCATION_TYPE_BYSTANDER):
            guess_outcome = CodenamesDatabase.CODENAMES_TURNS_TO_GUESSES_GUESS_OUTCOME_HIT_BYSTANDER
            if is_player1_turn:
                if (word_in_game[CodenamesDatabase.CODENAMES_GAMES_TO_WORDS_WORD_STATUS] ==
                        CodenamesDatabase.CODENAMES_GAMES_TO_WORDS_WORD_STATUS_PLAYER_2_HIT_BYSTANDER):
                    print("HERE1")
                    new_word_status = CodenamesDatabase.CODENAMES_GAMES_TO_WORDS_WORD_STATUS_BOTH_PLAYERS_HIT_BYSTANDERS
                else:
                    print("HERE12")
                    new_word_status = CodenamesDatabase.CODENAMES_GAMES_TO_WORDS_WORD_STATUS_PLAYER_1_HIT_BYSTANDER
            else:
                if (word_in_game[CodenamesDatabase.CODENAMES_GAMES_TO_WORDS_WORD_STATUS] ==
                        CodenamesDatabase.CODENAMES_GAMES_TO_WORDS_WORD_STATUS_PLAYER_1_HIT_BYSTANDER):
                    new_word_status = CodenamesDatabase.CODENAMES_GAMES_TO_WORDS_WORD_STATUS_BOTH_PLAYERS_HIT_BYSTANDERS
                    print("HERE13")
                else:
                    new_word_status = CodenamesDatabase.CODENAMES_GAMES_TO_WORDS_WORD_STATUS_PLAYER_2_HIT_BYSTANDER
                    print("HERE4")
            self._codenames_database.update_game_turn(
                game_id, game[CodenamesDatabase.CODENAMES_GAMES_TURN_NUMBER],
                CodenamesDatabase.CODENAMES_GAMES_TURN_TYPE_GIVE_HINT)
        elif (location_for_word[CodenamesDatabase.CODENAMES_GAMES_TO_LOCATIONS_LOCATION_TYPE] ==
              Location.LOCATION_TYPE_ASSASSIN):
            guess_outcome = CodenamesDatabase.CODENAMES_TURNS_TO_GUESSES_GUESS_OUTCOME_ASSASSIN_FOUND
            new_word_status = CodenamesDatabase.CODENAMES_GAMES_TO_WORDS_WORD_STATUS_ASSASSIN_FOUND
            self._codenames_database.update_game_over(game_id, True)
        else:
            raise Exception("Unknown location type")
        self._codenames_database.add_guess(
            game_id, game[CodenamesDatabase.CODENAMES_GAMES_TURN_NUMBER], player, guessed_word, guess_outcome)
        self._codenames_database.update_word_status(game_id, word_index, new_word_status)

    @staticmethod
    def _is_current_player_turn(player, game):
        is_current_user_player1 = player == game[CodenamesDatabase.CODENAMES_GAMES_PLAYER1]
        is_player1_turn = game[CodenamesDatabase.CODENAMES_GAMES_TURN_NUMBER] % 2 == 0
        return is_current_user_player1 == is_player1_turn

    def _get_words_for_new_game(self) -> List[str]:
        words = self._codenames_database.get_all_words()
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
