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
      self._card_games_database.delete_game(cur, player1, player2)
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
  #   Required:
  #   type {string} Required. the type of mutation to perform. Possible values are:
  #       increment: Increment a value. Supports data type.
  #       decrement: Decrement a value. Supports any data type.
  #       invert: Inverts a boolean value. Supports any data type.
  #       set: Sets a value. Works on any data type.
  #       moveCard: Moves a card to the destinationCardPath. Requires datatype = card
  #       shuffle: Shuffles the array specified. Requires datatype = property
  #       append: appends "value" to to the array. Requires datatype = property
  #   dataType {string} Required. the type of data to act on. Possible values are:
  #       card: Acts on a card object. Finds the card object in the game to act on.
  #           Requires gameCardId
  #       property: The a set property in the object to act on.
  #
  #   IFF datatype=card:
  #   gameCardId {number} the id of the card to perform the mutation on.
  #   cardPath {array} Required. this is an array of keys that determines where in the data object the object containing
  #       the card is.
  #
  #   IFF type=moveCard:
  #   destinationCardPath {array}: The array to move the card to.
  #
  #   IFF type in [increment, decrement, invert, set, shuffle, append]
  #   propertyPath {array} this is an array of keys that determines where in the data object the object containing
  #       the property is. For shuffle and append, this specifies the array to be modified.
  #       For type 'card', it begins at the card.
  #       For type property, it begins on the game object.
  #       (e.g., if subPath is ['a', 'b', 'c'], and the property is "d", then the property is represented by
  #       data["a"]["b"]["c"]["d"]).
  #
  #   IFF type in [increment, decrement, invert, set]
  #   property {string} the key of the property to modify.
  #
  #   IFF type in [set, append]
  #   value {anything} The value to set the property to or the value to append.
  #
  #   IFF type = shuffle
  #   shuffleIndices {array[number]} the list of numbers used by the algorithm to shuffle the array
  #
  # }>} the mutations to perform on the game data.
  def mutate_game(self, game_id, mutations):
    cur = self._card_games_database.get_cursor()

    try:
      game_row = self._card_games_database.get_game(cur, game_id)
      game_data = game_row["data"]
      for mutation in mutations:
        card_array = None
        card = None
        property_array = None

        if mutation["dataType"] == "card":
          card_array = CardGames._fetch_from_path(
              game_data, mutation["cardPath"])
          for cur_card in card_array:
            if cur_card["gameCardId"] == mutation["gameCardId"]:
              card = cur_card
              break
          if card is None:
            continue

        if mutation["type"] in ["increment", "decrement", "invert", "set", "shuffle", "append"]:
          starting_object = game_data
          if mutation["dataType"] == "card":
            starting_object = card
          property_array = CardGames._fetch_from_path(
              starting_object, mutation["propertyPath"])
        if mutation["type"] == "moveCard":
          destination_array = CardGames._fetch_from_path(
              game_data, mutation["destinationCardPath"])
          card_array.remove(card)
          destination_array.append(card)
        elif mutation["type"] == "increment":
          property_array[mutation["property"]] += 1
        elif mutation["type"] == "decrement":
          property_array[mutation["property"]] -= 1
        elif mutation["type"] == "invert":
          property_array[mutation["property"]
                         ] = not property_array[mutation["property"]]
        elif mutation["type"] == "set":
          property_array[mutation["property"]] = mutation["value"]
        elif mutation["type"] == "shuffle":
          CardGames._shuffle(property_array, mutation["shuffleIndices"])
        elif mutation["type"] == "append":
          property_array.append(mutation["value"])
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
  def _fetch_from_path(obj, keys):
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
