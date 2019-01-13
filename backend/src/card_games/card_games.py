import yaml
import random
import pprint
from src.card_games.card_games_database import CardGamesDatabase
from typing import List, Optional, Dict
import psycopg2
import re
import copy

# Manages card games.
# This class expects to operate on data which has Card objects which have a gameCardId property.


class CardGames:
  def __init__(self, database, games_table):
    self._card_games_database = CardGamesDatabase(database, games_table)

  # Creates a game with the given information. Modifies data to add the gameId.
  # player1 {string} the username of the first player.
  # player2 {string} the username of the second player.
  # data {Object} the data of the game. (Treated as a blob.)
  def create_game(self, player1, player2, data) -> int:
    cur = self._card_games_database.get_cursor()

    try:
      game_id = self._card_games_database.add_game(cur, player1, player2)
      data["gameId"] = game_id
      self._card_games_database.update_game(cur, game_id, data)

      self._card_games_database.commit()
      cur.close()
    except psycopg2.Error:
      self._card_games_database.rollback()
      cur.close()
      raise

    return data

  # Returns the latest game for a player.
  # player {string} the username of the player to fetch.
  # return the game row corresponding to the latest game.
  def get_latest_game(self, player) -> Optional[Dict]:
    cur = self._card_games_database.get_cursor()

    try:
      game = self._card_games_database.get_latest_game(cur, player)
      cur.close()
      if game is None:
        return None
    except psycopg2.Error:
      self._card_games_database.rollback()
      cur.close()
      raise

    return game

  # Performs the given mutations on the game with the given id.
  # game_id {number} the id of the game.
  # mutations {array<{
  #   type {string} the type of mutation to perform. Can be "moveCard", "incrementProperty", "decrementProperty",
  #       or "invertProperty", or "shuffleCards".
  #       incrementProperty expects an integer to be specified and increments that number. Acts on type card or property.
  #       decrementProperty expects an integer to be specified and decrements that number. Acts on type card or property.
  #       invertProperty expects a boolean to be specified and inverts it. Acts on type card or property.
  #       moveCards takes the specified card and moves it from cardPath to destinationCardPath. Acts on type card.
  #       shuffleCards takes in a cardPath and shuffles it. Acts on type array.
  #   dataType {string} the data type to perform the mutation on. Can be "card", "array" or "property".
  #   gameCardId {number?} the id of the card to perform the mutation on. If the card cannot be found in the sourceArray path,
  #       the mutation is skipped. Only used if the dataType specified is of type card.
  #   cardPath {array?} this is an array of keys that determines where in the data object the array of cards are. If the
  #       data type is "card" then this is where the card is found. If it is of type "array", then it is the array that is used.
  #       (e.g., if cardPath is ['a', 'b', 'c'], then the Card is expected to be present in the array defined by
  #       data["a"]["b"]["c"]). Only used if the dataType specified is of type "card" or "array".
  #   destinationCardPath {array?} this is the array of keys that determines where in the data object the card will be
  #       moved to. This is similar to cardPath. This is only used by the move_card operation if the dataType is "card".
  #   propertyPath {array?} this is an array of keys that determines where in the data object the property key is.
  #       (e.g., if propertyPath is ['a', 'b', 'c'], and the property is "d", then the property is represented by
  #       data["a"]["b"]["c"]["d"]). Only used if the dataType specified is of type "property".
  #   property {string} the key of the property to modify. This is only used by the "incrementProperty",
  #       "decrementProperty", and "invertProperty" mutation types.
  # }>} the mutations to perform on the game data.
  def mutate_game(self, game_id, mutations):
    cur = self._card_games_database.get_cursor()

    try:
      game_row = self._card_games_database.get_game(cur, game_id)
      game_data = game_row["data"]
      for mutation in mutations:
        source_array = None
        card = None
        property_path = None
        if mutation["dataType"] in ["array", "card"]:
          source_array = CardGames._get_property(
              game_data, mutation["cardPath"])

        if mutation["dataType"] == "card":
          for cur_card in source_array:
            if cur_card["gameCardId"] == mutation["gameCardId"]:
              card = cur_card
              break
          if card is None:
            continue
          property_path = card
        elif mutation["dataType"] == "property":
          property_path = CardGames._get_property(
              game_data, mutation["propertyPath"])

        if mutation["type"] == "moveCard":
          destination_array = CardGames._get_property(
              game_data, mutation["destinationCardPath"])
          source_array.remove(card)
          destination_array.append(card)
        elif mutation["type"] == "incrementProperty":
          property_path[mutation["property"]] += 1
        elif mutation["type"] == "decrementProperty":
          property_path[mutation["property"]] -= 1
        elif mutation["type"] == "invertProperty":
          property_path[mutation["property"]
                        ] = not property_path[mutation["property"]]
        elif mutation["type"] == "shuffleCards":
          CardGames._shuffle(source_array, mutation["shuffleIndices"])
        else:
          raise Exception("Unknown mutation type.")
      self._card_games_database.update_game(cur, game_id, game_data)

      self._card_games_database.commit()

    except psycopg2.Error:
      self._card_games_database.rollback()
      cur.close()
      raise
    return game_data

  # Given an object and an array of nested keys, gets the property referenced.
  # obj {Object} the object to search in
  # keys {array<string|number|anything>} the keys used to retrieve the property. (e.g. if keys is [1,'a', 2])
  # the property retrieved is obj[1]['a'][2].
  @staticmethod
  def _get_property(obj, keys):
    ret = obj
    for key in keys:
      ret = ret[key]
    return ret

  # Shuffles the given array using the indices as parameters. Essentially provides a seeded shuffle. Used to match the javascript.
  # arr {array<Card>} the array of cards to shuffle.
  # shuffleIndices {array<number>} the array of random numbers used to power the shuffle algorithm.
  @staticmethod
  def _shuffle(arr, shuffleIndices):
    currentIndex = len(arr)
    temporaryValue = None

    for shuffleIndex in shuffleIndices:
      currentIndex -= 1

      temporaryValue = arr[currentIndex]
      arr[currentIndex] = arr[shuffleIndex]
      arr[shuffleIndex] = temporaryValue
    return arr
