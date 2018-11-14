from src.codenames.codenames_database import CodenamesDatabase
from src.codenames.location import Location
import random
from typing import List, Dict


class Codenames:
    def __init__(self, database):
        self._codenames_database = CodenamesDatabase(database)

    def create_game(self, player1, player2):
        game_id = self._codenames_database.create_game(player1, player2)
        words = self._get_words_for_new_game()
        self._codenames_database.initialize_words_for_game(game_id, words)
        locations = Codenames._generate_locations()
        self._codenames_database.initialize_locations_for_game(game_id, player1, player2, locations)

    def get_latest_game(self, player) -> Dict:
        game = self._codenames_database.get_latest_game(player)
        turns_to_hints = self._codenames_database.get_turns_to_hints(game["id"])
        turns_to_guesses = self._codenames_database.get_turns_to_guesses(game["id"])
        words_for_game = self._codenames_database.get_words_for_game(game["id"])
        locations_owned_by_player = self._codenames_database.get_locations_owned_by_player(game["id"], player)
        return {
            "game": game,
            "turns_to_hints": turns_to_hints,
            "turns_to_guesses": turns_to_guesses,
            "words_for_game": words_for_game,
            "locations_owned_by_player": locations_owned_by_player
        }

    def give_hint(self, game_id, player, hint_word, hint_number):
        game = self._codenames_database.get_game(game_id)
        if player != game["player1"] and player != game["player2"]:
            raise Exception("Invalid player specified for the game.")
        if not Codenames._is_current_player_turn(player, game):
            raise Exception("It is not that player's turn")
        if game["turn_type"] != "give_hint":
            raise Exception("It is not the time to give hints.")
        self._codenames_database.add_hint(game_id, game["turn_number"], player, hint_word, hint_number)
        self._codenames_database.update_game_turn(game_id, game["turn_number"] + 1, "guess")

    def end_guesses(self, game_id, player):
        game = self._codenames_database.get_game(game_id)
        if not Codenames._is_current_player_turn(player, game):
            raise Exception("It is not that player's turn")
        if game["turn_type"] != "guess":
            raise Exception("It is not the time to guess.")
        self._codenames_database.update_game_turn(game_id, game["turn_number"], "give_hint")

    @staticmethod
    def _other_player(player, game):
      if game["player1"] == player:
        return game["player2"]
      return game["player1"]

    def guess(self, game_id, player, guessed_word):
        game = self._codenames_database.get_game(game_id)
        if not Codenames._is_current_player_turn(player, game):
            raise Exception("It is not that player's turn")
        if game["turn_type"] != "guess":
            raise Exception("It is not the time to guess.")

        is_player1_turn = game['player1'] == player
        word_in_game = self._codenames_database.get_word_in_game(game_id, guessed_word)
        if word_in_game["word_status"] != "unchecked":
            if is_player1_turn and word_in_game["word_status"] != "player_2_hit_bystander":
                raise Exception("Invalid word status for player 1.")
            elif (not is_player1_turn) and word_in_game["word_status"] != "player_1_hit_bystander":
                raise Exception("Invalid word status for player 2.")

        word_index = word_in_game["word_index"]
        other_player = Codenames._other_player(player, game)

        location_for_word = self._codenames_database.get_location_at_index(game_id, other_player, word_index)

        guess_outcome = ""
        new_word_status = ""

        if location_for_word["location_type"] == "agent":
            guess_outcome = "agent_found"
            new_word_status = "agent_found"
            num_found_agents = self._codenames_database.get_num_found_agents_for_game(game_id)["count"]
            # Hack. Because the next one makes 15.
            if num_found_agents == 14:
                self._codenames_database.set_game_over(game_id, False)
        elif location_for_word["location_type"] == "bystander":
            guess_outcome = "hit_bystander"
            if is_player1_turn:
                if word_in_game["word_status"] == "player_2_hit_bystander":
                    new_word_status = "both_players_hit_bystanders"
                else:
                    new_word_status = "player_1_hit_bystander"
            else:
                if word_in_game["word_status"] == "player_1_hit_bystander":
                    new_word_status = "both_players_hit_bystanders"
                else:
                    new_word_status = "player_2_hit_bystander"
            self._codenames_database.update_game_turn(game_id, game["turn_number"], "give_hint")
        elif location_for_word["location_type"] == "assassin":
            guess_outcome = "assassin_found"
            new_word_status = "assassin_found"
            self._codenames_database.set_game_over(game_id, True)
        self._codenames_database.add_guess(game_id, game["turn_number"], player, guessed_word, guess_outcome)
        self._codenames_database.update_word_status(game_id, word_index, new_word_status)



    @staticmethod
    def _is_current_player_turn(player, game):
        is_current_user_player1 = player == game["player1"]
        is_player1_turn = game["turn_number"] % 2 == 0
        return is_current_user_player1 == is_player1_turn

    def _get_words_for_new_game(self) -> List[str]:
        words = self._codenames_database.get_all_words()
        random.shuffle(words)
        return words[:25]

    @staticmethod
    def _generate_locations() -> List:
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
